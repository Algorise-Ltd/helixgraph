
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from neo4j import GraphDatabase
from rag.config import get_config

class Neo4jLoader:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters)
            return [record for record in result]

    def load_suppliers(self, file_path):
        df = pd.read_csv(file_path)
        df.rename(columns={
            'vendorCode': 'id',
            'legalName': 'name',
            'category_L1': 'category',
            'riskScore': 'risk_score',
            'paymentTerms': 'payment_terms',
            'lastAnnualRevenue': 'last_annual_revenue'
        }, inplace=True)
        for _, row in df.iterrows():
            self.run_query(
                "CREATE (s:Supplier {id: $id, name: $name, category: $category, risk_score: $risk_score, country: $country, payment_terms: $payment_terms, last_annual_revenue: $last_annual_revenue})",
                row.to_dict()
            )

    def load_pos(self, file_path):
        df = pd.read_csv(file_path)
        df.rename(columns={
            'orderNumber': 'id',
            'supplierVendorCode': 'supplier_id',
            'orderTotalValue': 'amount',
            'dateIssued': 'date',
            'orderStatus': 'status'
        }, inplace=True)
        df['campaign_id'] = df['description'].str.extract(r"Campaign ID: (\S+)")
        # Ensure productSku is present, handle NaNs
        if 'productSku' not in df.columns:
            df['productSku'] = None
        else:
            df['productSku'] = df['productSku'].where(pd.notnull(df['productSku']), None)

        for _, row in df.iterrows():
            self.run_query(
                "CREATE (p:PO {id: $id, supplier_id: $supplier_id, amount: $amount, date: $date, status: $status, category: $category, campaign_id: $campaign_id, description: $description, product_sku: $productSku, quantity: $quantity})",
                row.to_dict()
            )

    def load_products(self, file_path):
        df = pd.read_csv(file_path)
        # columns: sku, name, description, unitOfMeasure, isCritical, category_L1...
        for _, row in df.iterrows():
            self.run_query(
                "CREATE (p:Product {sku: $sku, name: $name, description: $description, unit_of_measure: $unitOfMeasure, is_critical: $isCritical, category: $category_L4})",
                row.to_dict()
            )

    def load_invoices(self, file_path):
        df = pd.read_csv(file_path)
        df.rename(columns={'invoiceNumber': 'id'}, inplace=True)
        for _, row in df.iterrows():
            self.run_query(
                "CREATE (i:Invoice {id: $id, po_id: $po_id, amount: $amount, issue_date: $issue_date, due_date: $due_date, paid_date: $paid_date, status: $status})",
                row.to_dict()
            )
            
    def load_campaigns(self, file_path):
        df = pd.read_csv(file_path)
        df.rename(columns={'campaign_id': 'id', 'campaign_name': 'name', ' budget ': 'budget'}, inplace=True)
        for _, row in df.iterrows():
            self.run_query(
                "CREATE (c:Campaign {id: $id, name: $name, budget: $budget, start_date: $start_date, end_date: $end_date, channel: $channel})",
                row.to_dict()
            )

    def load_campaign_po_links(self, file_path):
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            self.run_query(
                """
                MATCH (c:Campaign {id: $campaign_id})
                MATCH (p:PO {id: $po_id})
                CREATE (c)-[:FUNDED]->(p)
                """,
                row.to_dict()
            )

    def create_relationships(self):
        # POs to Suppliers
        self.run_query("""
        MATCH (p:PO), (s:Supplier)
        WHERE p.supplier_id = s.id
        CREATE (p)-[:BILLED_BY]->(s)
        """)
        
        # Invoices to POs
        self.run_query("""
        MATCH (i:Invoice), (p:PO)
        WHERE i.po_id = p.id
        CREATE (i)-[:INVOICES]->(p)
        """)

        # POs to Products
        self.run_query("""
        MATCH (p:PO), (prod:Product)
        WHERE p.product_sku = prod.sku
        CREATE (p)-[:ORDERS]->(prod)
        """)

    def clean_database(self):
        print("Cleaning database...")
        self.run_query("MATCH (n) DETACH DELETE n")

def main():
    config = get_config()
    loader = Neo4jLoader(config.neo4j_uri, config.neo4j_user, config.neo4j_password, config.neo4j_database)

    # Clean the database first to avoid duplicates
    loader.clean_database()

    data_path = "data/processed"
    
    print("Loading campaigns...")
    loader.load_campaigns(os.path.join(data_path, "marketing/campaigns_v1.csv"))
    
    print("Loading suppliers...")
    loader.load_suppliers(os.path.join(data_path, "procurement/suppliers.csv"))
    
    print("Loading products...")
    loader.load_products(os.path.join(data_path, "procurement/products.csv"))
    
    print("Loading POs...")
    loader.load_pos(os.path.join(data_path, "procurement/pos.csv"))
    
    print("Loading invoices...")
    loader.load_invoices(os.path.join(data_path, "procurement/invoices.csv"))
    
    print("Loading campaign PO links...")
    loader.load_campaign_po_links(os.path.join(data_path, "campaign_po_links.csv"))
    
    print("Creating relationships...")
    loader.create_relationships()
    
    print("Data loading complete.")
    loader.close()

if __name__ == "__main__":
    main()
