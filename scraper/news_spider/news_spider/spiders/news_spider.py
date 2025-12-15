import scrapy
from scrapy import Selector
from scraper.news_spider.news_spider.spiders.selenium_spider import fetch_dynamic_article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from newspaper import Article as NPArticle
import time
from urllib.parse import urljoin, urlparse
import re
import requests
import unicodedata
from datetime import datetime , timezone

from utils.nepali_date_parser import parse_nepali_date
from ..spider_config import SITE_CONFIGS as DEFAULT_SITE_CONFIGS, CUSTOM_SETTINGS


class NewsSpider(scrapy.Spider):
    name = "news_spider"
    MIN_CONTENT_LENGTH = 60
    # Website-specific configurations (imported)
    SITE_CONFIGS = DEFAULT_SITE_CONFIGS

    # Scrapy per-spider settings (imported)
    custom_settings = CUSTOM_SETTINGS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build start_urls from configs
        self.start_urls = []
        for site_config in self.SITE_CONFIGS.values():
            self.start_urls.extend(site_config["start_urls"])

        # Initialize Selenium driver (optional)
        self.driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=" + self.settings.get("USER_AGENT"))
            self.driver = webdriver.Chrome(options=chrome_options)
            try:
                self.driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
            except Exception:
                pass
        except Exception as e:
            self.logger.warning(f"Selenium driver not available: {e}")
            self.driver = None

    def get_site_config(self, url: str):
        for site_name, config in self.SITE_CONFIGS.items():
            if site_name in url or any(domain in url for domain in config.get("domains", [site_name])):
                return config
        return {
            "article_links": ['a[href*="/news/"]::attr(href)', 'article a::attr(href)'],
            "content_selectors": ["article p", ".content p", ".news-content p"],
            "title_selectors": ["h1::text", "title::text"],
            "image_selectors": ['meta[property="og:image"]::attr(content)', "article img::attr(src)"],
            "date_selectors": ['meta[property="article:published_time"]::attr(content)', "time::attr(datetime)"],
            "max_articles": 5,
        }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_with_selenium,
                errback=self.errback_handler,
                meta={"source": url, "site_config": self.get_site_config(url)},
            )

    def errback_handler(self, failure):
        url = getattr(failure.request, "url", "<unknown>")
        self.logger.warning(f"Request failed for {url}: {failure.value}")

    def parse_with_selenium(self, response):
        if response.status == 404:
            self.logger.warning(f"Page not found: {response.url}")
            return

        site_config = response.meta.get("site_config", {})
        self.logger.info(f"Fetching trending news from: {response.url}")

        if not self.driver:
            yield from self.parse_with_requests(response)
            return

        try:
            self.driver.get(response.url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            html = self.driver.page_source

            # IMPORTANT FIX
            response = response.replace(body=html)
            enhanced_response = response
            article_links = self.extract_article_links(enhanced_response, site_config)

            max_articles = site_config.get("max_articles", 100)

            self.logger.info(
                f"Found {len(article_links)} potential articles on {response.url}, taking {max_articles}"
            )

            for link in article_links[:max_articles]:
                yield scrapy.Request(
                    link,
                    callback=self.parse_article,
                    errback=self.errback_handler,
                    meta={"site_config": site_config},
                )
        except Exception as e:
            self.logger.error(f"Selenium failed for {response.url}: {e}")
            yield from self.parse_with_requests(response)

    def parse_with_requests(self, response):
        site_config = response.meta.get("site_config", {})
        article_links = self.extract_article_links(response, site_config)
        max_articles = site_config.get("max_articles", 5)

        for link in article_links[:max_articles]:
            yield scrapy.Request(
                link,
                callback=self.parse_article,
                errback=self.errback_handler,
                meta={"site_config": site_config},
            )

    def extract_article_links(self, response, site_config):
        links = set()

        for selector in site_config.get("article_links", []):
            links.update(response.css(selector).getall())

        links.update(response.css('a[href*="/news/"]::attr(href)').getall())
        links.update(response.css('a[href*="/story/"]::attr(href)').getall())
        links.update(response.css('a[href*="/article/"]::attr(href)').getall())

        full_links = []
        for link in links:
            if link and not self.should_exclude_link(link):
                full_url = urljoin(response.url, link)
                if self.is_article_url(full_url):
                    full_links.append(full_url)

        return list(set(full_links))[:15]

    def should_exclude_link(self, link):
        exclude_patterns = [
            "category/",
            "tag/",
            "author/",
            "page=",
            "comment",
            "/video/",
            "/gallery/",
            "#",
            "login",
            "register",
            "about",
            "contact",
            "privacy",
            "terms",
            "category/news",
        ]
        return any(p in link.lower() for p in exclude_patterns)

    def is_article_url(self, url):
        patterns = [
            r"/news/\d{4}/\d{2}/\d{2}/",
            r"/story/\d+",
            r"/detail/\d+",
            r"/article/\d+",
            r"-\d+\.html$",
            r"\.com/\d{4}/\d{2}/\d{2}/",
        ]
        return any(re.search(p, url) for p in patterns)

    def parse_article(self, response):
        if response.status != 200:
            return

        site_config = response.meta.get("site_config", {})

        if "ekantipur.com" in response.url or "nagariknetwork.com" in response.url:
            yield from self.parse_dynamic_article(response.url, site_config)
            return

        if not self.driver:
            yield from self.parse_article_fallback(response)
            return

        try:
            self.driver.get(response.url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
                or EC.presence_of_element_located((By.CSS_SELECTOR, ".content, .news-content, .entry-content"))
            )
            time.sleep(1)
            html = self.driver.page_source
            # IMPORTANT FIX (same as start page)
            response = response.replace(body=html)

            selector = Selector(text=html)

            yield from self.parse_article_content(selector, response.url, site_config)

        except Exception as e:
            self.logger.error(f"Selenium article parsing failed for {response.url}: {e}")
            yield from self.parse_article_fallback(response)

    def parse_article_fallback(self, response):
        if response.status != 200:
            return

        site_config = response.meta.get("site_config", {})
        yield from self.parse_article_content(response, response.url, site_config)

    def parse_dynamic_article(self, url, site_config):
        try:
            # Use your existing helper (fetch_dynamic_article)
            result = fetch_dynamic_article(url, self.get_source_name(url))

            if not result or not result.get("content"):
                self.logger.warning(f"No content fetched by fetch_dynamic_article for {url}")
                return

            title = result.get("title") or "No Title"
            content_text = result.get("content", "").strip()
            image_url = result.get("image")
            publish_date = result.get("published_at") or datetime.now(timezone.utc)

            if len(content_text) < self.MIN_CONTENT_LENGTH:
                self.logger.warning(f"Content too short for {url} ({len(content_text)} chars)")
                return

            yield self.make_item(
                title=title,
                url=url,
                content=content_text,
                summary=result.get("summary") or "",
                author=result.get("author"),
                published_at=publish_date,
                extras={
                    "image": image_url,
                    "thumbnail": image_url,
                    "source": self.get_source_name(url),
                    "method": "fetch_dynamic_article",
                },
            )

        except Exception as e:
            self.logger.error(f"fetch_dynamic_article failed for {url}: {e}")


    def extract_with_selectors(self, selector, selectors):
        for css_selector in selectors:
            result = selector.css(css_selector).get()
            if result and result.strip():
                return result.strip()
        return "No Title"

    def extract_content_with_selectors(self, selector, selectors):
        for css_selector in selectors:
            content_parts = selector.css(css_selector + "::text").getall()
            content = "\n".join([p.strip() for p in content_parts if p.strip()])
            if content and len(content) >= self.MIN_CONTENT_LENGTH:
                return content
        return ""

    def extract_ekantipur_content(self, selector):
        content_parts = selector.css(
            ".description p::text, .detail-content p::text, .news-detail p::text"
        ).getall()
        content = "\n".join([p.strip() for p in content_parts if p.strip()])
        return content

    

    def extract_publish_date(self, selector, site_config: dict, url: str | None = None) -> datetime | None:
        """
        Extract published date from a news article.

        Supports:
        - ISO 8601 / RFC 3339 (English)
        - Site-specific Nepali BS formats
        - Fallbacks to <meta>, <time>, or custom CSS selectors
        """

        # --- 1️⃣ Try meta tags (most reliable for structured news sites)
        meta_date = (
            selector.css('meta[property="article:published_time"]::attr(content)').get()
            or selector.css('meta[name="pubdate"]::attr(content)').get()
            or selector.css('meta[name="publishdate"]::attr(content)').get()
            or selector.css('meta[itemprop="datePublished"]::attr(content)').get()
        )

        if meta_date:
            meta_date = meta_date.strip()
            # (A) Try English ISO datetime
            parsed = self.try_parse_datetime(meta_date)
            if parsed:
                return parsed

            # (B) Try Nepali → AD conversion
            nep = parse_nepali_date(meta_date, url or "")
            if nep:
                return nep

        # --- 2️⃣ Try site-specific CSS selectors
        for selector_css in site_config.get("date_selectors", []):
            date_text = selector.css(selector_css).get()
            if not date_text:
                continue

            txt = date_text.strip()
            if not txt:
                continue

            # (A) English/ISO date formats
            parsed = self.try_parse_datetime(txt)
            if parsed:
                return parsed

            # (B) Nepali formats (e.g., "२०८२ कात्तिक २७ गते १०:५९")
            nep = parse_nepali_date(txt, url or "")
            if nep:
                return nep

        # --- 3️⃣ Check <time> tag
        time_tag = selector.css("time::attr(datetime)").get()
        if time_tag:
            time_tag = time_tag.strip()
            parsed = self.try_parse_datetime(time_tag)
            if parsed:
                return parsed

            nep = parse_nepali_date(time_tag, url or "")
            if nep:
                return nep

        # --- 4️⃣ Fallback: default to now (helps prevent DB null issues)
        return datetime.now(timezone.utc)


    def parse_article_content(self, selector, url, site_config):
        try:
            article = NPArticle(url)
            html_input = selector.get() if hasattr(selector, "get") else selector.text
            article.download(input_html=html_input)
            article.parse()

            title = self.extract_with_selectors(selector, site_config.get("title_selectors", []))
            if title == "No Title":
                title = article.title or "No Title"

            content_text = article.text.strip() if article.text else ""
            if len(content_text) < self.MIN_CONTENT_LENGTH:
                content_text = self.extract_content_with_selectors(
                    selector, site_config.get("content_selectors", [])
                )
            if len(content_text) < self.MIN_CONTENT_LENGTH:
                content_text = self.extract_text_from_html(selector, url)

            image_url = article.top_image or self.extract_image_url(selector, url, site_config)
            publish_date = article.publish_date or self.extract_publish_date(selector, site_config)

            if content_text and len(content_text) >= self.MIN_CONTENT_LENGTH:
                yield self.make_item(
                    title=title,
                    url=url,
                    content=content_text,
                    summary=getattr(article, "summary", "") or "",
                    author=(article.authors[0] if getattr(article, "authors", []) else None),
                    published_at=publish_date,
                    extras={
                        "image": image_url,
                        "thumbnail": image_url,
                        "source": self.get_source_name(url),
                        "method": "newspaper3k+site_specific",
                    },
                )
            else:
                self.logger.warning(f"Insufficient content for {url}")
        except Exception as e:
            self.logger.error(f"Content parsing failed for {url}: {e}")

    def extract_text_from_html(self, selector, url):
        texts = selector.css("p::text").getall()
        content = "\n".join([self.clean_text(t) for t in texts if len(t.strip()) > 20])
        return content

    def extract_image_url(self, selector, base_url, site_config):
        candidates = []

        for img_selector in site_config.get("image_selectors", []):
            candidates.extend(selector.css(img_selector).getall())

        candidates.extend(
            [
                selector.css('meta[property="og:image"]::attr(content)').get(),
                selector.css("article img::attr(src)").get(),
                selector.css(".featured-image img::attr(src)").get(),
                selector.css(".news-image img::attr(src)").get(),
            ]
        )

        for src in candidates:
            if src and not src.endswith(".svg") and "logo" not in src.lower():
                full_url = urljoin(base_url, src.strip())
                if self.is_valid_image_url(full_url):
                    return full_url
        return ""

    def is_valid_image_url(self, url):
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        return any(url.lower().endswith(ext) for ext in image_extensions)

    def get_source_name(self, url):
        domain_map = {
            "ekantipur.com": "Kantipur",
            "annapurnapost.com": "Annapurna Post",
            "ratopati.com": "Ratopati",
            "setopati.com": "Setopati",
            "onlinekhabar.com": "Online Khabar",
            "nagariknetwork.com": "Nagarik News",
            "nayapatrikadaily.com": "Naya Patrika",
            "gorkhapatraonline.com": "Gorkhapatra",
            "newsofnepal.com": "News of Nepal",
            "osnepal.com": "OS Nepal",
            "rajdhanidaily.com": "Rajdhani Daily",
            "lokantar.com": "Lokantar",
            "souryaonline.com": "Sourya Online",
            "ujyaaloonline.com": "Ujyaalo Online",
            "nepalaaja.com": "Nepal Aaja",
        }
        domain = self.get_domain(url)
        return domain_map.get(domain, domain)

    def get_domain(self, url):
        domain = urlparse(url).netloc
        return domain.replace("www.", "")

    def clean_text(self, text):
        if not text:
            return ""
        text = unicodedata.normalize("NFKC", text)
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned

    def try_parse_datetime(self, value: str):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    def make_item(self, title, url, content, summary, author, published_at, extras=None):
        item = {
            "title": self.clean_text(title),
            "url": url,
            "summary": summary or "",
            "content": content or None,
            "author": author,
            "published_at": published_at,
        }
        if extras and isinstance(extras, dict):
            item.update(extras)
            thumb = extras.get("thumbnail") or extras.get("image")
            if thumb:
                item["thumbnail"] = thumb
        return item

    def closed(self, reason):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Chrome driver closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
