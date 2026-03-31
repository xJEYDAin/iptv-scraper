#!/usr/bin/env python3
"""Helper utilities shared across modules."""
import json
import logging
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_aliases(alias_file=None):
    if alias_file is None:
        alias_file = Path(__file__).parent.parent / "alias.txt"
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
    if not name:
        return name
    name_stripped = name.strip()
    return aliases.get(name_stripped, name_stripped)


def setup_logging(log_dir, prefix):
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
    import re
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


DEFAULT_TIMEOUT = 5
DEFAULT_MAX_RETRIES = 3
DEFAULT_RATE_LIMIT_DELAY = 0.5
DEFAULT_MAX_CONCURRENCY = 5


def fetch_with_retry(url, session=None, timeout=DEFAULT_TIMEOUT,
                      max_retries=DEFAULT_MAX_RETRIES,
                      logger=None):
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
            future.result()

    return results
