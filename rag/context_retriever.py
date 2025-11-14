import os
from neo4j import GraphDatabase
from rag.config import get_config

class GraphContextRetriever:
    """
    Retrieves context from the Neo4j graph database for RAG operations.
    """
    def __init__(self):
        self.config = get_config()
        self.driver = GraphDatabase.driver(
            self.config.neo4j_uri,
            auth=(self.config.neo4j_user, self.config.neo4j_password)
        )
        self.database = self.config.neo4j_database

    def close(self):
        """Closes the Neo4j driver connection."""
        self.driver.close()

    def _run_query(self, query, params=None):
        """Helper to run a Cypher query."""
        with self.driver.session(database=self.database) as session:
            result = session.run(query, params if params else {})
            return [record for record in result]

    def get_supplier_context(self, supplier_id: str) -> str:
        """
        Retrieves comprehensive context for a given supplier.
        Includes basic info, procurement metrics, campaign relationships,
        risk indicators, and active contracts.
        """
        query = """
        MATCH (s:Supplier {id: $supplier_id})
        OPTIONAL MATCH (s)-[r_po:HAS_PO]->(po:PurchaseOrder)
        OPTIONAL MATCH (po)-[r_inv:HAS_INVOICE]->(inv:Invoice)
        OPTIONAL MATCH (po)-[r_camp:LINKED_TO_CAMPAIGN]->(c:Campaign)
        OPTIONAL MATCH (s)-[r_risk:HAS_RISK]->(risk:Risk)
        OPTIONAL MATCH (s)-[r_contract:HAS_CONTRACT]->(contract:Contract)
        RETURN
            s.name AS supplierName,
            s.category AS supplierCategory,
            s.risk_score AS supplierRiskScore,
            s.country AS supplierCountry,
            s.payment_terms AS supplierPaymentTerms,
            s.last_annual_revenue AS supplierLastAnnualRevenue,
            COUNT(DISTINCT po) AS totalPOs,
            SUM(po.amount) AS totalSpend,
            AVG(po.amount) AS averagePOSize,
            COUNT(DISTINCT CASE WHEN inv.status = 'late' THEN inv END) AS latePayments,
            COLLECT(DISTINCT c.name) AS linkedCampaigns,
            COLLECT(DISTINCT risk.type) AS riskTypes,
            COLLECT(DISTINCT contract.id) AS activeContracts
        """
        params = {"supplier_id": supplier_id}
        result = self._run_query(query, params)

        if not result or not result[0]['supplierName']:
            return f"No context found for supplier ID: {supplier_id}"

        record = result[0]
        context = f"Supplier: {record['supplierName']}\n" \
                  f"Category: {record['supplierCategory']}\n" \
                  f"Risk Score: {record['supplierRiskScore']} (Risk Level: {self._get_risk_level(record['supplierRiskScore'])})\n" \
                  f"Country: {record['supplierCountry']}\n" \
                  f"Payment Terms: {record['supplierPaymentTerms']}\n" \
                  f"Last Annual Revenue: ${record['supplierLastAnnualRevenue']:,}\n" \
                  f"Procurement Metrics:\n" \
                  f"  Total POs: {record['totalPOs']}\n" \
                  f"  Total Spend: ${record['totalSpend']:,}\n" \
                  f"  Average PO Size: ${record['averagePOSize']:,}\n" \
                  f"Risk Indicators:\n" \
                  f"  Late Payments: {record['latePayments']}\n" \
                  f"  Risk Types: {', '.join(record['riskTypes']) if record['riskTypes'] else 'None'}\n" \
                  f"Active Campaigns: {', '.join(record['linkedCampaigns']) if record['linkedCampaigns'] else 'None'}\n" \
                  f"Active Contracts: {', '.join(record['activeContracts']) if record['activeContracts'] else 'None'}\n" \
                  f"Recent Activity: (Not implemented yet, needs date logic)" # Placeholder

        return context

    def get_campaign_context(self, campaign_id: str) -> str:
        """
        Retrieves comprehensive context for a given marketing campaign.
        Includes basic info, linked POs, total spend, and associated suppliers.
        """
        query = """
        MATCH (c:Campaign {id: $campaign_id})
        OPTIONAL MATCH (c)<-[r_camp:LINKED_TO_CAMPAIGN]-(po:PurchaseOrder)
        OPTIONAL MATCH (po)-[r_supp:HAS_SUPPLIER]->(s:Supplier)
        RETURN
            c.name AS campaignName,
            c.budget AS campaignBudget,
            c.start_date AS campaignStartDate,
            c.end_date AS campaignEndDate,
            c.channel AS campaignChannel,
            c.kpis AS campaignKPIs,
            COUNT(DISTINCT po) AS totalLinkedPOs,
            SUM(po.amount) AS totalSpendOnCampaign,
            COLLECT(DISTINCT s.name) AS associatedSuppliers
        """
        params = {"campaign_id": campaign_id}
        result = self._run_query(query, params)

        if not result or not result[0]['campaignName']:
            return f"No context found for campaign ID: {campaign_id}"

        record = result[0]
        context = f"Campaign: {record['campaignName']}\n" \
                  f"Budget: ${record['campaignBudget']:,}\n" \
                  f"Dates: {record['campaignStartDate']} to {record['campaignEndDate']}\n" \
                  f"Channel: {record['campaignChannel']}\n" \
                  f"KPIs: {record['campaignKPIs']}\n" \
                  f"Procurement Linkages:\n" \
                  f"  Total Linked POs: {record['totalLinkedPOs']}\n" \
                  f"  Total Spend on Campaign: ${record['totalSpendOnCampaign']:,}\n" \
                  f"  Associated Suppliers: {', '.join(record['associatedSuppliers']) if record['associatedSuppliers'] else 'None'}\n"

        return context

    def get_product_context(self, product_sku: str) -> str:
        """
        Retrieves comprehensive context for a given product SKU.
        Includes basic info, associated POs, total spend, and suppliers.
        """
        query = """
        MATCH (p:Product {sku: $product_sku})
        OPTIONAL MATCH (p)<-[r_prod:HAS_PRODUCT]-(po:PurchaseOrder)
        OPTIONAL MATCH (po)-[r_supp:HAS_SUPPLIER]->(s:Supplier)
        RETURN
            p.name AS productName,
            p.description AS productDescription,
            p.category AS productCategory,
            p.unit_of_measure AS productUnitOfMeasure,
            p.is_critical AS productIsCritical,
            COUNT(DISTINCT po) AS totalPOsForProduct,
            SUM(po.amount) AS totalSpendOnProduct,
            COLLECT(DISTINCT s.name) AS suppliersOfProduct
        """
        params = {"product_sku": product_sku}
        result = self._run_query(query, params)

        if not result or not result[0]['productName']:
            return f"No context found for product SKU: {product_sku}"

        record = result[0]
        context = f"Product: {record['productName']} (SKU: {product_sku})\n" \
                  f"Description: {record['productDescription']}\n" \
                  f"Category: {record['productCategory']}\n" \
                  f"Unit of Measure: {record['productUnitOfMeasure']}\n" \
                  f"Is Critical: {'Yes' if record['productIsCritical'] else 'No'}\n" \
                  f"Procurement Metrics:\n" \
                  f"  Total POs for Product: {record['totalPOsForProduct']}\n" \
                  f"  Total Spend on Product: ${record['totalSpendOnProduct']:,}\n" \
                  f"  Suppliers: {', '.join(record['suppliersOfProduct']) if record['suppliersOfProduct'] else 'None'}\n"

        return context

    def _get_risk_level(self, score: int) -> str:
        """Helper to determine risk level from score."""
        if score <= 30:
            return "Low"
        elif score <= 70:
            return "Medium"
        else:
            return "High"

if __name__ == '__main__':
    # Example Usage (requires Neo4j to be running and populated with data)
    retriever = GraphContextRetriever()

    # Test Supplier Context
    print("--- Testing Supplier Context ---")
    supplier_id = "SUP-001" # Replace with an actual supplier ID from your data
    supplier_context = retriever.get_supplier_context(supplier_id)
    print(supplier_context)

    # Test Campaign Context
    print("\n--- Testing Campaign Context ---")
    campaign_id = "CAMP_2024_Q1" # Replace with an actual campaign ID from your data
    campaign_context = retriever.get_campaign_context(campaign_id)
    print(campaign_context)

    # Test Product Context
    print("\n--- Testing Product Context ---")
    product_sku = "PROD-001" # Replace with an actual product SKU from your data
    product_context = retriever.get_product_context(product_sku)
    print(product_context)

    retriever.close()