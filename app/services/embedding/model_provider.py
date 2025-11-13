from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable, List

from app.config.settings import settings

# Default Gemini embedding model and dimension
EMBEDDING_MODEL = settings.gemini_embedding_model
# text-embedding-004 returns 768-dimensional vectors
EMBEDDING_DIM = 3072


@lru_cache(maxsize=1)
def _get_gemini_client():
    """Global singleton Gemini client instance."""
    from google import genai  # lazy import to avoid hard dep at import time

    api_key = settings.gemini_api_key
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)


def _extract_embedding_values(resp) -> List[float]:
    """
    Try to robustly extract embedding values from google-genai responses.
    Handles both single and varied response shapes.
    """
    # Attribute style: resp.embedding.values
    try:
        emb = getattr(resp, "embedding", None)
        if emb is not None:
            vals = getattr(emb, "values", None)
            if vals is not None:
                return [float(x) for x in vals]
    except Exception:
        pass

    # Dict-like style: resp["embedding"]["values"]
    try:
        if isinstance(resp, dict):
            emb = resp.get("embedding")
            if isinstance(emb, dict) and "values" in emb:
                return [float(x) for x in emb["values"]]
    except Exception:
        pass

    # Raw list/tuple of floats
    if isinstance(resp, (list, tuple)) and all(isinstance(x, (int, float)) for x in resp):
        return [float(x) for x in resp]

    raise ValueError("Unexpected embedding response format from Gemini")


def embed_text(text: str) -> List[float]:
    """Encode a single string into an embedding list[float] via Gemini."""
    if not (text or "").strip():
        # Return a zero vector to preserve dimensionality expectations
        return [0.0] * EMBEDDING_DIM
    client = _get_gemini_client()
    resp = client.models.embed_content(model=EMBEDDING_MODEL, contents=text)
    values = resp.embeddings[0].values

    
    # Pad or trim to 3072 dims
    if len(values) < EMBEDDING_DIM:
        values = list(values) + [0.0] * (EMBEDDING_DIM - len(values))
    elif len(values) > EMBEDDING_DIM:
        values = list(values)[:EMBEDDING_DIM]
    return values


def embed_texts(texts: Iterable[str]) -> List[List[float]]:
    """Encode multiple strings into embeddings (list[list[float]]) via Gemini."""
    items = list(texts)
    if not items:
        return []
    client = _get_gemini_client()
    try:
        # Prefer batch endpoint when available
        resp = client.models.batch_embed_contents(
            model=EMBEDDING_MODEL,
            requests=[{"content": t} for t in items],
        )
        embeddings = getattr(resp, "embeddings", None)
        if embeddings is None and isinstance(resp, dict):
            embeddings = resp.get("embeddings")
        if embeddings:
            # Pad or trim each embedding to 3072 dims
            out: List[List[float]] = []
            for emb in embeddings:
                vals = getattr(emb, "values", None)
                if vals is None and isinstance(emb, dict):
                    vals = emb.get("values")
                vals = list(vals or [])
                if len(vals) < EMBEDDING_DIM:
                    vals = vals + [0.0] * (EMBEDDING_DIM - len(vals))
                elif len(vals) > EMBEDDING_DIM:
                    vals = vals[:EMBEDDING_DIM]
                out.append([float(x) for x in vals])
            return out
        # Fallback to sequential if unexpected structure
    except Exception:
        pass

    # Sequential fallback
    return [embed_text(t) for t in items]
