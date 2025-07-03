# app/nodes/get_stock_info.py

import yfinance as yf
from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file

logger = setup_logger(__name__)

def get_stock_info(state: dict) -> dict:
    ticker_symbol = state.get("ticker")
    company_name = state.get("company_name")

    logger.info(f"Starting get_stock_info for: {ticker_symbol}")

    if not ticker_symbol:
        logger.warning("No ticker symbol provided.")
        return {**state, "stock_info": "Stock information could not be retrieved."}

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        current_price = info.get("regularMarketPrice")
        high_52w = info.get("fiftyTwoWeekHigh")
        low_52w = info.get("fiftyTwoWeekLow")

        hist = ticker.history(period="60d")
        if hist.empty:
            logger.warning("No historical data retrieved.")
            return {**state, "stock_info": "Stock information could not be retrieved."}

        last_close = hist["Close"].iloc[-1]
        month_ago_close = hist["Close"].iloc[-21]
        pct_change = ((last_close - month_ago_close) / month_ago_close) * 100

        hist["Return"] = hist["Close"].pct_change()
        volatility = hist["Return"][-30:].std() * 100

        markdown = (
            f"- **Current Price:** ${current_price:.2f}\n"
            f"- **52-Week High:** ${high_52w:.2f}\n"
            f"- **52-Week Low:** ${low_52w:.2f}\n"
            f"- **1-Month Change:** {pct_change:+.2f}%\n"
            f"- **Volatility (Std Dev over 30 days):** {volatility:.2f}%"
        )

        file_path = get_company_file_path(company_name)
        append_section_to_file(file_path, "Stock Information", markdown)

        logger.info("Stock information retrieved.")
        return {**state, "stock_info": markdown}

    except Exception:
        logger.exception("Error retrieving stock information.")
        return {**state, "stock_info": "Stock information could not be retrieved."}
