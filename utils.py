#!/usr/bin/env python3
"""Shared utilities for IPTV Scraper"""
import json
import re
import sys
import logging
import time
import requests
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_aliases(alias_file=None):
    """Load channel alias mapping from alias.txt.
    
    Format: 原始名称 -> 标准名称
    Returns a dict: {alias_name: canonical_name}
    """
    if alias_file is None:
        alias_file = Path(__file__).parent / "alias.txt"
    else:
        alias_file = Path(alias_file)
    
    if not alias_file.exists():
        return {}
    
    aliases = {}
    try:
        content = alias_file.read_text(encoding='utf-8')
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '->' in line:
                parts = line.split('->', 1)
                alias_name = parts[0].strip()
                canonical = parts[1].strip()
                if alias_name and canonical:
                    aliases[alias_name] = canonical
    except Exception as e:
        logging.warning(f"Failed to load aliases from {alias_file}: {e}")
    
    return aliases


def normalize_channel_name(name, aliases):
    """Normalize a channel name using alias mapping.
    
    If the name matches an alias, return the canonical name.
    Otherwise return the original name stripped.
    """
    if not name:
        return name
    name_stripped = name.strip()
    return aliases.get(name_stripped, name_stripped)


def setup_logging(log_dir, prefix):
    """Setup logging to file and stdout."""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime('%Y%m%d')
    log_file = str(log_dir / (prefix + "_" + today_str + ".log"))
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def parse_m3u(content):
    """Parse M3U content and return list of channel dicts."""
    channels = []
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf = line
            name = line.split(',', 1)[1].strip() if ',' in line else ""
            tvg_name = re.search(r'tvg-name="([^"]*)"', line)
            tvg_logo = re.search(r'tvg-logo="([^"]*)"', line)
            group = re.search(r'group-title="([^"]*)"', line)
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    channels.append({
                        "name": name,
                        "tvg_name": tvg_name.group(1) if tvg_name else name,
                        "tvg_logo": tvg_logo.group(1) if tvg_logo else "",
                        "group": group.group(1) if group else "",
                        "url": url,
                        "raw_extinf": extinf
                    })
                    i += 2
                    continue
        i += 1
    return channels


# ─── Generic Cache ───────────────────────────────────────────────────────────

MAX_CACHE_ENTRIES = 10000  # Max entries before LRU eviction


def load_cache(cache_file):
    """Load JSON cache with proper error handling.
    Corrupted cache files are deleted and rebuilt.
    """
    cache_file = Path(cache_file)
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            logging.warning(f"Cache corrupted ({cache_file}), deleting and rebuilding...")
            cache_file.unlink()
    return {}


def save_cache(cache, cache_file):
    """Save JSON cache atomically with size-limit eviction.
    If entries exceed MAX_CACHE_ENTRIES, oldest entries are pruned.
    """
    cache_file = Path(cache_file)
    cache_dir = cache_file.parent
    cache_dir.mkdir(parents=True, exist_ok=True)

    # ── Fix #5: Cache size limit with LRU eviction ──────────────────────
    if len(cache) > MAX_CACHE_ENTRIES:
        # Sort by cache value (assumes value is timestamp or order key)
        # Keep the most recent MAX_CACHE_ENTRIES entries
        sorted_items = sorted(cache.items(), key=lambda x: str(x[1]))
        cache = dict(sorted_items[:MAX_CACHE_ENTRIES])
        logging.info(f"Cache pruned to {len(cache)} entries (limit: {MAX_CACHE_ENTRIES})")

    tmp = cache_file.with_suffix('.tmp')
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.rename(cache_file)


# ─── Retry + Rate-limiting URL Fetcher ──────────────────────────────────────

DEFAULT_TIMEOUT = 5
DEFAULT_MAX_RETRIES = 3
DEFAULT_RATE_LIMIT_DELAY = 0.5  # seconds between requests
DEFAULT_MAX_CONCURRENCY = 5


