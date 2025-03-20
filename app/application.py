from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import logging
from logs.logging import log

# Import necessary services
from service.qdrant_service import VectorDBService
from src.retriever import DocumentRetriever
from src.reranker import Reranker
from src.perform_llm import PerformLLM
from src.route import Route
from db.s3_db import S3Handler
from configs import config

# Initialize FastAPI
app = FastAPI(
    title="RAG for Cryptocurrency",
    description="FastAPI demo for cryptocurrency crime investigation",
    version="0.0.1"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize S3 Handler
s3_storage = S3Handler()

# Health Check Endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Investigation API Endpoint
@app.post("/crypto_investigate")
async def crypto_investigate(query: Dict[str, str]):
    """
    Executes the full RAG pipeline for cryptocurrency crime investigation and uploads report to S3.

    Args:
        query (Dict[str, str]): {"query": "some query text", "user_id": "some_user_id"}

    Returns:
        JSON response with investigation results and S3 storage status.
    """
    try:
        query_text = query.get("query", "").strip()
        user_id = query.get("user_id", "unknown_user")  # Default if user_id is missing
        log.info(f"Received investigation query: {query_text} from {user_id}")

        # Initialize required components
        route = Route()
        retriever = DocumentRetriever()
        reranker = Reranker()
        report_generator = PerformLLM()

        # Step 1: Validate the query
        is_valid, reason = route.assess_query(query_text)
        if not is_valid:
            log.warning(f"Query rejected: {reason}")
            return {
                "query": query_text,
                "error": True,
                "message": "Query is not relevant to crypto crime investigation",
                "reason": reason
            }

        log.info(f"Query is valid: {reason}")

        # Step 2: Retrieve relevant documents from Qdrant
        retrieval_result = retriever.retrieve(query_text)
        if not retrieval_result["documents"]:
            log.warning("No relevant documents found.")
            return {
                "query": query_text,
                "retrieval": "No relevant documents found",
                "error": True
            }

        log.info(f"Retrieved {len(retrieval_result['documents'])} documents.")

        # Step 3: Rank the retrieved documents
        ranked_docs = reranker.rank_evidence(query_text, retrieval_result["documents"])
        retrieval_result["documents"] = ranked_docs
        log.info(f"Top {len(ranked_docs)} ranked documents selected.")

        # Step 4: Generate an investigation report using LLM
        report_data = report_generator.generate_report(query_text, ranked_docs, retrieval_result)
        report_data["user_id"] = user_id  # Attach user_id for tracking
        log.info("Investigation report generated.")

        # Step 5: Upload the report to S3
        storage_result = s3_storage.upload_report(report_data)

        # Step 6: Return the final response
        return {
            "query": query_text,
            "retrieval": retrieval_result,
            "report": report_data,
            "storage": storage_result,
        }

    except Exception as e:
        log.error(f"Error processing investigation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Investigation failed: {str(e)}")
