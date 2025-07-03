# app/test_env.py

import os
from dotenv import load_dotenv

load_dotenv()

print("NEWS_API_KEY =", os.getenv("NEWS_API_KEY"))
