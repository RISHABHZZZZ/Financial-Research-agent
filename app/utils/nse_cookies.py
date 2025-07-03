import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

def get_nse_cookies():
    options = Options()
    options.binary_location = r"C:/Users/Rishabh/Downloads/chrome-win64/chrome-win64/chrome.exe"
    # Comment out headless to see the browser visibly
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = ChromeService(
        executable_path=r"C:/Users/Rishabh/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
    )

    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.nseindia.com")

    # Wait to let the page load and cookies get set
    time.sleep(8)

    # Collect cookies
    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}

    # Get user agent
    user_agent = driver.execute_script("return navigator.userAgent;")

    driver.quit()

    return cookies, user_agent

# Example usage
if __name__ == "__main__":
    cookies, ua = get_nse_cookies()
    print("✅ User Agent:", ua)
    print("✅ Cookies:", cookies)
