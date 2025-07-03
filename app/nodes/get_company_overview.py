# app/nodes/get_company_overview.py

import wikipedia
import yfinance as yf
from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file

logger = setup_logger(__name__)

def get_company_overview(state: dict) -> dict:
    company_name = state.get("company_name")
    ticker = state.get("ticker")

    if not company_name:
        logger.error("No company name provided.")
        return {**state, "company_overview": "No company name provided."}

    logger.info(f"Fetching company overview for: {company_name}")

    overview_text = None

    # Wikipedia
    try:
        logger.debug("Trying Wikipedia...")
        page = wikipedia.page(company_name, auto_suggest=False)
        summary = page.summary
        if summary:
            logger.info("Wikipedia summary found.")
            overview_text = summary
    except wikipedia.exceptions.DisambiguationError as e:
        logger.warning(f"Disambiguation error: {e.options}")
        overview_text = f"Multiple Wikipedia pages found: {e.options}"
    except wikipedia.exceptions.PageError:
        logger.warning("Wikipedia page not found.")
    except Exception:
        logger.exception("Wikipedia lookup error.")

    # Fallback to yfinance
    if not overview_text or "Multiple Wikipedia pages" in overview_text:
        try:
            if not ticker:
                logger.warning("No ticker provided for Yahoo Finance fallback.")
            else:
                logger.debug("Trying Yahoo Finance...")
                yf_ticker = yf.Ticker(ticker)
                info = yf_ticker.info
                summary = info.get("longBusinessSummary")
                if summary:
                    logger.info("Yahoo Finance summary found.")
                    overview_text = summary
        except Exception:
            logger.exception("Yahoo Finance lookup error.")

    # Final fallback
    if not overview_text:
        overview_text = f"{company_name} is a publicly traded company. Detailed overview could not be retrieved."

    # Append to raw file
    file_path = get_company_file_path(company_name)
    append_section_to_file(file_path, "Company Overview", overview_text)

    return {**state, "company_overview": overview_text}
