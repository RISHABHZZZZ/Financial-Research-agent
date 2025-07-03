# app/nodes/get_raw_data_from_multiple_sources.py

import os
import requests
from newspaper import Article
from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file

logger = setup_logger(__name__)

def get_raw_data_from_multiple_sources(state: dict) -> dict:
    company_name = state.get("company_name")
    combined_texts = []
    sources = []

    logger.info(f"Gathering web data for '{company_name}' via SerpAPI...")

    serpapi_key = os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        logger.error("SERPAPI_KEY not set in .env.")
        return {**state, "raw_company_text": "", "raw_sources": []}

    # 1️⃣ Query SerpAPI
    try:
        serpapi_url = "https://serpapi.com/search.json"
        params = {
            "q": f"{company_name} company profile latest financials",
            "engine": "google",
            "api_key": serpapi_key,
            "num": "7"
        }
        response = requests.get(serpapi_url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()

        organic_results = results.get("organic_results", [])
        logger.info(f"SerpAPI returned {len(organic_results)} results.")

        for result in organic_results:
            url = result.get("link")
            if not url:
                continue

            sources.append(url)
            logger.debug(f"Downloading: {url}")

            try:
                article = Article(url)
                article.download()
                article.parse()
                text = article.text

                if text and len(text) > 500:
                    combined_texts.append(f"## Article from {url}\n{text}")
                    logger.debug(f"Article length: {len(text)} characters")
                else:
                    logger.warning(f"Article from {url} too short, skipping.")
            except Exception as e:
                logger.warning(f"Failed to parse {url}: {e}")

    except Exception:
        logger.exception("SerpAPI request failed.")

    # Combine all text
    all_text = "\n\n".join(combined_texts) if combined_texts else "No web data retrieved."
    
    
    file_path = get_company_file_path(company_name)
    append_section_to_file(file_path, "Web Search Data", all_text)

    return {**state, "raw_company_text": all_text, "raw_sources": sources}
