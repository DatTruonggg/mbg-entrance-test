import logging
from service.qdrant_service import VectorDBService
from logs.logging import log

def main():
    log.info("🚀 Starting document loading process into Qdrant...")
    try:
        service = VectorDBService()
        response = service.load_all_documents()
        if response["success"]:
            log.info(f"Successfully loaded {response.get('chunk_count', 0)} document chunks into Qdrant.")
        else:
            log.error(f"Failed to load documents: {response.get('error', 'Unknown error')}")
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
