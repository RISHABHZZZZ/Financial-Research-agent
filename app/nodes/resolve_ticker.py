# app/nodes/resolve_ticker.py

import os
import requests
from logging_config import setup_logger
from utils.file_helpers import get_company_file_path

logger = setup_logger(__name__)

def resolve_ticker(state: dict) -> dict:
    company_name = state.get("company_name")

    if not company_name:
        return {**state, "ticker": None}

    ticker = None

    # 🟢 Clear the output file at the start
    file_path = get_company_file_path(company_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Raw Data for {company_name}\n")

    # 1️⃣ Attempt Yahoo Finance search (or fallback)
    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {"q": company_name, "lang": "en-US", "region": "US"}

        logger.debug(f"Searching Yahoo Finance for ticker of '{company_name}'...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        quotes = data.get("quotes", [])
        for q in quotes:
            if q.get("quoteType") == "EQUITY":
                ticker = q.get("symbol")
                logger.info(f"Resolved ticker from Yahoo Finance: {ticker}")
                return {**state, "ticker": ticker}

        logger.warning("No equity tickers found in Yahoo Finance search.")

    except Exception as e:
        logger.exception("Yahoo Finance ticker lookup failed.")

    # 2️⃣ Fallback: Ask LLM
    if not ticker:
        logger.info("Attempting fallback: asking LLM for ticker.")

        ollama_url = os.getenv("OLLAMA_API_URL")
        if not ollama_url:
            logger.error("OLLAMA_API_URL not set.")
            return {**state, "ticker": None}

        prompt = (
            f"You are a financial analyst. Given the company name:\n\n"
            f"'{company_name}'\n\n"
            "Provide its primary stock ticker symbol (e.g., AAPL for Apple Inc.). "
            "Return ONLY the ticker symbol without explanation or formatting."
        )

        payload = {
            "model": "llama3:8b",
            "num_predict": 50,
            "stream": False,
            "messages": [
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content")
            if content:
                ticker_from_llm = content.strip().split()[0].upper()
                logger.info(f"Resolved ticker from LLM: {ticker_from_llm}")
                return {**state, "ticker": ticker_from_llm}
        except Exception:
            logger.exception("LLM ticker resolution failed.")

    # 3️⃣ Final fallback
    logger.warning("Ticker could not be resolved.")
    return {**state, "ticker": None}
