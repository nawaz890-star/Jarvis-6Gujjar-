"""
News fetching via RSS feeds using feedparser. Returns top N headlines as
(title, link, published).
"""
from typing import List, Tuple
import feedparser
import logging
from .cache import get_cache, set_cache

logger = logging.getLogger(__name__)
CACHE_TTL = 900

DEFAULT_FEEDS = [
    "https://news.google.com/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://hnrss.org/frontpage"
]


def fetch_headlines(feeds: List[str] = None, top_n: int = 5) -> List[Tuple[str, str, str]]:
    feeds = feeds or DEFAULT_FEEDS
    cache_key = f"news:{','.join(feeds)}:{top_n}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    headlines = []
    try:
        for feed in feeds:
            d = feedparser.parse(feed)
            for e in d.entries[:top_n]:
                title = e.get('title', 'No title')
                link = e.get('link', '')
                published = e.get('published', '')
                headlines.append((title, link, published))
                if len(headlines) >= top_n:
                    break
            if len(headlines) >= top_n:
                break
        set_cache(cache_key, headlines, ttl=CACHE_TTL)
        return headlines
    except Exception as e:
        logger.exception("Failed to fetch headlines: %s", e)
        if cached:
            return cached
        return []
