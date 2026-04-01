#!/usr/bin/env python3
"""Unified URL validation for IPTV streams.

Unified implementation: HEAD first + GET fallback + CDN whitelist.
Used by all modules - no more duplicate implementations.
"""
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional

from config import CACHE_DIR
from lib.whitelist import is_whitelisted

DEFAULT_TIMEOUT = 3
DEFAULT_MAX_WORKERS = 50


def validate_url(url: str, session: Optional[requests.Session] = None,
                 timeout: int = DEFAULT_TIMEOUT, logger=None) -> Tuple[str, bool]:
    """Validate stream URL: whitelist → HEAD first → GET fallback.

    Returns:
        tuple: (url, is_valid)
    """
    # 1. CDN whitelist - skip validation
    if is_whitelisted(url):
        if logger:
            logger.debug(f"  [Whitelist] Skipping validation for {url}")
        return (url, True)

    if session is None:
        session = requests.Session()

    headers = {"User-Agent": "Mozilla/5.0 (compatible; IPTV-Scraper/1.0)"}

    # 2. Try HEAD first (fast)
    try:
        resp = session.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        if resp.status_code in (200, 206, 301, 302, 303, 307, 308):
            return (url, True)
    except Exception as e:
        if logger:
            logger.debug(f"  HEAD failed for {url}: {e}")

    # 3. Fallback to GET (only on HEAD failure)
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True,
                          headers=headers, stream=True)
        if resp.status_code in (200, 206, 301, 302, 303, 307, 308):
            return (url, True)
    except Exception as e:
        if logger:
            logger.debug(f"  GET fallback failed for {url}: {e}")

    return (url, False)


def validate_batch(urls: List[str], max_workers: int = DEFAULT_MAX_WORKERS,
                   timeout: int = DEFAULT_TIMEOUT, logger=None) -> List[Tuple[str, bool]]:
    """Validate multiple URLs concurrently.

    Returns:
        list of (url, is_valid) tuples
    """
    results = []
    session = requests.Session()

    def _validate(url):
        return validate_url(url, session=session, timeout=timeout, logger=logger)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_validate, url): url for url in urls}
        for future in as_completed(futures):
            results.append(future.result())

    return results


# ─── Legacy wrappers for backward compatibility ────────────────────────────────

def validate_url_head_first(url: str, session=None, timeout=DEFAULT_TIMEOUT, logger=None):
    """Legacy wrapper: returns bool instead of tuple."""
    return validate_url(url, session=session, timeout=timeout, logger=logger)[1]


def check_url(url: str, session=None):
    """Legacy wrapper from generate_playlist.py."""
    return validate_url(url, session=session, timeout=DEFAULT_TIMEOUT, logger=None)
