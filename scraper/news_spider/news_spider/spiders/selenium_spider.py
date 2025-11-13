# app/utils/selenium_fetcher.py

import time
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.nepali_date_parser import parse_nepali_date


def close_ekantipur_modal(driver):
    """Close the Kantipur roadblock modal if present."""
    try:
        # Wait for modal div
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "roadblock-ad"))
        )

        # Try clicking the close button (icon-close)
        close_button = driver.find_element(By.CSS_SELECTOR, "#roadblock-ad .icon-close")
        driver.execute_script("arguments[0].click();", close_button)
        time.sleep(0.5)
        return True

    except Exception:
        # Modal not found or not closable
        return False


def fetch_dynamic_article(url: str, source: str) -> dict:
    """Fetch article content from dynamic JS-based sites like Kantipur & Nagarik."""

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(2)  # Let JS run

        # ⛔ Close modal if visible
        close_ekantipur_modal(driver)

        # Scroll to bottom to load full lazy content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        html = driver.page_source

    finally:
        driver.quit()

    soup = BeautifulSoup(html, "lxml")

    # -------------------------------
    # Extract Article Title
    # -------------------------------
    title = soup.select_one("h1.title, h1.article-title, h1.post-title, h1")
    title = title.get_text(strip=True) if title else None

    # -------------------------------
    # Clean unnecessary tags
    # -------------------------------
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    for ad in soup.select(
        ".ekans-wrapper, .ekans-row, .ads, .advertisement, #roadblock-ad"
    ):
        ad.decompose()

    # -------------------------------
    # Extract article content
    # -------------------------------
    content_selectors = [
        "div.description p",
        "div.article-content p",
        "div.article-content-wrapper p",
        "div.current-news-block p",
        "article p",
        ".story p",
    ]

    content_elements = []
    for selector in content_selectors:
        found = soup.select(selector)
        if found:
            content_elements = found
            break

    content = (
        " ".join(p.get_text(strip=True) for p in content_elements)
        if content_elements
        else None
    )

    # -------------------------------
    # Extract Main Image
    # -------------------------------
    image = soup.select_one(
        "figure img, .featured-image img, .article-image img, .image img"
    )
    image_url = image["src"] if image and image.has_attr("src") else None

    # -------------------------------
    # Author
    # -------------------------------
    author_el = soup.select_one(".author-name, .post-meta__author, .author")
    author = author_el.get_text(strip=True) if author_el else None

    # -------------------------------
    # Published Date
    # -------------------------------
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
