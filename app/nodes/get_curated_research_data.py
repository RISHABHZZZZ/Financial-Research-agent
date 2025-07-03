# app/nodes/get_curated_research_data.py

from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file
from utils.model_client import run_model_chat

logger = setup_logger(__name__)

def get_curated_research_data(state: dict) -> dict:
    company_name = state.get("company_name")

    if not company_name:
        logger.error("Company name missing in state.")
        return {**state, "curated_text": "Company name not provided."}

    file_path = get_company_file_path(company_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except FileNotFoundError:
        logger.error("Raw data file not found.")
        return {**state, "curated_text": "No raw data file found."}

    prompt = (
        f"Extract only sections relevant to {company_name}'s Indian operations, financial disclosures, numeric data, or business activities.\n"
        "Remove generic marketing content.\n\n"
        f"{raw_content}"
    )

    try:
        content = run_model_chat(
            prompt,
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            backend="openrouter"
        )
        append_section_to_file(file_path, "Curated Relevant Data", content)
        logger.info("Curated data generated.")
        return {**state, "curated_text": content}
    except Exception:
        logger.exception("Error generating curated research data.")
        return {**state, "curated_text": "Curation failed."}
