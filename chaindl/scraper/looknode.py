from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver

import pandas as pd

import json
import time

INVALID_LINKS = ["BTCPrice", "getUserInfo", "chartInfo"]
API_URL = "https://www.looknode.com/api/"

def _download(url, **kwargs):
    data_json = _intercept_network_requests(url, **kwargs)

    data = data_json.get("data", [])

    processed_data = []
    for entry in data:
        date = pd.to_datetime(entry["t"], unit="ms").normalize()

        values = {}
        for key, value in entry.items():
            if key == "t":
                continue
            if key == "v":
                values["v1"] = value
            elif key.startswith("v") and key[1:].isdigit():
                values[key] = value

        row = {"Date": date}
        row.update(values)
        processed_data.append(row)

    df = pd.DataFrame(processed_data)

    if not df.empty:
        df = df.set_index("Date")
        
        v_columns = sorted(
            [col for col in df.columns if col.startswith("v")],
            key=lambda x: int(x[1:]) if x[1:].isdigit() else 0
        )

        df = df[v_columns]

    return df

def _check_validity(url):
    if not url.startswith(API_URL):
        return False
    
    info = url.replace(API_URL, "")
    
    for link in INVALID_LINKS:
        if link in info:
            return False
        
    return True

def _intercept_network_requests(url, check_interval=0.5, timeout=30):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for compatibility
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    start_time = time.time()
    request = None

    while time.time() - start_time < timeout:
        for req in driver.requests:
            if _check_validity(req.url) and req.response:
                request = req
                break
        if request:
            break
        time.sleep(check_interval)

    if request:
        body = request.response.body
        driver.quit()
        
        return json.loads(body)
    else:
        driver.quit()
        raise TimeoutError(f"Could not find the request within {timeout} seconds. Try increasing the timeout!")