# app/utils/model_client.py

import os
import requests
from dotenv import load_dotenv
load_dotenv()

# Load your API key from .env
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_API_URL")

def run_model_chat(
    prompt: str,
    model: str,
    backend: str = "openrouter",
    temperature: float = 0.7,
    max_tokens: int = 4096
) -> str:
    """
    Unified LLM helper.
    backend = 'openrouter' or 'ollama'
    """
    if backend == "openrouter":
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENAI_API_KEY (OpenRouter) is missing.")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            # Optionally, you can add referer and title:
            # "HTTP-Referer": "http://localhost:8501",
            # "X-Title": "YourAppName"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful financial analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    elif backend == "ollama":
        if not OLLAMA_URL:
            raise ValueError("OLLAMA_API_URL not configured.")
        payload = {
            "model": model,
            "stream": False,
            "num_predict": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": "You are a helpful financial analyst."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "").strip()

    else:
        raise ValueError("Invalid backend specified. Use 'openrouter' or 'ollama'.")


print("OPENAI_API_KEY loaded:", bool(OPENROUTER_API_KEY))
