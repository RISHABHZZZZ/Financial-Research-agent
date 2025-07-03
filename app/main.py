# app/main.py

import os
from dotenv import load_dotenv
from logging_config import setup_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logger(__name__)

def main():
    try:
        logger.info("Starting Company Research Agent bootstrap...")

        ollama_url = os.getenv("OLLAMA_API_URL")
        if not ollama_url:
            logger.error("OLLAMA_API_URL is not set in your .env file.")
            raise ValueError("Missing OLLAMA_API_URL in environment.")

        logger.debug(f"OLLAMA_API_URL: {ollama_url}")

        # Here, we'll later initialize LangGraph and Streamlit
        logger.info("Bootstrap complete. Ready to proceed to next steps.")

    except Exception as e:
        logger.exception("An error occurred during bootstrap.")

if __name__ == "__main__":
    main()
