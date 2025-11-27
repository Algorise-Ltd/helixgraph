
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from neo4j import GraphDatabase
from rag.config import get_config

class GraphValidator:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters)
            return [record for record in result]

    def validate_graph(self):
        print("--- Starting Graph Validation ---")

        # 1. Count nodes for each label
        print("\n--- Node Counts ---")
        labels = ["Supplier", "PO", "Invoice", "Campaign", "Product"]
        for label in labels:
            query = f"MATCH (n:{label}) RETURN count(n) AS count"
            result = self.run_query(query)
            count = result[0]["count"]
            print(f"Number of {label} nodes: {count}")

        # 2. Count relationships for each type
        print("\n--- Relationship Counts ---")
        rel_types = ["BILLED_BY", "INVOICES", "FUNDED", "ORDERS"]
        for rel_type in rel_types:
            query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS count"
            result = self.run_query(query)
            count = result[0]["count"]
            print(f"Number of {rel_type} relationships: {count}")

        # 3. Check for dangling relationships
        print("\n--- Dangling Relationship Checks ---")
        
        # POs without Suppliers
        query = "MATCH (p:PO) WHERE NOT (p)-[:BILLED_BY]->(:Supplier) RETURN count(p) AS count"
        result = self.run_query(query)
        count = result[0]["count"]
        print(f"POs without a Supplier: {count}")
        
        # Invoices without POs
        query = "MATCH (i:Invoice) WHERE NOT (i)-[:INVOICES]->(:PO) RETURN count(i) AS count"
        result = self.run_query(query)
        count = result[0]["count"]
        print(f"Invoices without a PO: {count}")

        # Funded POs without Campaigns
        query = "MATCH (p:PO) WHERE (p)<-[:FUNDED]-() AND NOT (p)<-[:FUNDED]-(:Campaign) RETURN count(p) AS count"
        result = self.run_query(query)
        count = result[0]["count"]
        print(f"Funded POs without a Campaign: {count}")

        print("\n--- Graph Validation Complete ---")

def main():
    config = get_config()
    validator = GraphValidator(config.neo4j_uri, config.neo4j_user, config.neo4j_password, config.neo4j_database)
    validator.validate_graph()
    validator.close()

if __name__ == "__main__":
    main()
