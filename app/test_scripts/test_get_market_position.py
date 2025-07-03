from app.utils.load_environment import ensure_environment
ensure_environment()

from app.nodes.get_market_position import get_market_position
from app.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    state = {
        "company_name": "Apple Inc.",
        "company_overview": (
            "Apple Inc. is an American multinational corporation and technology company headquartered in Cupertino, California, "
            "in Silicon Valley..."
        )
    }

    logger.info("Testing get_market_position node...")
    result = get_market_position(state)
    print("\n=== MARKET POSITION RESULT ===")
    print(result["market_position"])

if __name__ == "__main__":
    main()
