# app/utils/load_environment.py

from dotenv import load_dotenv
import os

def ensure_environment():
    loaded = load_dotenv()
    if not loaded:
        raise RuntimeError("Could not load .env file. Make sure it exists in project root.")

    # Debug print to confirm loading
    print(f"✅ Loaded .env")
    print(f"✅ OLLAMA_API_URL = {os.getenv('OLLAMA_API_URL')}")
