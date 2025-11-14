# app/utils/selenium_fetcher.py

import time
import psutil
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.nepali_date_parser import parse_nepali_date


# ---------------------------------------------------
# KILL ZOMBIE CHROME / CHROMEDRIVER PROCESSES
# ---------------------------------------------------
def kill_zombies():
    """Kill leftover Chrome and Chromedriver processes."""
    for proc in psutil.process_iter(["name"]):
        name = proc.info.get("name", "").lower()
        if "chromedriver" in name or "chrome" in name or "chromium" in name:
            try:
                proc.kill()
            except Exception:
                pass


# ---------------------------------------------------
# EKANTIPUR MODAL HANDLER
# ---------------------------------------------------
def close_ekantipur_modal(driver):
    """Close the Kantipur roadblock modal if present."""
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "roadblock-ad"))
        )
        close_button = driver.find_element(By.CSS_SELECTOR, "#roadblock-ad .icon-close")
        driver.execute_script("arguments[0].click();", close_button)
        time.sleep(0.5)
        return True
    except Exception:
        return False


# ---------------------------------------------------
# MAIN ARTICLE FETCHER
# ---------------------------------------------------
def fetch_dynamic_article(url: str, source: str) -> dict:
    """Fetch article content from dynamic JS-based sites like Kantipur & Nagarik."""

    # -------------------------------
    # Chrome Options
    # -------------------------------
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Prevent zombie Chrome debugging processes
    options.add_argument("--remote-debugging-port=0")

    # Ensures Chrome closes when Selenium session ends
    options.add_experimental_option("detach", False)

    service = Service()  # Selenium 4+ recommended

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(2)  # let JS load

        # Close Kantipur modal
        close_ekantipur_modal(driver)

        # Scroll bottom to trigger lazy load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        html = driver.page_source

    finally:
        # Robust shutdown
        try:
            driver.close()
        except Exception:
            pass

        try:
            driver.quit()
        except Exception:
            pass

        # Kill any zombies leftover
        kill_zombies()

    # -------------------------------
    # Parse HTML
    # -------------------------------
    soup = BeautifulSoup(html, "lxml")

    # Title
    title_el = soup.select_one("h1.title, h1.article-title, h1.post-title, h1")
    title = title_el.get_text(strip=True) if title_el else None

    # Remove scripts and ads
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    for ad in soup.select(".ekans-wrapper, .ekans-row, .ads, .advertisement, #roadblock-ad"):
        ad.decompose()

    # Content Selectors
    content_selectors = [
        "div.description p",
        "div.article-content p",
        "div.article-content-wrapper p",
        "div.current-news-block p",
        "article p",
        ".story p",
    ]

    content = None
    for selector in content_selectors:
        found = soup.select(selector)
        if found:
            content = " ".join(p.get_text(strip=True) for p in found)
            break

    # Main Image
    image = soup.select_one(
        "figure img, .featured-image img, .article-image img, .image img"
    )
    image_url = image.get("src") if image else None

    # Author
    author_el = soup.select_one(".author-name, .post-meta__author, .author")
    author = author_el.get_text(strip=True) if author_el else None

    # Published Date
    date_el = soup.select_one(
        ".published-at, .post-meta__date, .published-date, .post-date, time"
    )
    date_text = date_el.get_text(strip=True) if date_el else ""
    published_at = parse_nepali_date(date_text, url) or datetime.now(timezone.utc)

    # Return clean structured data
    return {
        "title": title,
        "url": url,
        "content": content,
        "image": image_url,
        "author": author,
        "published_at": published_at,
        "source": source,
        "method": "selenium",
    }