def fetch_with_retry(url, session=None, timeout=DEFAULT_TIMEOUT,
                      max_retries=DEFAULT_MAX_RETRIES,
                      logger=None):
    """Fetch URL with exponential-backoff retry (3 attempts).

    Returns:
        tuple: (success: bool, content: str or error_msg: str)
    """
    if session is None:
        session = requests.Session()

    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            return True, response.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait = (2 ** attempt) * DEFAULT_RATE_LIMIT_DELAY
                if logger:
                    logger.debug(f"  Retry {attempt+1}/{max_retries} for {url} after {wait:.1f}s: {e}")
                time.sleep(wait)
            else:
                if logger:
                    logger.debug(f"  Failed {url} after {max_retries} attempts: {e}")
                return False, str(e)
    return False, "exhausted retries"


def fetch_sources_rate_limited(sources, logger, max_workers=DEFAULT_MAX_CONCURRENCY,
                                delay=DEFAULT_RATE_LIMIT_DELAY):
    """Fetch multiple sources with rate-limiting and concurrency cap.

    Uses a semaphore to limit max concurrent requests and enforces
    a delay between successive requests to avoid rate-limiting.

    Returns:
        list of result dicts
    """
    import threading

    semaphore = threading.Semaphore(max_workers)
    results = []
    results_lock = threading.Lock()

    def fetch_one(source):
        name = source.get("name", "?")
        url = source.get("url", "")
        with semaphore:
            if delay > 0:
                time.sleep(delay)
            success, content = fetch_with_retry(url, logger=logger)
        result = {"name": name, "url": url, "success": success}
        if success:
            result["content"] = content
        else:
            result["error"] = content
        with results_lock:
            results.append(result)
        return result

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, src): src for src in sources}
        for future in as_completed(futures):
            future.result()  # raise exceptions if any

    return results


# ─── HK CDN Whitelist ─────────────────────────────────────────────────────────
# Domains/IPs in this list skip HEAD/GET validation (they require HK IP)
# to avoid false negatives from non-HK validation servers.

import re

HK_CDN_WHITELIST_PATTERNS = [
    # Domain wildcards
    re.compile(r'^https?://([^/]+\.)*hkdtmb\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*tdm\.com\.mo/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*viutv\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*now\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*tvb\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*rthk\.hk/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*hkcable\.com\.hk/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*cable-tvc\.com/', re.IGNORECASE),
    # IP ranges (partial Hong Kong ISP ranges)
    re.compile(r'^https?://61\.238\.\d+\.\d+/'),
    re.compile(r'^https?://116\.199\.\d+\.\d+/'),
    re.compile(r'^https?://202\.181\.\d+\.\d+/'),
    re.compile(r'^https?://203\.186\.\d+\.\d+/'),
    re.compile(r'^https?://1\.32\.\d+\.\d+/'),
    re.compile(r'^https?://42\.2\.\d+\.\d+/'),
]


def is_hk_cdn_whitelisted(url):
    """Return True if URL matches an HK CDN whitelist pattern."""
    for pattern in HK_CDN_WHITELIST_PATTERNS:
        if pattern.match(url):
            return True
    return False


# ─── HEAD-first URL validator ────────────────────────────────────────────────

def validate_url_head_first(url, session=None, timeout=DEFAULT_TIMEOUT,
                             logger=None):
    """Validate stream URL: try HEAD first (fast), fall back to GET on failure.

    Returns:
        bool: True if URL is reachable
    """
    # ── HK CDN Whitelist: skip validation for known HK CDN domains ─────────
    if is_hk_cdn_whitelisted(url):
        if logger:
            logger.debug(f"  [HK CDN whitelist] Skipping validation for {url}")
        return True

    if session is None:
        session = requests.Session()

    # ── Fix #3: HEAD first, GET fallback ─────────────────────────────────
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IPTV-Scraper/1.0)"}
    try:
        resp = session.head(url, timeout=timeout, allow_redirects=True,
                            headers=headers)
        if resp.status_code in (200, 206, 301, 302, 303, 307, 308):
            return True
    except Exception as e:
        if logger:
            logger.debug(f"  HEAD failed for {url}: {e}")

    # Fallback to GET (only on HEAD failure)
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True,
                           headers=headers, stream=True)
        if resp.status_code in (200, 206, 301, 302, 303, 307, 308):
            return True
    except Exception as e:
        if logger:
            logger.debug(f"  GET fallback failed for {url}: {e}")
    return False
