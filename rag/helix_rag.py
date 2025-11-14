import google.genai as genai
from google.genai import types
from jinja2 import Environment, FileSystemLoader
import os
from rag.config import get_config
from rag.context_retriever import GraphContextRetriever

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

    def ask(self, question: str, entity_type: str, entity_id: str) -> str:
        """
        Answers a natural language question by retrieving context and using Gemini.
        
        Args:
            question (str): The natural language question.
            entity_type (str): The type of entity (e.g., "supplier", "campaign", "product").
            entity_id (str): The ID of the entity.
            
        Returns:
            str: The natural language answer.
        """
        context = ""
        if entity_type == "supplier":
            context = self.context_retriever.get_supplier_context(entity_id)
            template = self.jinja_env.get_template('supplier.j2')
        elif entity_type == "campaign":
            context = self.context_retriever.get_campaign_context(entity_id)
            template = self.jinja_env.get_template('campaign.j2')
        elif entity_type == "product":
            context = self.context_retriever.get_product_context(entity_id)
            template = self.jinja_env.get_template('product.j2')
        else:
            return "Unsupported entity type."

        if "No context found" in context:
            return context # Return the error message from retriever

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
