from app.utils.nse_cookies import get_nse_cookies
import requests

def fetch_nse_quote(ticker):
    # Get fresh cookies and user-agent each time
    cookies, user_agent = get_nse_cookies()

    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=" + ticker,
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    url = f"https://www.nseindia.com/api/quote-equity?symbol={ticker}"

    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    response.raise_for_status()
    return response.json()

