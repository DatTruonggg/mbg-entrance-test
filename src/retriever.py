import openai
import json
from typing import List, Dict, Any, Tuple
from configs import config
from db.qdrant_db import QdrantDB
from src.prompt_engineering import build_expanded_query_prompt


class DocumentRetriever:
    """
    Retrieves relevant case documents using multi-step retrieval strategy with Qdrant.
    """

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=config.open_api_key)
        self.qdrant_db = QdrantDB()
        self.top_k = config.top_k_retrieval
        self.strategy = config.strategy  # Single-step or multi-step retrieval

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for the given text using OpenAI's model.

        Args:
            text (str): The input text to be embedded.

        Returns:
            List[float]: A vector representation of the text.
        """
        response = self.openai_client.embeddings.create(
            input=[text],
            model=config.embedding_model
        )
        return response.data[0].embedding

    def _generate_expanded_queries(self, query: str) -> List[str]:
        """
        Uses LLM to generate multiple refined search queries for deeper retrieval.

        Args:
            query (str): The investigator's original query.

        Returns:
            List[str]: A list of expanded queries covering different investigative aspects.
        """
        prompt = build_expanded_query_prompt(query)

        response = self.openai_client.chat.completions.create(
            model=config.gpt_model,
            messages=[
                {"role": "system", "content": "You are a cybercrime forensic assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )

        try:
            content = response.choices[0].message.content
            queries = json.loads(content)
            return queries if isinstance(queries, list) else [query]
        except Exception as e:
            print(f"Error generating expanded queries: {e}")
            return [query]

    def retrieve(self, query: str) -> Dict[str, Any]:
        """
        Retrieves documents using single-step or multi-step retrieval strategy.

        Args:
            query (str): The investigator's search query.

        Returns:
            Dict[str, Any]: Retrieved documents and metadata.
        """
        # Step 1: Generate query embedding
        query_embedding = self._get_embedding(query)

        # Step 2: Perform initial retrieval from Qdrant
        initial_results = self.qdrant_db.similarity_search(query_embedding, self.top_k)

        # Step 3: Multi-step retrieval (if enabled)
        expanded_queries = []
        all_documents = initial_results

        if self.strategy == "multi-step":
            expanded_queries = self._generate_expanded_queries(query)
            for exp_query in expanded_queries:
                exp_embedding = self._get_embedding(exp_query)
                additional_results = self.qdrant_db.similarity_search(exp_embedding, self.top_k)
                all_documents.extend(additional_results)

            # Remove duplicates by document ID
            all_documents = {doc["id"]: doc for doc in all_documents}.values()

        return {
            "documents": list(all_documents),
            "strategy": self.strategy,
            "expanded_queries": expanded_queries if self.strategy == "multi-step" else None
        }
