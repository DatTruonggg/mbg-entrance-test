from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from typing import List, Dict, Any
from configs import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantDB:
    """
    Manages vector storage and retrieval using Qdrant.
    """

    def __init__(self):
        """
        Initializes the connection to Qdrant, ensuring the collection is ready.
        """
        self.client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
        self.collection_name = config.qdrant_collection

        self._initialize_collection()

    def _initialize_collection(self):
        """
        Creates the collection in Qdrant if it does not already exist.
        """
        existing_collections = [col.name for col in self.client.get_collections().collections]
        if self.collection_name not in existing_collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=config.embedding_dim, distance=Distance.COSINE),
            )
            logger.info(f"Qdrant collection '{self.collection_name}' created.")

    def add_vectors(self, ids: List[str], vectors: List[List[float]], metadata: List[Dict[str, Any]]):
        """
        Inserts vectors into Qdrant with correct payload structure.
        """
        try:
            points = []
            for doc_id, vec, meta in zip(ids, vectors, metadata):
                if "text" not in meta:
                    logger.error(f"❌ Missing 'text' in metadata for document {doc_id}: {meta}")
                
                payload = {"text": meta.get("text", ""), **meta}
                
                points.append({
                    "id": doc_id,
                    "vector": vec,
                    "payload": payload
                })

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info("✅ Successfully inserted vectors into Qdrant.")

        except Exception as e:
            logger.error(f"❌ Error inserting vectors into Qdrant: {e}")

    def similarity_search(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        Searches for similar vectors in Qdrant.

        Args:
            query_embedding (List[float]): Query embedding vector.
            top_k (int): Number of top similar documents to return.

        Returns:
            List[Dict[str, Any]]: Retrieved documents sorted by relevance.
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
            )
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "metadata": hit.payload,
                }
                for hit in results
            ]

        except Exception as e:
            logger.error(f"Error performing similarity search in Qdrant: {e}")
            return []

    def delete_all(self):
        """
        Deletes all stored vectors from Qdrant.
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Successfully deleted collection '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
