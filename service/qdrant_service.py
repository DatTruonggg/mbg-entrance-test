import logging
from typing import List, Dict, Any, Optional
from db.qdrant_db import QdrantDB
from src.embedding import Embedding
from logs.logging import log


class VectorDBService:
    """
    Handles embedding documents and storing them in Qdrant.
    """

    def __init__(self):
        """
        Initializes the embedding processor and Qdrant database connection.
        """
        self.embedding_processor = Embedding()
        self.qdrant_db = QdrantDB()

    def load_all_documents(self) -> Dict[str, Any]:
        """
        Loads and embeds all documents, then stores them in Qdrant.

        Args:
            documents (Optional[List[Dict[str, Any]]]): List of documents to process and store.
                If None, it will process files from the configured `data_dir`.

        Returns:
            Dict[str, Any]: A response indicating the success/failure of the operation.
        """
        try:
            log.info("Starting document loading process...")

            processed_chunks = self.embedding_processor.process()

            if not processed_chunks:
                log.warning("No documents found for processing.")
                return {"success": False, "message": "No documents available to embed."}

            log.info(f"Processed {len(processed_chunks)} document chunks.")

            # Extract vectors & metadata
            doc_ids = [doc["id"] for doc in processed_chunks]
            embeddings = [doc["embedding"] for doc in processed_chunks]
            metadata = [doc["metadata"] for doc in processed_chunks]

            # Store in Qdrant
            self.qdrant_db.add_vectors(doc_ids, embeddings, metadata)

            log.info("Successfully uploaded documents to Qdrant.")

            return {
                "success": True,
                "chunk_count": len(processed_chunks),
                "message": "Documents successfully loaded and embedded into Qdrant."
            }

        except Exception as e:
            log.error(f"Error loading documents: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to load documents into Qdrant."
            }
