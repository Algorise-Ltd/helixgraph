"""Procurement CSV Loader - loads procurement CSV data into Neo4j.

This loader reads procurement data from CSV files provided by HEL-19 (mertalpaydin):
- suppliers.csv (240 records)
- products.csv (120 records)  
- purchase_orders.csv (1,452 records)
- invoices.csv (674 records)
- risks.csv (960 records)

Total: 3,446 records
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional

from etl.base_loader import BaseLoader
from etl.utils import setup_file_logger, get_project_root


class ProcurementCSVLoader(BaseLoader):
    """Domain loader for procurement CSV data: suppliers, products, POs, invoices, risks."""

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
        batch_size: int = 500,
        data_dir: Optional[str] = None,
        log_file: Optional[str] = None,
    ):
        if log_file is None:
            log_file = str(get_project_root() / "logs" / "procurement_csv_load.log")
        logger = setup_file_logger("ProcurementCSVLoader", log_file)

        super().__init__(uri, user, password, database, batch_size, logger)

        if data_dir is None:
            data_dir = str(get_project_root() / "data" / "procurement_csv")
        self.data_dir = Path(data_dir)
        
        # Data storage
        self.suppliers: List[Dict] = []
        self.products: List[Dict] = []
        self.purchase_orders: List[Dict] = []
        self.invoices: List[Dict] = []
        self.risks: List[Dict] = []

    def setup_schema(self):
        """Create constraints and indexes for procurement data."""
        self.logger.info("Setting up procurement CSV schema constraints and indexes")

        constraints = [
            """CREATE CONSTRAINT procurement_supplier_vendor_code_unique IF NOT EXISTS
               FOR (s:Supplier) REQUIRE s.vendorCode IS UNIQUE""",
            """CREATE CONSTRAINT procurement_product_sku_unique IF NOT EXISTS
               FOR (p:Product) REQUIRE p.sku IS UNIQUE""",
            """CREATE CONSTRAINT procurement_purchase_order_number_unique IF NOT EXISTS
               FOR (po:PurchaseOrder) REQUIRE po.orderNumber IS UNIQUE""",
            """CREATE CONSTRAINT procurement_invoice_number_unique IF NOT EXISTS
               FOR (inv:Invoice) REQUIRE inv.invoiceNumber IS UNIQUE""",
            """CREATE CONSTRAINT procurement_risk_id_unique IF NOT EXISTS
               FOR (r:SupplierRisk) REQUIRE r.riskId IS UNIQUE""",
        ]
        for constraint in constraints:
            self.create_constraint(constraint)

        indexes = [
            """CREATE INDEX procurement_supplier_country IF NOT EXISTS
               FOR (s:Supplier) ON (s.country)""",
            """CREATE INDEX procurement_product_category IF NOT EXISTS
               FOR (p:Product) ON (p.category_L1)""",
            """CREATE INDEX procurement_po_status IF NOT EXISTS
               FOR (po:PurchaseOrder) ON (po.orderStatus)""",
            """CREATE INDEX procurement_invoice_status IF NOT EXISTS
               FOR (inv:Invoice) ON (inv.paymentStatus)""",
            """CREATE INDEX procurement_risk_type IF NOT EXISTS
               FOR (r:SupplierRisk) ON (r.riskType)""",
        ]
        for index in indexes:
            self.create_index(index)

    def load_csv_file(self, filename: str) -> List[Dict]:
        """Load a CSV file and return list of dictionaries."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        data = []
        with filepath.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        self.logger.info(f"Loaded {len(data)} records from {filename}")
        return data

    def load_data(self):
        """Load all CSV files."""
        self.logger.info(f"Loading procurement CSV data from {self.data_dir}")
        
        self.suppliers = self.load_csv_file("suppliers.csv")
        self.products = self.load_csv_file("products.csv")
        self.purchase_orders = self.load_csv_file("purchase_orders.csv")
        self.invoices = self.load_csv_file("invoices.csv")
        self.risks = self.load_csv_file("risks.csv")
        
        self.logger.info(
            "Loaded procurement data: %d suppliers, %d products, %d POs, %d invoices, %d risks",
            len(self.suppliers),
            len(self.products),
            len(self.purchase_orders),
            len(self.invoices),
            len(self.risks),
        )

    def load_suppliers(self):
        """Load supplier nodes."""
        cypher = """
            UNWIND $batch AS supplier
            MERGE (s:Supplier {vendorCode: supplier.vendorCode})
            SET s.legalName = supplier.legalName,
                s.address = supplier.address,
                s.country = supplier.country,
                s.contactPerson = supplier.contactPerson,
                s.isActive = supplier.isActive = 'True',
                s.financialHealth = supplier.financialHealth,
                s.riskScore = toFloat(supplier.riskScore),
                s.created_at = datetime()
        """
        count = self.batch_load(self.suppliers, cypher, batch_size=500)
        self.stats.add_nodes("Supplier", count)

    def load_products(self):
        """Load product nodes with category hierarchy."""
        cypher = """
            UNWIND $batch AS product
            MERGE (p:Product {sku: product.sku})
            SET p.name = product.name,
                p.description = product.description,
                p.unitOfMeasure = product.unitOfMeasure,
                p.isCritical = product.isCritical = 'True',
                p.category_L1 = product.category_L1,
                p.category_L2 = product.category_L2,
                p.category_L3 = product.category_L3,
                p.category_L4 = product.category_L4,
                p.created_at = datetime()
            
            // Create category nodes and relationships
            WITH p, product
            WHERE product.category_L1 IS NOT NULL AND product.category_L1 <> ''
            MERGE (c1:ProductCategory {name: product.category_L1, level: 1})
            MERGE (p)-[:IN_CATEGORY]->(c1)
            
            WITH p, product, c1
            WHERE product.category_L2 IS NOT NULL AND product.category_L2 <> ''
            MERGE (c2:ProductCategory {name: product.category_L2, level: 2})
            MERGE (p)-[:IN_CATEGORY]->(c2)
            MERGE (c2)-[:PARENT_CATEGORY]->(c1)
            
            WITH p, product, c2
            WHERE product.category_L3 IS NOT NULL AND product.category_L3 <> ''
            MERGE (c3:ProductCategory {name: product.category_L3, level: 3})
            MERGE (p)-[:IN_CATEGORY]->(c3)
            MERGE (c3)-[:PARENT_CATEGORY]->(c2)
            
            WITH p, product, c3
            WHERE product.category_L4 IS NOT NULL AND product.category_L4 <> ''
            MERGE (c4:ProductCategory {name: product.category_L4, level: 4})
            MERGE (p)-[:IN_CATEGORY]->(c4)
            MERGE (c4)-[:PARENT_CATEGORY]->(c3)
        """
        count = self.batch_load(self.products, cypher, batch_size=200)
        self.stats.add_nodes("Product", count)

    def load_purchase_orders(self):
        """Load purchase orders and connect to suppliers and products."""
        cypher = """
            UNWIND $batch AS po
            MERGE (p:PurchaseOrder {orderNumber: po.orderNumber})
            SET p.item = po.item,
                p.dateIssued = datetime(replace(po.dateIssued, ' ', 'T')),
                p.dateChanged = datetime(replace(po.dateChanged, ' ', 'T')),
                p.orderStatus = po.orderStatus,
                p.orderTotalValue = toFloat(po.orderTotalValue),
                p.approvedBy = po.approvedBy,
                p.quantity = toFloat(po.quantity),
                p.unitPrice = toFloat(po.unitPrice),
                p.deliveryDate = datetime(replace(po.deliveryDate, ' ', 'T')),
                p.still_to_be_delivered_qty = toFloat(po.still_to_be_delivered_qty),
                p.still_to_be_delivered_value = toFloat(po.still_to_be_delivered_value),
                p.still_to_be_invoiced_qty = toFloat(po.still_to_be_invoiced_qty),
                p.still_to_be_invoiced_value = toFloat(po.still_to_be_invoiced_value),
                p.contractReference = po.contractReference,
                p.paymentTerms = po.paymentTerms,
                p.requisitioner = po.requisitioner,
                p.costCenter = po.costCenter,
                p.created_at = datetime()
            
            WITH p, po
            MATCH (s:Supplier {vendorCode: po.supplierVendorCode})
            MERGE (p)-[r:FROM_SUPPLIER]->(s)
            SET r.created_at = datetime()
            
            WITH p, po
            MATCH (prod:Product {sku: po.productSku})
            MERGE (p)-[r2:FOR_PRODUCT]->(prod)
            SET r2.created_at = datetime()
        """
        count = self.batch_load(self.purchase_orders, cypher, batch_size=500)
        self.stats.add_nodes("PurchaseOrder", count)
        self.stats.add_relationships("FROM_SUPPLIER", count)
        self.stats.add_relationships("FOR_PRODUCT", count)

    def load_invoices(self):
        """Load invoices and connect to purchase orders."""
        cypher = """
            UNWIND $batch AS inv
            MERGE (i:Invoice {invoiceNumber: inv.invoiceNumber})
            SET i.supplierReference = inv.supplierReference,
                i.dateCreated = datetime(replace(inv.dateCreated, ' ', 'T')),
                i.paymentDueDate = datetime(replace(inv.paymentDueDate, ' ', 'T')),
                i.totalPaymentDue = toFloat(inv.totalPaymentDue),
                i.paymentStatus = inv.paymentStatus,
                i.late_payment_flag = inv.late_payment_flag = 'True',
                i.glAccount = inv.glAccount,
                i.costCenter = inv.costCenter,
                i.invoiceText = inv.invoiceText,
                i.postingDate = datetime(replace(inv.postingDate, ' ', 'T')),
                i.created_at = datetime()
            
            WITH i, inv
            MATCH (po:PurchaseOrder {orderNumber: inv.poOrderNumber})
            MERGE (i)-[r:FOR_PURCHASE_ORDER]->(po)
            SET r.created_at = datetime()
        """
        count = self.batch_load(self.invoices, cypher, batch_size=500)
        self.stats.add_nodes("Invoice", count)
        self.stats.add_relationships("FOR_PURCHASE_ORDER", count)

    def load_risks(self):
        """Load supplier risk assessments."""
        cypher = """
            UNWIND $batch AS risk
            MERGE (r:SupplierRisk {riskId: risk.riskId})
            SET r.riskType = risk.riskType,
                r.riskScore = toFloat(risk.riskScore),
                r.riskDescription = risk.riskDescription,
                r.mitigationPlan = risk.mitigationPlan,
                r.riskStatus = risk.riskStatus,
                r.created_at = datetime()
            
            WITH r, risk
            MATCH (s:Supplier {vendorCode: risk.supplierVendorCode})
            MERGE (r)-[rel:ASSESSES]->(s)
            SET rel.created_at = datetime()
        """
        count = self.batch_load(self.risks, cypher, batch_size=500)
        self.stats.add_nodes("SupplierRisk", count)
        self.stats.add_relationships("ASSESSES", count)

    def load(self):
        """Execute the full procurement CSV data load."""
        self.logger.info("Starting procurement CSV data load")
        try:
            self.load_data()
            self.setup_schema()
            self.load_suppliers()
            self.load_products()
            self.load_purchase_orders()
            self.load_invoices()
            self.load_risks()
            self.print_statistics()
            graph_stats = self.get_graph_statistics()
            self.logger.info(
                "Procurement CSV graph totals: %d nodes, %d relationships",
                graph_stats["total_nodes"],
                graph_stats["total_relationships"],
            )
        except Exception as exc:  # pragma: no cover
            self.logger.error("Procurement CSV load failed: %s", exc, exc_info=True)
            raise


def main():
    from etl.utils import get_neo4j_config

    config = get_neo4j_config()
    with ProcurementCSVLoader(
        uri=config["uri"],
        user=config["user"],
        password=config["password"],
    ) as loader:
        if not loader.test_connection():
            raise RuntimeError("Failed to connect to Neo4j")
        loader.load()


if __name__ == "__main__":
    main()

