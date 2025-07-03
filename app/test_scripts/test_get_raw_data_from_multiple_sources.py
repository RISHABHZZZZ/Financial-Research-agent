# app/test_get_raw_data_from_multiple_sources.py

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

from nodes.get_raw_data_from_multiple_sources import get_raw_data_from_multiple_sources

def main():
    # Define the input state
    state = {
        "company_name": "Deloitte"
    }

    print("✅ Starting test of get_raw_data_from_multiple_sources with company: Deloitte...")

    # Call the node
    result = get_raw_data_from_multiple_sources(state)

    # Retrieve results
    raw_text = result.get("raw_company_text", "")
    raw_sources = result.get("raw_sources", [])

    # Output summary
    print("\n✅ Test Completed.")
    print(f"\nNumber of characters retrieved: {len(raw_text)}")
    print(f"Number of sources retrieved: {len(raw_sources)}")
    
    print("\nSources List:")
    for url in raw_sources:
        print(f"- {url}")

    # Show preview
    preview_len = min(2000, len(raw_text))
    print("\n--- Start of Retrieved Text Preview ---\n")
    print(raw_text[:preview_len])
    if len(raw_text) > preview_len:
        print("\n... [TRUNCATED]")
    print("\n--- End of Preview ---")

if __name__ == "__main__":
    main()
