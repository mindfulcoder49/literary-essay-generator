from __future__ import annotations

import re
from typing import Any

import httpx

from app.config import get_settings
from app.logging_config import configure_logging


START_RE = re.compile(r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG EBOOK.*\*\*\*", re.IGNORECASE)
END_RE = re.compile(r"\*\*\* END OF (THIS|THE) PROJECT GUTENBERG EBOOK.*\*\*\*", re.IGNORECASE)

logger = configure_logging("gutenberg", "api.log")

def fetch_gutenberg_text(gutenberg_id: int) -> str:
    settings = get_settings()
    base_url = settings.gutenberg_text_url.format(id=gutenberg_id)
    candidates = [
        base_url,
        base_url.replace(".txt.utf-8", ".txt"),
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt",
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-8.txt",
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}.txt",
    ]
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        last_exc: Exception | None = None
        for url in candidates:
            try:
                logger.info("gutenberg fetch: %s", url)
                resp = client.get(url)
                resp.raise_for_status()
                if resp.text and len(resp.text) > 1000:
                    return resp.text
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                continue
        if last_exc:
            raise last_exc
        raise RuntimeError("Failed to fetch Gutenberg text")


def normalize_gutenberg_text(raw_text: str) -> str:
    start_match = START_RE.search(raw_text)
    end_match = END_RE.search(raw_text)
    if start_match and end_match:
        raw_text = raw_text[start_match.end(): end_match.start()]
    text = raw_text.replace("\r\n", "\n")
    # collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_gutenberg_metadata(gutenberg_id: int) -> dict[str, str | None]:
    settings = get_settings()
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        resp = client.get(f"{settings.gutendex_url}/{gutenberg_id}")
        resp.raise_for_status()
        data = resp.json()
    title = data.get("title")
    authors = data.get("authors") or []
    author = authors[0]["name"] if authors else None
    return {"title": title, "author": author}


def search_gutenberg(query: str) -> dict[str, Any]:
    settings = get_settings()
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        resp = client.get(settings.gutendex_url, params={"search": query})
        resp.raise_for_status()
        return resp.json()
