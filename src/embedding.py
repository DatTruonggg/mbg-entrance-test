import os
import glob
import openai
import tiktoken
from typing import List, Dict, Any, Optional
from logs.logging import log
from configs import config
import uuid  

class Embedding:
    """
    Handles text embedding and chunking for documents.
    """
    def __init__(self):
        """
        Initializes OpenAI embedding model and tokenizer.
        """
        self.openai_client = openai.OpenAI(api_key=config.open_api_key)
        self.embedding_model = config.embedding_model
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.chunk_size = config.chunk_size
        self.chunk_overlap = config.chunk_overlap
        self.data_dir = config.data_dir
        
    def _collect_file_paths(self, file_extension=".txt") -> List[str]:
        """
        Retrieves document file paths from the configured directory.

        Args:
            file_extension (str): The file extension to look for.

        Returns:
            List[str]: A list of document file paths.
        """
        pattern = f"*{file_extension}"

        return glob.glob(os.path.join(self.data_dir, pattern))

    def _read_documents(self) -> List[Dict[str, Any]]:
        """
        Reads text documents from files and prepares metadata.

        Returns:
            List[Dict[str, Any]]: A list of document dictionaries.
        """
        documents = []

        file_paths = self._collect_file_paths()
        for path in file_paths:
            metadata = {
                "source": path,
                "file_name": os.path.basename(path),
                "file_size": os.path.getsize(path)
            }
            with open(path, 'r', encoding='utf-8') as file:
                text_content = file.read()

            doc = {
                "id": metadata["file_name"],
                "text": text_content,  
                "metadata": metadata
            }
            documents.append(doc)

        return documents

    def _generate_chunks(self, document_text: str) -> List[str]:
        """
        Splits a document into smaller chunks for embedding.

        Args:
            document_text (str): The document content.

        Returns:
            List[str]: A list of text chunks.
        """
        tokens = self.tokenizer.encode(document_text)
        total_tokens = len(tokens)
        cursor = 0
        chunks = []

        while cursor < total_tokens:
            chunk = tokens[cursor: cursor + self.chunk_size]
            chunks.append(self.tokenizer.decode(chunk))
            cursor += self.chunk_size - self.chunk_overlap

        return chunks

    def _generate_embeddings(self, text_segments: List[str]) -> List[List[float]]:
        """
        Generates embeddings for the given text segments.

        Args:
            text_segments (List[str]): The list of text chunks.

        Returns:
            List[List[float]]: A list of embeddings.
        """
        try:
            result = self.openai_client.embeddings.create(input=text_segments, model=self.embedding_model)
            return [entry.embedding for entry in result.data]
        except Exception as error:
            log.error(f"Error while embedding texts: {error}")
            raise

    def process(self) -> List[Dict[str, Any]]:
        """
        Processes and embeds documents, either from input or file storage.

        Args:
            documents (Optional[List[Dict[str, Any]]]): List of documents to process. 
                If None, loads from the file system.

        Returns:
            List[Dict[str, Any]]: A list of processed document chunks with embeddings.
        """
        documents = self._read_documents()

        processed_chunks = []

        for doc in documents:
            chunked_texts = self._generate_chunks(doc["text"])  
            chunk_count = len(chunked_texts)

            for idx, chunk_text in enumerate(chunked_texts):
                chunk_entry = {
                    "id": str(uuid.uuid4()), 
                    "text": chunk_text,  
                    "metadata": {
                        **doc["metadata"],
                        "chunk_index": idx,
                        "total_chunks": chunk_count,
                        "text": chunk_text  
                    }
                }
                processed_chunks.append(chunk_entry)

        for start_idx in range(0, len(processed_chunks), 100):
            current_batch = processed_chunks[start_idx:start_idx + 100]
            texts_for_embedding = [item["text"] for item in current_batch]
            embeddings_batch = self._generate_embeddings(texts_for_embedding)

            for chunk_item, embedding in zip(current_batch, embeddings_batch):
                chunk_item["embedding"] = embedding

        return processed_chunks
