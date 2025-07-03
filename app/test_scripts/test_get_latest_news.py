from app.nodes.get_latest_news import get_latest_news
from app.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    state = {
        "company_name": "Apple Inc.",
        "region": "US"
    }
    logger.info("Testing get_latest_news node...")
    result = get_latest_news(state)
    print("\n=== RAW RESULT ===")
    print(result)

    print("\n=== PARSED NEWS ===")
    # This prevents KeyError
    if "latest_news" in result:
        print(result["latest_news"])
    elif "news" in result:
        print(result["news"])
    elif "error" in result:
        print("Error:", result["error"])
    else:
        print("Unexpected response:", result)

if __name__ == "__main__":
    main()
