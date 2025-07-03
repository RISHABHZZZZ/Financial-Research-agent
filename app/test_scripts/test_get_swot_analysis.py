# app/test_get_swot_analysis.py

from app.utils.load_environment import ensure_environment
ensure_environment()

from app.nodes.get_swot_analysis import get_swot_analysis
from app.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    state = {
        "company_name": "Apple Inc.",
        "company_overview": (
            "Apple Inc. is an American multinational corporation and technology company headquartered in Cupertino, California. "
            "It is best known for its consumer electronics, software, and services."
        ),
        "market_position": (
            "Apple holds a dominant market position in the premium smartphone segment and has strong brand recognition globally."
        ),
        "financials": {
            "Market Cap": "$3,000,000,000,000",
            "Revenue": "$394 Billion",
            "Net Income": "$97 Billion",
            "P/E Ratio": "31.4",
            "Dividend Yield": "0.52%",
            "52 Week High": "$198",
            "52 Week Low": "$124"
        }
    }

    logger.info("Testing get_swot_analysis node...")
    result = get_swot_analysis(state)
    print("\n=== SWOT ANALYSIS RESULT ===")
    print(result["swot_analysis"])

if __name__ == "__main__":
    main()
