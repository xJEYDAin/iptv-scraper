#!/usr/bin/env python3
"""Download logic for IPTV sources."""
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from config import SOURCES_DIR
from utils.helpers import fetch_with_retry, fetch_sources_rate_limited, setup_logging

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
DEFAULT_MAX_RETRIES = 3
DEFAULT_RATE_LIMIT_DELAY = 0.5
DEFAULT_MAX_CONCURRENCY = 5


def download_source(name: str, url: str, timeout: int = DEFAULT_TIMEOUT,
                   max_retries: int = DEFAULT_MAX_RETRIES) -> Tuple[str, bool, str]:
    """Download a single source URL.
    
    Returns:
        tuple: (name, success, content_or_error)
    """
    success, content = fetch_with_retry(url, timeout=timeout, max_retries=max_retries, logger=logger)
    return (name, success, content)


def download_sources(sources: List[Dict[str, str]], 
                    max_workers: int = DEFAULT_MAX_CONCURRENCY,
                    delay: float = DEFAULT_RATE_LIMIT_DELAY) -> List[Dict]:
    """Download multiple sources concurrently.
    
    Args:
        sources: list of dicts with 'name' and 'url' keys
        max_workers: max concurrent downloads
        delay: delay between requests
    
    Returns:
        list of result dicts
    """
    return fetch_sources_rate_limited(sources, logger, max_workers=max_workers, delay=delay)


def save_downloaded_content(name: str, content: str, output_dir: Path = None) -> Path:
    """Save downloaded M3U content to file.
    
    Args:
        name: source name (used for filename)
        content: M3U content
        output_dir: directory to save to (defaults to SOURCES_DIR)
    
    Returns:
        Path to saved file
    """
    if output_dir is None:
        output_dir = SOURCES_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_name = "".join(c if c.isalnum() or c in '_- ' else '_' for c in name)
    filepath = output_dir / f"{safe_name}.m3u"
    filepath.write_text(content, encoding='utf-8')
    return filepath
