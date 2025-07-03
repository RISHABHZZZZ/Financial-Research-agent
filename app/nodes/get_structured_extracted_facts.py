# # app/nodes/get_structured_extracted_facts.py

# import os
# import requests
# from logging_config import setup_logger
# from utils.file_helpers import get_company_file_path, append_section_to_file
# import json

# logger = setup_logger(__name__)

# def get_structured_extracted_facts(state: dict) -> dict:
#     """
#     Node to extract structured numeric and factual data using LLM.
#     """
#     company_name = state.get("company_name")

#     if not company_name:
#         logger.error("Company name missing in state.")
#         return {**state, "extracted_facts": "Company name not provided."}

#     # Load the raw text
#     file_path = get_company_file_path(company_name)
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             raw_content = f.read()
#     except FileNotFoundError:
#         logger.error("Raw data file not found.")
#         return {**state, "extracted_facts": "No raw data file found for this company."}

#     # Compose prompt
#     prompt = (
#         f"You are a financial data extraction assistant.\n\n"
#         f"**Task:** From the raw text below, extract all relevant numeric financial metrics, M&A activity, leadership changes, awards, and certifications. \n"
#         "- Return a JSON object with the following keys:\n"
#         "  - 'financial_metrics': dictionary of metrics (Revenue, Net Income, Employees, etc.)\n"
#         "  - 'mergers_acquisitions': list of M&A events\n"
#         "  - 'leadership_changes': list of leadership announcements\n"
#         "  - 'awards_certifications': list of awards or certifications\n"
#         "- If no data is available for a section, return an empty list or empty dictionary.\n\n"
#         "**Raw Text:**\n\n"
#         f"{raw_content}\n\n"
#         "**Important:** Only output the JSON. No extra commentary."
#     )
# #
#     ollama_url = os.getenv("OLLAMA_API_URL")
#     if not ollama_url:
#         logger.error("OLLAMA_API_URL not configured.")
#         return {**state, "extracted_facts": "OLLAMA API URL missing."}

#     payload = {
#         "model": "llama3:8b",
#         "stream": False,
#         "num_predict": 30000,
#         "temperature": 0.1,
#         "messages": [
#             {"role": "system", "content": "You are a structured data extractor."},
#             {"role": "user", "content": prompt}
#         ]
#     }

#     try:
#         logger.debug("Sending structured extraction prompt to Ollama...")
#         response = requests.post(ollama_url, json=payload, timeout=300)
#         response.raise_for_status()
#         data = response.json()
#         content = data.get("message", {}).get("content")

#         if content:
#             try:
#                 parsed = json.loads(content)
#                 # Append as pretty JSON
#                 formatted = json.dumps(parsed, indent=2)
#                 append_section_to_file(file_path, "Structured Extracted Facts", formatted)
#                 logger.info("Structured facts extracted and saved.")
#                 return {**state, "extracted_facts": parsed}
#             except json.JSONDecodeError:
#                 logger.warning("LLM did not return valid JSON.")
#                 return {**state, "extracted_facts": "Invalid JSON returned by LLM."}
#         else:
#             logger.warning("Ollama response empty.")
#             return {**state, "extracted_facts": "No content returned."}

#     except Exception:
#         logger.exception("Error extracting structured facts.")
#         return {**state, "extracted_facts": "Extraction failed due to exception."}


# app/nodes/get_structured_extracted_facts.py

import json
from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file
from utils.model_client import run_model_chat

logger = setup_logger(__name__)

def get_structured_extracted_facts(state: dict) -> dict:
    company_name = state.get("company_name")

    if not company_name:
        logger.error("Company name missing in state.")
        return {**state, "extracted_facts": "Company name not provided."}

    file_path = get_company_file_path(company_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except FileNotFoundError:
        logger.error("Raw data file not found.")
        return {**state, "extracted_facts": "No raw data file found."}

    prompt = (
        "Extract all numeric financial metrics, M&A events, leadership changes, awards, and certifications.\n"
        "Return as JSON with keys: 'financial_metrics', 'mergers_acquisitions', 'leadership_changes', 'awards_certifications'.\n\n"
        f"{raw_content}"
    )

    try:
        content = run_model_chat(
            prompt,
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            backend="openrouter"
        )
        parsed = json.loads(content)
        formatted = json.dumps(parsed, indent=2)
        append_section_to_file(file_path, "Structured Extracted Facts", formatted)
        logger.info("Structured facts extracted.")
        return {**state, "extracted_facts": parsed}
    except json.JSONDecodeError:
        logger.warning("Invalid JSON returned by LLM.")
        return {**state, "extracted_facts": "Invalid JSON."}
    except Exception:
        logger.exception("Error extracting structured facts.")
        return {**state, "extracted_facts": "Extraction failed."}
