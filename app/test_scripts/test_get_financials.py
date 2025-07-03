# app/test_get_financials.py

from nodes.get_financials import get_financials
from logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    state = {
    "company_name": "deloitte",
    "ticker": "DLT",
    "region": "IN"
}
    logger.info("Testing get_financials node...")
    result = get_financials(state)
    print("\n=== FINANCIALS RESULT ===")
    print(result)

if __name__ == "__main__":
    main()
