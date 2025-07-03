# # app/nodes/get_swot_analysis.py

# import requests
# import os
# from logging_config import setup_logger
# from utils.file_helpers import get_company_file_path, append_section_to_file

# logger = setup_logger(__name__)

# def get_swot_analysis(state: dict) -> dict:
#     company_name = state.get("company_name")
#     ticker = state.get("ticker")
#     overview_text = state.get("company_overview", "")
#     market_position_text = state.get("market_position", "")
#     financials = state.get("financials", {})

#     logger.info(f"Starting get_swot_analysis for: {company_name}")

#     if not overview_text:
#         logger.warning("No company overview available, skipping.")
#         return {**state, "swot_analysis": "SWOT analysis could not be generated."}

#     ollama_url = os.getenv("OLLAMA_API_URL")
#     if not ollama_url:
#         logger.error("OLLAMA_API_URL is not set.")
#         return {**state, "swot_analysis": "SWOT analysis could not be generated."}

#     financials_text = (
#         "\n".join(f"- {k}: {v}" for k, v in financials.items())
#         if financials else "No financial data available."
#     )

#     prompt = (
#         f"You are a senior financial analyst. Your task is to create a detailed, comprehensive SWOT analysis for the following company.\n\n"
#         f"**Company Overview:**\n{overview_text}\n\n"
#         f"**Market Position:**\n{market_position_text}\n\n"
#         f"**Financial Summary:**\n{financials_text}\n\n"
#         "Use the above information to create each section of the SWOT analysis, citing relevant facts where applicable.\n\n"
#         "Format in markdown with headings 'Strengths', 'Weaknesses', 'Opportunities', 'Threats'. "
#         "Each section should have 3-5 bullet points. Return only markdown."
#     )

#     payload = {
#         "model": "llama3:8b",
#         "num_predict": 10000,
#         "stream": False,
#         "messages": [
#             {"role": "system", "content": "You are a helpful and precise financial analyst."},
#             {"role": "user", "content": prompt}
#         ]
#     }

#     try:
#         logger.debug("Sending prompt to Ollama...")
#         response = requests.post(ollama_url, json=payload, timeout=180)
#         response.raise_for_status()
#         data = response.json()
#         content = data.get("message", {}).get("content")
#         if content:
#             logger.info("SWOT analysis generated.")
#             file_path = get_company_file_path(company_name)
#             append_section_to_file(file_path, "SWOT Analysis", content.strip())
#             return {**state, "swot_analysis": content.strip()}
#         else:
#             logger.warning("Ollama response did not contain content.")
#             return {**state, "swot_analysis": "SWOT analysis could not be generated."}
#     except Exception:
#         logger.exception("Error generating SWOT analysis.")
#         return {**state, "swot_analysis": "SWOT analysis could not be generated."}


# app/nodes/get_swot_analysis.py

from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file
from utils.model_client import run_model_chat

logger = setup_logger(__name__)

def get_swot_analysis(state: dict) -> dict:
    company_name = state.get("company_name")
    overview_text = state.get("company_overview", "")
    market_position_text = state.get("market_position", "")
    financials = state.get("financials", {})

    logger.info(f"Starting get_swot_analysis for: {company_name}")

    if not overview_text:
        logger.warning("No company overview available, skipping.")
        return {**state, "swot_analysis": "SWOT analysis could not be generated."}

    financials_text = (
        "\n".join(f"- {k}: {v}" for k, v in financials.items())
        if financials else "No financial data available."
    )

    prompt = (
        f"You are a senior financial analyst with expertise in comprehensive business analysis. "
        f"Using the information provided below, create a detailed, professional SWOT analysis of the company.\n\n"
        f"**Company Overview:**\n{overview_text}\n\n"
        f"**Market Position:**\n{market_position_text}\n\n"
        f"**Financial Summary:**\n{financials_text}\n\n"
        "Your analysis must:\n"
        "- Be factual and grounded only in the information above. Avoid adding assumptions not supported by the data.\n"
        "- Use a clear, neutral, professional tone.\n"
        "- Provide at least 3–5 well-developed bullet points for each of the four sections.\n"
        "- In each bullet, include concise evidence or reasoning drawn from the provided content.\n"
        "- Format the response in Markdown using the following structure:\n\n"
        "### Strengths\n"
        "- ...\n\n"
        "### Weaknesses\n"
        "- ...\n\n"
        "### Opportunities\n"
        "- ...\n\n"
        "### Threats\n"
        "- ...\n\n"
        "Ensure the content is thorough, clear, and suitable for presentation in a professional research report."
    )


    try:
        content = run_model_chat(
            prompt,
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            backend="openrouter"
        )
        file_path = get_company_file_path(company_name)
        append_section_to_file(file_path, "SWOT Analysis", content)
        logger.info("SWOT analysis generated.")
        return {**state, "swot_analysis": content}
    except Exception:
        logger.exception("Error generating SWOT analysis.")
        return {**state, "swot_analysis": "SWOT analysis could not be generated."}
