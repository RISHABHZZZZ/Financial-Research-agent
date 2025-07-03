# app/utils/file_helpers.py

import os

def get_company_file_path(company_name: str, folder="data") -> str:
    """
    Generates a consistent file path for storing raw data for a company.
    """
    safe_name = company_name.replace(" ", "_")
    if not os.path.exists(folder):
        os.makedirs(folder)
    return os.path.join(folder, f"{safe_name}_raw.txt")

def append_section_to_file(file_path: str, section_title: str, content: str):
    """
    Appends a section with a title and content to the specified file.
    """
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n## {section_title}\n")
        f.write(content.strip())
