import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# CI ortamını basitçe tespit et
CI_ENV = os.getenv("CI", "").lower() in ("1", "true", "yes")

# Base URL ortam değişkeniyle değiştirilebilir
BASE_URL = os.getenv("BASE_URL", "https://skin.dracofusion.com/")

def open_browser():
    """Chrome WebDriver açar ve BASE_URL'e gider."""
    options = Options()
    options.add_argument("--window-size=1920,1080")
    # CI'da headless ve gerekli flag'ler
    if CI_ENV:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    driver.set_page_load_timeout(60)
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 20)
    return driver, wait
