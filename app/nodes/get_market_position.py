# app/nodes/get_market_position.py

from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file
from utils.model_client import run_model_chat

logger = setup_logger(__name__)

def get_market_position(state: dict) -> dict:
    company_name = state.get("company_name")
    overview_text = state.get("company_overview", "")

    logger.info(f"Starting get_market_position for: {company_name}")

    if not overview_text:
        logger.warning("No company overview available, skipping.")
        return {**state, "market_position": "Market position information could not be retrieved."}

    prompt = (
        "You are a financial analyst. Based on the following company overview, "
        "write a comprehensive paragraph only using important and relevant describing the company's market position, competitive advantages, and key competitors.\n\n"
        f"Company Overview:\n{overview_text}"
    )

    try:
        content = run_model_chat(
            prompt,
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            backend="openrouter"
        )
        file_path = get_company_file_path(company_name)
        append_section_to_file(file_path, "Market Position", content)
        logger.info("Market position generated.")
        return {**state, "market_position": content}
    except Exception:
        logger.exception("Error generating market position.")
        return {**state, "market_position": "Market position could not be retrieved."}
