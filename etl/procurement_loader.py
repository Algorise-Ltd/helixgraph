"""Procurement Loader - loads procurement data into Neo4j."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from etl.base_loader import BaseLoader
from etl.utils import setup_file_logger, get_project_root
from schemas.procurement_schema import ProcurementDataset


class ProcurementLoader(BaseLoader):
    """Domain loader for suppliers, contracts, risks, and purchase orders."""

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
        batch_size: int = 500,
        data_file: Optional[str] = None,
        log_file: Optional[str] = None,
    ):
        if log_file is None:
            log_file = str(get_project_root() / "logs" / "procurement_load.log")
        logger = setup_file_logger("ProcurementLoader", log_file)

        super().__init__(uri, user, password, database, batch_size, logger)

        if data_file is None:
            data_file = str(get_project_root() / "data" / "procurement" / "procurement_data.json")
        self.data_file = Path(data_file)
        self.dataset: Optional[ProcurementDataset] = None

    def setup_schema(self):
        self.logger.info("Setting up procurement schema constraints and indexes")

        constraints = [
            """CREATE CONSTRAINT procurement_supplier_id_unique IF NOT EXISTS
               FOR (s:Supplier) REQUIRE s.supplier_id IS UNIQUE""",
            """CREATE CONSTRAINT procurement_contract_id_unique IF NOT EXISTS
               FOR (c:Contract) REQUIRE c.contract_id IS UNIQUE""",
            """CREATE CONSTRAINT procurement_purchase_order_id_unique IF NOT EXISTS
               FOR (po:PurchaseOrder) REQUIRE po.po_id IS UNIQUE""",
            """CREATE CONSTRAINT procurement_po_line_id_unique IF NOT EXISTS
               FOR (line:PurchaseOrderLine) REQUIRE line.line_id IS UNIQUE""",
        ]
        for constraint in constraints:
            self.create_constraint(constraint)

        indexes = [
            """CREATE INDEX procurement_supplier_name IF NOT EXISTS
               FOR (s:Supplier) ON (s.name)""",
            """CREATE INDEX procurement_supplier_country IF NOT EXISTS
               FOR (s:Supplier) ON (s.country)""",
            """CREATE INDEX procurement_contract_category IF NOT EXISTS
               FOR (c:Contract) ON (c.category)""",
            """CREATE INDEX procurement_po_status IF NOT EXISTS
               FOR (po:PurchaseOrder) ON (po.status)""",
        ]
        for index in indexes:
            self.create_index(index)

    def load_data(self):
        self.logger.info(f"Loading procurement dataset from {self.data_file}")
        if not self.data_file.exists():
            raise FileNotFoundError(f"Procurement data file not found: {self.data_file}")

        with self.data_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self.dataset = ProcurementDataset(**raw)
        self.logger.info(
            "Loaded procurement dataset: %d suppliers, %d contracts",
            len(self.dataset.suppliers),
            len(self.dataset.contracts),
        )

    def load_suppliers(self):
        assert self.dataset is not None
        data = [supplier.model_dump(mode="json") for supplier in self.dataset.suppliers]

        cypher = """
            UNWIND $batch AS supplier
            MERGE (s:Supplier {supplier_id: supplier.supplier_id})
            SET s.name = supplier.name,
                s.country = supplier.country,
                s.industry = supplier.industry,
                s.tier = supplier.tier,
                s.onboarding_date = date(supplier.onboarding_date),
                s.created_at = datetime()
        """
        count = self.batch_load(data, cypher, batch_size=500)
        self.stats.add_nodes("Supplier", count)

    def load_contracts(self):
        assert self.dataset is not None
        data = [contract.model_dump(mode="json") for contract in self.dataset.contracts]

        cypher = """
            UNWIND $batch AS contract
            MATCH (s:Supplier {supplier_id: contract.supplier_id})
            MERGE (c:Contract {contract_id: contract.contract_id})
            SET c.category = contract.category,
                c.start_date = date(contract.start_date),
                c.end_date = CASE contract.end_date WHEN NULL THEN NULL ELSE date(contract.end_date) END,
                c.value = contract.value,
                c.currency = contract.currency,
                c.created_at = datetime()
            MERGE (s)-[r:HAS_CONTRACT]->(c)
            SET r.created_at = datetime(),
                r.source = "procurement_data"
        """
        count = self.batch_load(data, cypher, batch_size=500)
        self.stats.add_nodes("Contract", count)
        self.stats.add_relationships("HAS_CONTRACT", count)

    def load_risk_scores(self):
        assert self.dataset is not None
        data = [risk.model_dump(mode="json") for risk in self.dataset.risk_scores]

        cypher = """
            UNWIND $batch AS risk
            MATCH (s:Supplier {supplier_id: risk.supplier_id})
            MERGE (score:SupplierRisk {supplier_id: risk.supplier_id, category: risk.category, assessed_date: risk.assessed_date})
            SET score.score = risk.score,
                score.notes = risk.notes,
                score.created_at = datetime()
            MERGE (s)-[r:HAS_RISK]->(score)
            SET r.created_at = datetime()
        """
        count = self.batch_load(data, cypher, batch_size=500)
        self.stats.add_nodes("SupplierRisk", count)
        self.stats.add_relationships("HAS_RISK", count)

    def load_purchase_orders(self):
        assert self.dataset is not None

        order_records: List[Dict[str, Any]] = []
        line_records: List[Dict[str, Any]] = []

        for po in self.dataset.purchase_orders:
            order_records.append(
                {
                    "po_id": po.po_id,
                    "supplier_id": po.supplier_id,
                    "issue_date": po.issue_date,
                    "expected_delivery_date": po.expected_delivery_date,
                    "status": po.status,
                }
            )
            for line in po.lines:
                line_records.append(
                    {
                        "line_id": line.line_id,
                        "po_id": po.po_id,
                        "contract_id": line.contract_id,
                        "product_category": line.product_category,
                        "quantity": line.quantity,
                        "unit_price": line.unit_price,
                        "currency": line.currency,
                    }
                )

        cypher_po = """
            UNWIND $batch AS po
            MATCH (s:Supplier {supplier_id: po.supplier_id})
            MERGE (p:PurchaseOrder {po_id: po.po_id})
            SET p.issue_date = date(po.issue_date),
                p.expected_delivery_date = date(po.expected_delivery_date),
                p.status = po.status,
                p.created_at = datetime()
            MERGE (s)-[r:PLACED_ORDER]->(p)
            SET r.created_at = datetime()
        """
        order_count = self.batch_load(order_records, cypher_po, batch_size=500)
        self.stats.add_nodes("PurchaseOrder", order_count)
        self.stats.add_relationships("PLACED_ORDER", order_count)

        cypher_line = """
            UNWIND $batch AS line
            MATCH (po:PurchaseOrder {po_id: line.po_id})
            MATCH (c:Contract {contract_id: line.contract_id})
            MERGE (l:PurchaseOrderLine {line_id: line.line_id})
            SET l.product_category = line.product_category,
                l.quantity = line.quantity,
                l.unit_price = line.unit_price,
                l.currency = line.currency,
                l.created_at = datetime()
            MERGE (po)-[r:HAS_LINE]->(l)
            SET r.created_at = datetime()
            MERGE (l)-[r2:FULFILLED_BY]->(c)
            SET r2.created_at = datetime()
        """
        line_count = self.batch_load(line_records, cypher_line, batch_size=1000)
        self.stats.add_nodes("PurchaseOrderLine", line_count)
        self.stats.add_relationships("HAS_LINE", line_count)
        self.stats.add_relationships("FULFILLED_BY", line_count)

    def load(self):
        self.logger.info("Starting procurement data load")
        try:
            self.load_data()
            self.setup_schema()
            self.load_suppliers()
            self.load_contracts()
            self.load_risk_scores()
            self.load_purchase_orders()
            self.print_statistics()
            graph_stats = self.get_graph_statistics()
            self.logger.info(
                "Procurement graph totals: %d nodes, %d relationships",
                graph_stats["total_nodes"],
                graph_stats["total_relationships"],
            )
        except Exception as exc:  # pragma: no cover
            self.logger.error("Procurement load failed: %s", exc, exc_info=True)
            raise


def main():
    from etl.utils import get_neo4j_config

    config = get_neo4j_config()
    with ProcurementLoader(
        uri=config["uri"],
        user=config["user"],
        password=config["password"],
    ) as loader:
        if not loader.test_connection():
            raise RuntimeError("Failed to connect to Neo4j")
        loader.load()


if __name__ == "__main__":
    main()
