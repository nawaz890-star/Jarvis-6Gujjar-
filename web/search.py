"""
DuckDuckGo HTML search integration with auto-open-of-top-result option.

This module scrapes the DuckDuckGo HTML search result page, extracts titles and
URLs, and optionally auto-opens the top result in the default browser. Results
are cached for a short TTL to improve resiliency when offline.
"""
from typing import List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
import webbrowser
import logging
from .cache import get_cache, set_cache

logger = logging.getLogger(__name__)

DUCKDUCKGO_HTML = "https://html.duckduckgo.com/html/"
DEFAULT_TTL = 180


def search(query: str, max_results: int = 5, auto_open_top: bool = True) -> List[Tuple[str, str, Optional[str]]]:
    """Search and return a list of (title, url, snippet). If auto_open_top is True,
    open the first result in the default browser.
    """
    if not query:
        return []
    cache_key = f"ddg:{query}:{max_results}"
    cached = get_cache(cache_key)
    if cached:
        logger.debug("DDG: cache hit for %s", query)
        results = cached
        if auto_open_top and results:
            try:
                webbrowser.open(results[0][1])
            except Exception:
                logger.exception("Failed to open top search result")
        return results

    headers = {"User-Agent": "jarvis/1.0 (+https://example)"}
    try:
        resp = requests.post(DUCKDUCKGO_HTML, data={"q": query}, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Tuple[str, str, Optional[str]]] = []
        # DuckDuckGo HTML uses links with class 'result__a'
        for a in soup.select("a.result__a")[:max_results]:
            title = a.get_text().strip()
            href = a.get('href')
            snippet_el = a.find_parent().select_one('.result__snippet')
            snippet = snippet_el.get_text().strip() if snippet_el else None
            results.append((title, href, snippet))
        # Fallback: look for generic links
        if not results:
            for a in soup.select('a'):
                href = a.get('href')
                txt = a.get_text().strip()
                if href and txt and href.startswith('http'):
                    results.append((txt, href, None))
                    if len(results) >= max_results:
                        break
        # Cache results
        set_cache(cache_key, results, ttl=DEFAULT_TTL)
        if auto_open_top and results:
            try:
                webbrowser.open(results[0][1])
            except Exception:
                logger.exception("Failed to open top search result")
        return results
    except Exception as e:
        logger.exception("DuckDuckGo search failed: %s", e)
        # Fallback to cache even on error
        if cached:
            return cached
        return []
