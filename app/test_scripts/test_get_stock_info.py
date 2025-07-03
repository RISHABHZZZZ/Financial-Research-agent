# app/test_get_stock_info.py

from app.utils.load_environment import ensure_environment
ensure_environment()

from app.nodes.get_stock_info import get_stock_info
from app.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    state = {
        "ticker": "AAPL"
    }

    logger.info("Testing get_stock_info node...")
    result = get_stock_info(state)
    print("\n=== STOCK INFO RESULT ===")
    print(result["stock_info"])

if __name__ == "__main__":
    main()
