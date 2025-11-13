import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
import time
import random
from app.config.settings import settings

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


def _retry_params():
    attempts = max(1, int(settings.summary_retry_attempts))
    base_backoff = max(0.0, float(settings.summary_retry_backoff_seconds))
    max_backoff = max(base_backoff, float(settings.summary_retry_max_backoff_seconds))
    jitter = bool(settings.summary_retry_jitter)
    return attempts, base_backoff, max_backoff, jitter


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    from google import genai  # lazy import
    api_key = settings.gemini_api_key
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
    client = _get_gemini_client()
    prompt = SUMMARY_PROMPT_TEMPLATE.format(article=article.strip())
    attempts, base_backoff, max_backoff, jitter = _retry_params()

    last_exc: Exception | None = None
    for i in range(attempts):
        try:
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
            last_exc = e
            if i == attempts - 1:
                break
            delay = min(max_backoff, base_backoff * (2 ** i))
            if jitter:
                delay *= 0.5 + random.random()
            await asyncio.sleep(max(0.05, delay))
    return "Error: Could not generate summary."


def generate_summary_sync(article: str, model: str = "gemini-2.0-flash") -> str:
    """Synchronous wrapper for environments where async is inconvenient.
    Used by Scrapy pipeline to avoid event-loop conflicts.
    """
    if not (article or "").strip():
        return ""
    client = _get_gemini_client()
    prompt = SUMMARY_PROMPT_TEMPLATE.format(article=article.strip())
    attempts, base_backoff, max_backoff, jitter = _retry_params()

    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            summary_text = getattr(response, "text", None)
            if not summary_text and hasattr(response, "candidates"):
                try:
                    summary_text = response.candidates[0].content.parts[0].text
                except (AttributeError, IndexError):
                    summary_text = str(response)
            return summary_text.strip() if summary_text else "Error: No summary text found."
        except Exception as e:
            last_exc = e
            if i == attempts - 1:
                break
            delay = min(max_backoff, base_backoff * (2 ** i))
            if jitter:
                delay *= 0.5 + random.random()
            time.sleep(max(0.05, delay))
    return "Error: Could not generate summary."
