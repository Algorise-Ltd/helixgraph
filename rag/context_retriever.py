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

    def get_supplier_context(self, identifier: str) -> str:
        """
        Retrieves comprehensive context for a given supplier by ID or Name.
        Includes basic info, procurement metrics, campaign relationships,
        risk indicators, and active contracts.
        """
        query = """
        MATCH (s:Supplier)
        WHERE s.id = $identifier OR s.name = $identifier
        OPTIONAL MATCH (s)<-[:BILLED_BY]-(po:PO)
        OPTIONAL MATCH (po)<-[:INVOICES]-(inv:Invoice)
        OPTIONAL MATCH (po)<-[:FUNDED]-(c:Campaign)
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
            COLLECT(DISTINCT c.name) AS linkedCampaigns
        """
        params = {"identifier": identifier}
        result = self._run_query(query, params)

        if not result or not result[0]['supplierName']:
            return f"No context found for supplier: {identifier}"

        record = result[0]
        
        total_spend = record['totalSpend'] or 0
        avg_po_size = record['averagePOSize'] or 0
        risk_score = record['supplierRiskScore']
        risk_level = self._get_risk_level(risk_score) if risk_score is not None else "N/A"
        
        context = f"Supplier: {record['supplierName']}\n" \
                  f"Category: {record['supplierCategory']}\n" \
                  f"Risk Score: {risk_score} (Risk Level: {risk_level})\n" \
                  f"Country: {record['supplierCountry']}\n" \
                  f"Payment Terms: {record['supplierPaymentTerms']}\n" \
                  f"Last Annual Revenue: ${record['supplierLastAnnualRevenue']:,}\n" \
                  f"Procurement Metrics:\n" \
                  f"  Total POs: {record['totalPOs']}\n" \
                  f"  Total Spend: ${total_spend:,}\n" \
                  f"  Average PO Size: ${avg_po_size:,}\n" \
                  f"Risk Indicators:\n" \
                  f"  Late Payments: {record['latePayments']}\n" \
                  f"Active Campaigns: {', '.join(record['linkedCampaigns']) if record['linkedCampaigns'] else 'None'}\n"

        return context

    def get_campaign_context(self, identifier: str) -> str:
        """
        Retrieves comprehensive context for a given marketing campaign by ID or Name.
        Includes basic info, linked POs, total spend, and associated suppliers.
        """
        query = """
        MATCH (c:Campaign)
        WHERE c.id = $identifier OR c.name = $identifier
        OPTIONAL MATCH (c)-[:FUNDED]->(po:PO)
        OPTIONAL MATCH (po)-[:BILLED_BY]->(s:Supplier)
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
        params = {"identifier": identifier}
        result = self._run_query(query, params)

        if not result or not result[0]['campaignName']:
            return f"No context found for campaign: {identifier}"

        record = result[0]
        
        budget = record['campaignBudget'] or 0
        total_spend = record['totalSpendOnCampaign'] or 0
        
        context = f"Campaign: {record['campaignName']}\n" \
                  f"Budget: ${budget:,}\n" \
                  f"Dates: {record['campaignStartDate']} to {record['campaignEndDate']}\n" \
                  f"Channel: {record['campaignChannel']}\n" \
                  f"KPIs: {record['campaignKPIs']}\n" \
                  f"Procurement Linkages:\n" \
                  f"  Total Linked POs: {record['totalLinkedPOs']}\n" \
                  f"  Total Spend on Campaign: ${total_spend:,}\n" \
                  f"  Associated Suppliers: {', '.join(record['associatedSuppliers']) if record['associatedSuppliers'] else 'None'}\n"

        return context

    def get_product_context(self, identifier: str) -> str:
        """
        Retrieves comprehensive context for a given product by SKU or Name.
        Includes basic info, associated POs, total spend, and suppliers.
        """
        query = """
        MATCH (p:Product)
        WHERE p.sku = $identifier OR p.name = $identifier
        OPTIONAL MATCH (po:PO)-[:ORDERS]->(p)
        OPTIONAL MATCH (po)-[:BILLED_BY]->(s:Supplier)
        RETURN
            p.name AS productName,
            p.description AS productDescription,
            p.category AS productCategory,
            p.unit_of_measure AS unitOfMeasure,
            p.is_critical AS isCritical,
            COUNT(DISTINCT po) AS totalPOs,
            SUM(po.amount) AS totalSpend,
            AVG(po.amount) AS averagePrice,
            COLLECT(DISTINCT s.name) AS suppliers
        """
        params = {"identifier": identifier}
        result = self._run_query(query, params)

        if not result or not result[0]['productName']:
            return f"No context found for product: {identifier}"

        record = result[0]
        
        total_spend = record['totalSpend'] or 0
        avg_price = record['averagePrice'] or 0
        is_critical = "Yes" if record['isCritical'] else "No"
        
        context = f"Product: {record['productName']}\n" \
                  f"Description: {record['productDescription']}\n" \
                  f"Category: {record['productCategory']}\n" \
                  f"Unit of Measure: {record['unitOfMeasure']}\n" \
                  f"Critical Item: {is_critical}\n" \
                  f"Procurement Metrics:\n" \
                  f"  Total POs: {record['totalPOs']}\n" \
                  f"  Total Spend: ${total_spend:,}\n" \
                  f"  Average Order Value: ${avg_price:,}\n" \
                  f"Suppliers: {', '.join(record['suppliers']) if record['suppliers'] else 'None'}\n"

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