"""
Shared configuration for the news spider.

Exposes:
- SITE_CONFIGS: per-site scraping selectors and limits
- CUSTOM_SETTINGS: per-spider Scrapy settings
"""

SITE_CONFIGS = {
    "ekantipur": {
        "start_urls": ["https://ekantipur.com/news"],
        "article_links": [
            "article a::attr(href)",
            ".teaser a::attr(href)",
            ".news-title a::attr(href)",
        ],
        "content_selectors": [
            ".description p",
            ".detail-content p",
            ".news-detail p"
        ],
        "title_selectors": ["h1::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".article-image img::attr(src)",
            ".detail-image img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".published-date span::text",
            ".post-byline span::text",
            ".date::text",
            "time::attr(datetime)",
        ],
        "max_articles": 10
    },
    "annapurnapost": {
        "start_urls": ["https://annapurnapost.com/category/latest-news"],
        "article_links": [
            ".grid__card a::attr(href)",
            "h3 a::attr(href)",
            ".news-list a::attr(href)",
        ],
        "content_selectors": [
            ".news-details p",
            ".description p",
            ".content p"
        ],
        "title_selectors": ["h1::text", ".news-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".featured-image img::attr(src)",
            ".news-image img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".publish-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 8
    },
    "ratopati": {
        "start_urls": ["https://www.ratopati.com/category/main-news"],
        "article_links": [
            ".news-item a::attr(href)",
            ".post-title a::attr(href)",
            "article a::attr(href)",
        ],
        "content_selectors": [
            ".news-content p",
            ".detail-news p",
            ".entry-content p"
        ],
        "title_selectors": [
            ".news-title h1::text",
            ".post-title h1::text",
            ".detail-title::text",
            "h1.news-title::text",
            "h1.post-title::text",
        ],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".news-image img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".post-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 8
    },
    "setopati": {
        "start_urls": ["https://www.setopati.com/politics"],
        "article_links": [
            "h2.title a::attr(href)",
            ".list__item a::attr(href)",
            ".news-list a::attr(href)",
        ],
        "content_selectors": [
            ".news-details p",
            ".description p",
            ".content p"
        ],
        "title_selectors": ["h1::text", ".news-headline::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".featured-image img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".published-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 8
    },
    "onlinekhabar": {
        "start_urls": ["https://www.onlinekhabar.com/content/news"],
        "article_links": [
            ".ok-news-post a::attr(href)",
            ".post__title a::attr(href)",
            ".news-list a::attr(href)",
        ],
        "content_selectors": [
            ".news-details p",
            ".description p",
            ".main__content p"
        ],
        "title_selectors": ["h1::text", ".news-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".featured-image img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".article-posted-date::text",
            ".article-posted-date img::attr(alt)",
            "time::attr(datetime)"
        ],
        "max_articles": 10
    },
    "nagariknews": {
        "start_urls": ["https://nagariknews.nagariknetwork.com"],
        "article_links": [
            ".news-list a::attr(href)",
            "article a::attr(href)",
            ".title a::attr(href)",
        ],
        "content_selectors": [
            ".news-content p",
            ".detail-content p",
            ".article-content p"
        ],
        "title_selectors": ["h1::text", ".news-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".news-image img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".publish-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 8
    },
    "nayapatrika": {
        "start_urls": ["https://nayapatrikadaily.com/news"],
        "article_links": [
            ".news-item a::attr(href)",
            ".title a::attr(href)",
            "article a::attr(href)",
        ],
        "content_selectors": [
            ".news-details p",
            ".content p",
            ".article-content p"
        ],
        "title_selectors": ["h1::text", ".news-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".featured-image img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".post-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 6
    },
    "newsofnepal": {
        "start_urls": ["https://newsofnepal.com/category/news"],
        "article_links": [
            ".news-item a::attr(href)",
            ".post-title a::attr(href)",
            "article a::attr(href)",
        ],
        "content_selectors": [
            ".entry-content p",
            ".news-content p",
            ".post-content p"
        ],
        "title_selectors": ["h1::text", ".entry-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".post-thumbnail img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".post-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 5
    },
    "osnepal": {
        "start_urls": ["https://osnepal.com/category/news"],
        "article_links": [
            ".news-item a::attr(href)",
            ".entry-title a::attr(href)",
            "article a::attr(href)",
        ],
        "content_selectors": [
            ".entry-content p",
            ".news-content p",
            ".post-content p"
        ],
        "title_selectors": ["h1::text", ".entry-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".post-image img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".posted-on::text",
            "time::attr(datetime)"
        ],
        "max_articles": 5
    },
    "rajdhanidaily": {
        "start_urls": ["https://rajdhanidaily.com/category/news"],
        "article_links": [
            ".news-list a::attr(href)",
            ".post-title a::attr(href)",
            "article a::attr(href)",
        ],
        "content_selectors": [
            ".entry-content p",
            ".news-content p",
            ".post-content p"
        ],
        "title_selectors": ["h1::text", ".entry-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".post-thumbnail img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".post-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 5
    },
    "lokantar": {
        "start_urls": ["https://lokantar.com/category/news"],
        "article_links": [
            ".news-item a::attr(href)",
            ".entry-title a::attr(href)",
            "article a::attr(href)",
        ],
        "content_selectors": [
            ".entry-content p",
            ".news-content p",
            ".post-content p"
        ],
        "title_selectors": ["h1::text", ".entry-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".post-thumbnail img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".post-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 5
    },
    "souryaonline": {
        "start_urls": ["https://souryaonline.com/category/news"],
        "article_links": [
            ".news-list a::attr(href)",
            ".post-title a::attr(href)",
            "article a::attr(href)",
        ],
        "content_selectors": [
            ".entry-content p",
            ".news-content p",
            ".post-content p"
        ],
        "title_selectors": ["h1::text", ".entry-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".post-image img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".post-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 5
    },
    "ujyaaloonline": {
        "start_urls": ["https://ujyaaloonline.com/news"],
        "article_links": [
            ".news-item a::attr(href)",
            ".title a::attr(href)",
            "article a::attr(href)",
        ],
        "content_selectors": [
            ".news-details p",
            ".content p",
            ".article-content p"
        ],
        "title_selectors": ["h1::text", ".news-title::text"],
        "image_selectors": [
            'meta[property="og:image"]::attr(content)',
            ".featured-image img::attr(src)",
            "article img::attr(src)"
        ],
        "date_selectors": [
            'meta[property="article:published_time"]::attr(content)',
            ".post-date::text",
            "time::attr(datetime)"
        ],
        "max_articles": 5
    },
}


CUSTOM_SETTINGS = {
    "FEEDS": {
        "trending_news.json": {
            "format": "json",
            "encoding": "utf8",
            "indent": 4,
        }
    },
    "LOG_LEVEL": "INFO",
    "ROBOTSTXT_OBEY": False,
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "DOWNLOAD_DELAY": 1,
    "CONCURRENT_REQUESTS": 2,
    "AUTOTHROTTLE_ENABLED": True,
    "RETRY_TIMES": 2,
    "HTTPERROR_ALLOWED_CODES": [404, 403, 500],
    "HTTPERROR_ALLOW_ALL": True,
}

