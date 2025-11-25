import json
from urllib.parse import urlparse

from google import genai
from tavily import TavilyClient
from app.services.embedding.model_provider import _get_gemini_client
from app.config.settings import settings

WHITELIST = {
    "kathmandupost.com": 0.9,
    "ekantipur.com": 0.85,
    "thehimalayantimes.com": 0.85,
}

tavily_client = TavilyClient(api_key=settings.tavily_api_key)
gemini_client = _get_gemini_client()


def reliability_score(article) -> int:
    search_query = article["title"]
    tavily_response = tavily_client.search(search_query, max_results=10)

    search_context = json.dumps(tavily_response, ensure_ascii=False, indent=2)

    prompt = f"""
    You are a fact-checking assistant. Analyze the following news article and compare it with search results to verify its accuracy.

    NEWS ARTICLE:
    Title: {article["title"]}
    Summary: {article["summary"]}
    Content: {article["content"]}
    Source: {article["source"]}

    SEARCH RESULTS FROM TAVILY:
    {search_context}

    Please provide a fact-check analysis with:

    1. **Accuracy Score (0-100)**: Overall confidence (0-100) that the article's factual
        claims are accurate.
    2. **Verification Status**: For each claim, indicate if it's verified, unverified, or
        contradicted.
    3. **Supporting Evidence**: Evidence from the search results that supports or
        contradicts each claim.
    4. **Overall Assessment**: Brief summary of the article's reliability.

    Respond in JSON format.
    """

    response = gemini_client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0,
        ),
    )

    response_text = response.text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
    elif response_text.startswith("```"):
        response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

    fact_check_json = json.loads(response_text)

    return fact_check_json["accuracy_score"]
