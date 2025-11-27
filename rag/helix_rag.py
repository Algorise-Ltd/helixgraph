import google.genai as genai
from google.genai import types
from jinja2 import Environment, FileSystemLoader
import os
import sys
from pathlib import Path

# Add project root to path to ensure nlp module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.config import get_config
from rag.context_retriever import GraphContextRetriever
from nlp.entity_extraction import get_canonical_entities

class HelixRAG:
    """
    HelixRAG class orchestrates the RAG process:
    1. Retrieves relevant context from the Neo4j graph using GraphContextRetriever.
    2. Generates a prompt using Jinja2 templates.
    3. Sends the prompt to the Gemini API to generate a natural language answer.
    """
    def __init__(self):
        self.config = get_config()
        self.client = genai.Client(api_key=self.config.gemini_api_key)
        self.context_retriever = GraphContextRetriever()

        # Setup Jinja2 environment for loading templates
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path))

    def _generate_answer(self, prompt: str) -> str:
        """
        Sends the generated prompt to the Gemini API and returns the answer.
        """
        try:
            cfg = types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_output_tokens,
                top_p=self.config.top_p,
                top_k=self.config.top_k
            )
            response = self.client.models.generate_content(
                model=self.config.gemini_model,
                contents=prompt,
                config=cfg
            )
            return response.text
        except Exception as e:
            raise e

    def ask(self, question: str, entity_type: str = None, entity_id: str = None) -> str:
        """
        Answers a natural language question by retrieving context and using Gemini.
        
        Args:
            question (str): The natural language question.
            entity_type (str, optional): The type of entity (e.g., "supplier", "campaign", "product").
            entity_id (str, optional): The ID of the entity.
            
        Returns:
            str: The natural language answer.
        """
        # If entity info is missing, try to extract it using NER
        if not entity_type or not entity_id:
            extracted_entities = get_canonical_entities(question)
            
            # Logic to pick the "primary" entity if multiple are found
            # For now, we prioritize Supplier > Campaign > Product
            if 'Supplier' in extracted_entities and extracted_entities['Supplier']:
                entity_type = 'supplier'
                entity_id = extracted_entities['Supplier'][0] # Assumption: Entity Linking returns the canonical ID/Name
                # Note: If get_canonical_entities returns a Name, we might need to resolve it to an ID 
                # or update get_supplier_context to search by Name.
                # Assuming here that the canonical form IS the ID or a unique Name queryable by the retriever.
            elif 'Campaign' in extracted_entities and extracted_entities['Campaign']:
                entity_type = 'campaign'
                entity_id = extracted_entities['Campaign'][0]
            elif 'Product' in extracted_entities and extracted_entities['Product']:
                entity_type = 'product'
                entity_id = extracted_entities['Product'][0]
            
            if not entity_type:
                return "I couldn't identify any specific supplier, campaign, or product in your question. Please specify one."

        context = ""
        # Normalize entity type to lowercase for comparison
        entity_type = entity_type.lower()

        if entity_type == "supplier":
            # Note: You might need to adjust get_supplier_context if entity_id is a Name, not an ID.
            # If the NER returns "Acme Corp" but the ID is "SUP-001", the retriever needs to handle it.
            # For this sprint, we assume the extracted 'entity_id' can be used to find the record (or we need a lookup).
            # Let's assume for now the retriever might need a slight tweak or the NER returns something usable.
            # Ideally, get_canonical_entities returns the NAME, so we should query by NAME or Alias.
            # For now, passing the extracted string.
            context = self.context_retriever.get_supplier_context(entity_id) 
            template = self.jinja_env.get_template('supplier.j2')
        elif entity_type == "campaign":
            context = self.context_retriever.get_campaign_context(entity_id)
            template = self.jinja_env.get_template('campaign.j2')
        elif entity_type == "product":
            context = self.context_retriever.get_product_context(entity_id)
            template = self.jinja_env.get_template('product.j2')
        else:
            return f"Unsupported entity type: {entity_type}"

        if "No context found" in context:
             # Fallback: If lookup by ID failed, maybe it was a Name? 
             # (This logic depends heavily on what `get_supplier_context` expects.
             # If it expects an ID like 'SUP-001' but gets 'Acme Corp', it fails.
             # We might need to update ContextRetriever to search by Name property as well.)
            return f"I found a {entity_type} named '{entity_id}', but I couldn't retrieve detailed data for it."

        prompt = template.render(context=context, question=question)
        answer = self._generate_answer(prompt)
        return answer

    def close(self):
        """Closes the Neo4j driver connection in the context retriever."""
        self.context_retriever.close()

if __name__ == '__main__':
    # Example Usage
    rag = HelixRAG()

    # Example 1: Ask about a supplier
    supplier_question = "What is their risk score and what campaigns are they linked to?"
    supplier_id = "SUP-001" # Replace with an actual supplier ID from your Neo4j data
    print(f"Question about Supplier {supplier_id}: {supplier_question}")
    answer = rag.ask(supplier_question, "supplier", supplier_id)
    print(f"Answer: {answer}\n")

    # Example 2: Ask about a campaign
    campaign_question = "What was the budget for this campaign and which suppliers were involved?"
    campaign_id = "CAMP_2024_Q1" # Replace with an actual campaign ID from your Neo4j data
    print(f"Question about Campaign {campaign_id}: {campaign_question}")
    answer = rag.ask(campaign_question, "campaign", campaign_id)
    print(f"Answer: {answer}\n")

    # Example 3: Ask about a product
    product_question = "Is this product critical and what is the total spend on it?"
    product_sku = "PROD-001" # Replace with an actual product SKU from your Neo4j data
    print(f"Question about Product {product_sku}: {product_question}")
    answer = rag.ask(product_question, "product", product_sku)
    print(f"Answer: {answer}\n")

    rag.close()
