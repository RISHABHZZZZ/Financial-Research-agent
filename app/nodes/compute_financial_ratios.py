# app/nodes/compute_financial_ratios.py

from logging_config import setup_logger
from utils.file_helpers import get_company_file_path, append_section_to_file

logger = setup_logger(__name__)

def compute_financial_ratios(state: dict) -> dict:
    company_name = state.get("company_name")
    financials = state.get("financials", {})
    ratios = {}

    logger.info("Computing financial ratios...")

    try:
        # Convert fields to float safely
        def safe_float(value):
            if value is None or value == "N/A":
                return 0.0
            if isinstance(value, str):
                value = value.replace("$", "").replace(",", "").strip()
            try:
                return float(value)
            except Exception:
                return 0.0

        revenue = safe_float(financials.get("Revenue"))
        net_income = safe_float(financials.get("Net Income"))
        market_cap = safe_float(financials.get("Market Cap"))
        pe_ratio = safe_float(financials.get("P/E Ratio"))
        total_assets = safe_float(financials.get("Total Assets"))
        total_liabilities = safe_float(financials.get("Total Liabilities"))

        # Net Margin
        if revenue > 0 and net_income > 0:
            ratios["Net Margin"] = f"{(net_income / revenue) * 100:.2f}%"
        else:
            ratios["Net Margin"] = "N/A"

        # Debt to Assets
        if total_assets > 0 and total_liabilities > 0:
            ratios["Debt to Assets"] = f"{(total_liabilities / total_assets) * 100:.2f}%"
        else:
            ratios["Debt to Assets"] = "N/A"

        # P/E Ratio
        ratios["P/E Ratio"] = f"{pe_ratio:.2f}" if pe_ratio > 0 else "N/A"

        logger.debug(f"Computed ratios: {ratios}")

    except Exception:
        logger.exception("Error computing financial ratios.")

    # Append to the company raw data file
    file_path = get_company_file_path(company_name)
    ratio_lines = "\n".join(f"- {k}: {v}" for k, v in ratios.items())
    append_section_to_file(file_path, "Financial Ratios", ratio_lines)

    return {**state, "financial_ratios": ratios}
