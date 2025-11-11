import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
import time
import threading

# Load .env if present
load_dotenv()


SUMMARY_PROMPT_TEMPLATE = """
You are a multilingual summarization model.

Summarize the following article clearly and concisely in the same language as the input.
If the text is in Nepali, return the summary in Nepali.
Keep the summary factual, neutral, and about 1 sentences long.

Article:
{article}
"""


_gemini_client = None
_rate_limiter = None


class _RateLimiter:
    def __init__(self, per_minute: int, per_day: int, wait: bool = True):
        self.per_minute = max(1, int(per_minute))
        self.per_day = max(1, int(per_day))
        self.wait = wait
        self._lock = threading.Lock()
        # Token bucket for minute limit
        self._tokens = float(self.per_minute)
        self._last_refill = time.time()
        self._rate_per_sec = self.per_minute / 60.0
        # Daily counter
        self._day_key = time.strftime("%Y-%m-%d", time.gmtime())
        self._day_count = 0

    def _refill(self, now: float):
        elapsed = max(0.0, now - self._last_refill)
        if elapsed > 0:
            self._tokens = min(self.per_minute, self._tokens + elapsed * self._rate_per_sec)
            self._last_refill = now

    def _check_rollover(self):
        today = time.strftime("%Y-%m-%d", time.gmtime())
        if today != self._day_key:
            self._day_key = today
            self._day_count = 0

    def acquire(self) -> bool:
        while True:
            with self._lock:
                self._check_rollover()
                if self._day_count >= self.per_day:
                    return False
                now = time.time()
                self._refill(now)
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    self._day_count += 1
                    return True
                # Need to wait for next token
                if not self.wait:
                    return False
                # Compute sleep time for next token
                needed = (1.0 - self._tokens) / self._rate_per_sec if self._rate_per_sec > 0 else 1.0
            # Sleep outside lock
            time.sleep(max(0.05, needed))


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    from google import genai  # lazy import
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


async def generate_summary(article: str, model: str = "gemini-2.0-flash") -> str:
    """
    Generate a concise summary of a given article using Google Gemini.
    Returns a clean text summary in the same language as the input.
    """
    if not (article or "").strip():
        return ""
    try:
        # Rate limiting
        global _rate_limiter
        if _rate_limiter is None:
            minute_limit = int(os.getenv("SUMMARY_MINUTE_LIMIT", "15"))
            daily_limit = int(os.getenv("SUMMARY_DAILY_LIMIT", "200"))
            wait_on_limit = os.getenv("SUMMARY_WAIT_ON_LIMIT", "true").lower() in ("1", "true", "yes")
            _rate_limiter = _RateLimiter(per_minute=minute_limit, per_day=daily_limit, wait=wait_on_limit)
        if not _rate_limiter.acquire():
            return "Error: Rate limit exceeded."
        client = _get_gemini_client()
        prompt = SUMMARY_PROMPT_TEMPLATE.format(article=article.strip())
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.models.generate_content(model=model, contents=prompt)
        )
        summary_text = getattr(response, "text", None)
        if not summary_text and hasattr(response, "candidates"):
            try:
                summary_text = response.candidates[0].content.parts[0].text
            except (AttributeError, IndexError):
                summary_text = str(response)
        return summary_text.strip() if summary_text else "Error: No summary text found."
    except Exception as e:
        return "Error: Could not generate summary."


def generate_summary_sync(article: str, model: str = "gemini-2.0-flash") -> str:
    """Synchronous wrapper for environments where async is inconvenient.
    Used by Scrapy pipeline to avoid event-loop conflicts.
    """
    if not (article or "").strip():
        return ""
    try:
        global _rate_limiter
        if _rate_limiter is None:
            minute_limit = int(os.getenv("SUMMARY_MINUTE_LIMIT", "15"))
            daily_limit = int(os.getenv("SUMMARY_DAILY_LIMIT", "200"))
            wait_on_limit = os.getenv("SUMMARY_WAIT_ON_LIMIT", "true").lower() in ("1", "true", "yes")
            _rate_limiter = _RateLimiter(per_minute=minute_limit, per_day=daily_limit, wait=wait_on_limit)
        if not _rate_limiter.acquire():
            return "Error: Rate limit exceeded."
        client = _get_gemini_client()
        prompt = SUMMARY_PROMPT_TEMPLATE.format(article=article.strip())
        response = client.models.generate_content(model=model, contents=prompt)
        summary_text = getattr(response, "text", None)
        if not summary_text and hasattr(response, "candidates"):
            try:
                summary_text = response.candidates[0].content.parts[0].text
            except (AttributeError, IndexError):
                summary_text = str(response)
        return summary_text.strip() if summary_text else "Error: No summary text found."
    except Exception:
        return "Error: Could not generate summary."
