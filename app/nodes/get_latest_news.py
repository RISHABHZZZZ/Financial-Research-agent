# app/nodes/get_latest_news.py

import os
import requests
from datetime import datetime, timedelta
from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger(__name__)

def get_latest_news(state: dict) -> dict:
    company_name = state.get("company_name")
    region = state.get("region", "IN")

    logger.info(f"Starting get_latest_news for: {company_name}")

    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if not NEWS_API_KEY:
        logger.error("NEWS_API_KEY not set in environment.")
        return {**state, "latest_news": "API key not configured."}

    url = "https://newsapi.org/v2/everything"

    # Date filter (last 30 days)
    from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    params = {
        "qInTitle": company_name,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY,
    }

    logger.debug(f"Requesting NewsAPI with params: {params}")

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "articles" not in data or not data["articles"]:
            logger.warning("No articles found.")
            news_text = "No recent news articles found for this company."
        else:
            # Extract clean summaries
            articles = []
            for item in data["articles"]:
                title = item.get("title")
                url = item.get("url")
                published_at = item.get("publishedAt", "")[:10]
                articles.append(f"- **{title}** ({published_at})\n  {url}")

            news_text = "\n\n".join(articles)

        # Save to file
        file_path = get_company_file_path(company_name)
        append_section_to_file(file_path, "Latest News", news_text)

        return {**state, "latest_news": news_text}

    except Exception as e:
        logger.exception("Error retrieving latest news.")
        file_path = get_company_file_path(company_name)
        append_section_to_file(file_path, "Latest News", "Error retrieving news.")
        return {**state, "latest_news": "Error retrieving news."}
