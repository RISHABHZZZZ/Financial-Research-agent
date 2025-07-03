# app/nodes/get_financials.py

import os
import requests
import yfinance as yf
from logging_config import setup_logger
from utils.nse_cookies import get_nse_cookies
from utils.file_helpers import get_company_file_path, append_section_to_file

logger = setup_logger(__name__)

def fetch_nse_quote(ticker):
    # Get fresh cookies and user-agent
    cookies, user_agent = get_nse_cookies()

    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json",
        "Referer": f"https://www.nseindia.com/get-quotes/equity?symbol={ticker}",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    url = f"https://www.nseindia.com/api/quote-equity?symbol={ticker}"
    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    response.raise_for_status()
    return response.json()

def get_financials(state: dict) -> dict:
    """
    Node to fetch enriched financial data.
    For Indian tickers, uses NSE API with Selenium.
    For others, falls back to FMP, Alpha Vantage, and yfinance.
    """
    company_name = state.get("company_name")
    ticker = state.get("ticker")
    region = state.get("region", "IN")
    
    if not ticker:
        logger.error("No ticker available to retrieve financials.")
        return {"company_name": company_name, "ticker": ticker, "financials": "Ticker not resolved. Cannot retrieve financials."}

    logger.info(f"Fetching financials for: {ticker}")

    logger.info(f"Starting get_financials for: {company_name} (Ticker: {ticker}, Region: {region})")

    financials = {}
    sources_used = []

    if region == "IN":
        # 1️⃣ NSE API via Selenium
        try:
            logger.debug("Attempting NSE direct API retrieval with Selenium...")

            cookies_dict, user_agent = get_nse_cookies()

            headers = {
                "User-Agent": user_agent,
                "Accept": "application/json",
                "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=" + ticker,
            }

            session = requests.Session()
            session.headers.update(headers)
            jar = requests.cookies.RequestsCookieJar()
            for k, v in cookies_dict.items():
                jar.set(k, v)
            session.cookies = jar

            url = f"https://www.nseindia.com/api/quote-equity?symbol={ticker}"
            response = session.get(url, timeout=15)
            response.raise_for_status()
            nse_data = response.json()

            price_info = nse_data.get("priceInfo", {})
            metadata = nse_data.get("metadata", {})
            security_info = nse_data.get("securityInfo", {})
            industry_info = nse_data.get("industryInfo", {})

            # Extract everything meaningful
            financials.update({
                "Last Traded Price": f"₹{price_info.get('lastPrice')}",
                "Change (%)": f"{price_info.get('pChange', 0):.2f}%",
                "Previous Close": f"₹{price_info.get('previousClose')}",
                "Day High": f"₹{price_info.get('intraDayHighLow', {}).get('max')}",
                "Day Low": f"₹{price_info.get('intraDayHighLow', {}).get('min')}",
                "52 Week High": f"₹{price_info.get('weekHighLow', {}).get('max')}",
                "52 Week Low": f"₹{price_info.get('weekHighLow', {}).get('min')}",
                "P/E Ratio": metadata.get("pdSymbolPe"),
                "Face Value": f"₹{security_info.get('faceValue')}",
                "Industry": metadata.get("industry"),
                "Sector": industry_info.get("sector"),
                "ISIN": metadata.get("isin"),
                "Market Cap": metadata.get("marketCap")
            })

            sources_used.append("NSE API")
            logger.info("NSE data retrieved successfully.")

        except Exception as e:
            logger.exception("NSE retrieval failed.")

        # 2️⃣ yfinance fallback
        try:
            logger.debug("Attempting yfinance retrieval (.NS)...")
            yf_ticker = yf.Ticker(ticker if ".NS" in ticker else ticker + ".NS")
            info = yf_ticker.info

            if not financials.get("Market Cap") and info.get("marketCap"):
                financials["Market Cap"] = info.get("marketCap")
            if info.get("trailingPE"):
                financials["P/E Ratio"] = info.get("trailingPE")
            if info.get("dividendYield") is not None:
                dy = info.get("dividendYield")
                financials["Dividend Yield"] = f"{dy * 100:.2f}%" if dy < 1 else f"{dy:.2f}%"
            if info.get("totalRevenue"):
                financials["Revenue"] = info.get("totalRevenue")
            if info.get("netIncomeToCommon"):
                financials["Net Income"] = info.get("netIncomeToCommon")

            sources_used.append("yfinance")
            logger.info("yfinance .NS data retrieved successfully.")
        except Exception as e:
            logger.exception("yfinance retrieval failed.")

    else:
        # 🌍 Non-India fallback
        ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
        FMP_API_KEY = os.getenv("FMP_API_KEY")

        # FMP
        try:
            logger.debug("Attempting Financial Modeling Prep...")
            url_fmp = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
            response = requests.get(url_fmp, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    profile = data[0]
                    financials["Market Cap"] = profile.get("mktCap")
                    financials["P/E Ratio"] = profile.get("pe")
                    financials["Dividend Yield"] = profile.get("lastDiv")
                    financials["52 Week High"] = profile.get("range")
                    sources_used.append("FMP")
                    logger.info("FMP data retrieved successfully.")
        except Exception as e:
            logger.exception("FMP retrieval failed.")

        # Alpha Vantage
        missing = [k for k in ["Market Cap", "P/E Ratio"] if not financials.get(k)]
        if missing:
            try:
                logger.debug("Attempting Alpha Vantage...")
                url_av = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
                response = requests.get(url_av, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data and "MarketCapitalization" in data:
                        if "Market Cap" in missing:
                            financials["Market Cap"] = data.get("MarketCapitalization")
                        if "P/E Ratio" in missing:
                            financials["P/E Ratio"] = data.get("PERatio")
                        financials["Revenue"] = data.get("RevenueTTM")
                        financials["Net Income"] = data.get("NetIncomeTTM")
                        sources_used.append("Alpha Vantage")
                        logger.info("Alpha Vantage data retrieved.")
            except Exception as e:
                logger.exception("Alpha Vantage retrieval failed.")

    # Format numbers
    formatted = {}
    for k, v in financials.items():
        if v is None:
            continue
        try:
            if isinstance(v, (int, float)):
                if "₹" in k or "Price" in k or "High" in k or "Low" in k:
                    formatted[k] = f"₹{v:,.2f}"
                elif any(term in k for term in ["Market Cap", "Revenue", "Income"]):
                    formatted[k] = f"${v:,.0f}"
                else:
                    formatted[k] = str(v)
            else:
                formatted[k] = str(v)
        except Exception:
            formatted[k] = str(v)

    if not formatted:
        logger.error("All data sources failed.")
        return {"financials": "Financial data could not be retrieved."}

    logger.debug(f"Final formatted financials: {formatted}")
    
    file_path = get_company_file_path(company_name)
    fin_lines = "\n".join(f"- {k}: {v}" for k, v in formatted.items())
    append_section_to_file(file_path, "Financial Data", fin_lines)
    
    return {**state, "financials": formatted}
