# app/nodes/generate_final_report.py

import os
import json
from logging_config import setup_logger
from utils.file_helpers import get_company_file_path
from utils.model_client import run_model_chat

logger = setup_logger(__name__)

def generate_final_report(state: dict) -> dict:
    company_name = state.get("company_name")

    if not company_name:
        logger.error("Company name missing in state.")
        return {**state, "final_report": "Company name not provided."}

    # Load the raw text
    file_path = get_company_file_path(company_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except FileNotFoundError:
        logger.error("Raw data file not found.")
        return {**state, "final_report": "No raw data file found."}

    # Structured data
    extracted_facts = state.get("extracted_facts")
    financials = state.get("financials")
    financial_ratios = state.get("financial_ratios")

    # Convert to formatted JSON text
    structured_data_text = (
        json.dumps(extracted_facts, indent=2) if isinstance(extracted_facts, dict) else "No structured data extracted."
    )
    financials_text = (
        json.dumps(financials, indent=2) if isinstance(financials, dict) else "No financials available."
    )
    financial_ratios_text = (
        json.dumps(financial_ratios, indent=2) if isinstance(financial_ratios, dict) else "No financial ratios available."
    )

    # Compose prompt
    prompt = (
        f"You are a senior equity research analyst.\n\n"
        "**Task:** Create a detailed, professional company research report for **{company_name}**.\n\n"
        "**Guidelines:**\n"
        "- Use ALL structured numeric data as the primary source.\n"
        "- Supplement with the narrative text.\n"
        "- Include all numeric metrics and computed ratios in the Financial Metrics & Ratios section.\n"
        "- If any section is missing data, state it explicitly.\n"
        "- Write in a polished, neutral tone suitable for investors.\n\n"
        "### Financial Data:\n"
        f"{financials_text}\n\n"
        "### Financial Ratios:\n"
        f"{financial_ratios_text}\n\n"
        "### Structured Extracted Facts:\n"
        f"{structured_data_text}\n\n"
        "### Additional Narrative Data:\n"
        f"{raw_content}\n\n"
        "**Return Markdown with these sections:**\n"
        "1. Executive Summary\n"
        "2. Company Profile\n"
        "3. Leadership & Governance\n"
        "4. Market Position\n"
        "5. M&A Activity\n"
        "6. CSR and ESG\n"
        "7. Innovation and R&D\n"
        "8. Talent and Workforce\n"
        "9. Risk Management\n"
        "10. Financial Metrics and Ratios with commentary\n"
        "11. Conclusion\n"
        "12. Sources\n\n"
        "**Important:**\n"
        "- Do not omit any numeric data.\n"
        "- Clearly reference specific figures and ratios."
    )

    # Save prompt to a file for inspection
    prompt_file_path = file_path.replace("_raw.txt", "_final_prompt.txt")
    with open(prompt_file_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    logger.debug(f"Saved prompt text to {prompt_file_path}")

    try:
        content = run_model_chat(
            prompt,
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            backend="openrouter"
        )
        logger.info("Final report generated.")
        return {**state, "final_report": content}
    except Exception:
        logger.exception("Error generating final report.")
        return {**state, "final_report": "Report generation failed."}
