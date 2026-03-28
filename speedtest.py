#!/usr/bin/env python3
"""IPTV Speed Test - Measure stream download speed and filter by rate threshold"""
import json
import logging
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from config import CACHE_DIR, LOG_DIR

# Speed test settings
MIN_SPEED_KB = float(os.getenv("MIN_SPEED_KB", "500"))   # Minimum speed in KB/s (default 500KB/s)
TIMEOUT_SEC = int(os.getenv("SPEEDTEST_TIMEOUT", "5"))   # Timeout per URL
MAX_WORKERS = int(os.getenv("SPEEDTEST_WORKERS", "10"))  # Parallel workers
HEAD_BYTES = 512 * 1024  # Download 512KB to measure speed

# Cache file for speed test results
SPEEDTEST_CACHE_FILE = CACHE_DIR / "speedtest_cache.json"


def speedtest_url_curl(url, timeout=TIMEOUT_SEC):
    """Test URL download speed using curl.
    
    Returns:
        float: Speed in bytes/second, or 0 if failed
    """
    try:
        # curl -w "%{speed_download}" -m timeout -r 0-511999 -L -s -o /dev/null $URL
        # -w "%{speed_download}" outputs bytes/sec
        # -r 0-511999 downloads only first 512KB
        # -L follow redirects
        # -s silent
        # -o /dev/null discard output
        result = subprocess.run(
            [
                "curl", "-w", "%{speed_download}",
                "-m", str(timeout),
                "-r", f"0-{HEAD_BYTES - 1}",
                "-L", "-s", "-o", "/dev/null",
                "--connect-timeout", "3",
                url
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 2
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                speed = float(result.stdout.strip())
                return speed  # bytes/sec
            except ValueError:
                return 0
        return 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        return 0


def speedtest_url_requests(url, timeout=TIMEOUT_SEC, session=None):
    """Fallback: test URL speed using requests + timing.
    
    Returns:
        float: Speed in bytes/second, or 0 if failed
    """
    import requests
    if session is None:
        session = requests.Session()
    try:
        start = datetime.now()
        r = session.get(url, timeout=timeout, stream=True, allow_redirects=True)
        r.raise_for_status()
        # Read up to HEAD_BYTES
        total = 0
        for chunk in r.iter_content(chunk_size=8192):
            total += len(chunk)
            if total >= HEAD_BYTES:
                break
        elapsed = (datetime.now() - start).total_seconds()
        if elapsed > 0:
            return total / elapsed
        return 0
    except Exception:
        return 0


def load_speedtest_cache():
    """Load speedtest cache from disk."""
    if SPEEDTEST_CACHE_FILE.exists():
        try:
            return json.loads(SPEEDTEST_CACHE_FILE.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            SPEEDTEST_CACHE_FILE.unlink()
    return {}


def save_speedtest_cache(cache):
    """Atomically save speedtest cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = SPEEDTEST_CACHE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.rename(SPEEDTEST_CACHE_FILE)


def format_speed(speed_bps):
    """Format bytes/sec as human-readable string."""
    if speed_bps <= 0:
        return "N/A"
    kbps = speed_bps / 1024
    mbps = kbps / 1024
    if mbps >= 1:
        return f"{mbps:.1f} MB/s"
    elif kbps >= 1:
        return f"{kbps:.0f} KB/s"
    else:
        return f"{speed_bps:.0f} B/s"


def speedtest_channels(channels, logger, use_curl=True, min_speed_kb=MIN_SPEED_KB):
    """Speed test all channels and return results.
    
    Args:
        channels: List of channel dicts with 'url' key
        logger: Logger instance
        use_curl: Use curl (True) or requests fallback (False)
        min_speed_kb: Minimum speed threshold in KB/s
    
    Returns:
        dict: url -> speed (bytes/sec)
    """
    cache = load_speedtest_cache()
    logger.info(f"[Speedtest] Cache loaded: {len(cache)} entries")
    logger.info(f"[Speedtest] Min speed threshold: {min_speed_kb} KB/s ({min_speed_kb * 1024} bytes/sec)")
    logger.info(f"[Speedtest] Method: {'curl' if use_curl else 'requests'}")
    logger.info(f"[Speedtest] Workers: {MAX_WORKERS}, Timeout: {TIMEOUT_SEC}s")
    
    # Deduplicate URLs first
    unique_urls = list({ch["url"] for ch in channels if ch.get("url")})
    logger.info(f"[Speedtest] Unique URLs to test: {len(unique_urls)}")
    
    to_test = [url for url in unique_urls if url not in cache]
    logger.info(f"[Speedtest] Already cached: {len(unique_urls) - len(to_test)}, need to test: {len(to_test)}")
    
    results = {}
    newly_tested = 0
    
    if to_test:
        session = None if use_curl else __import__('requests').Session()
        
        # Batch processing
        BATCH = 100
        total_batches = (len(to_test) + BATCH - 1) // BATCH
        
        for batch_start in range(0, len(to_test), BATCH):
            batch_end = min(batch_start + BATCH, len(to_test))
            batch = to_test[batch_start:batch_end]
            batch_num = batch_start // BATCH + 1
            
            logger.info(f"[Speedtest] Batch {batch_num}/{total_batches}: testing {len(batch)} URLs...")
            
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {
                    executor.submit(
                        speedtest_url_curl if use_curl else speedtest_url_requests,
                        url, TIMEOUT_SEC, session
                    ): url for url in batch
                }
                
                for future in as_completed(futures):
                    url = futures[future]
                    speed = future.result()
                    cache[url] = speed
                    newly_tested += 1
                    
                    if newly_tested % 50 == 0:
                        save_speedtest_cache(cache)
            
            save_speedtest_cache(cache)
            logger.info(f"[Speedtest] Batch {batch_num} done. Cached: {len(cache)}, New: {newly_tested}")
    
    # Use cache for all URLs
    for ch in channels:
        url = ch.get("url")
        if url:
            ch["speed_bps"] = cache.get(url, 0)
            ch["speed_str"] = format_speed(ch["speed_bps"])
            ch["meets_min_speed"] = ch["speed_bps"] >= (min_speed_kb * 1024)
    
    # Stats
    total = len(unique_urls)
    above_threshold = sum(1 for url, spd in cache.items() if spd >= min_speed_kb * 1024)
    
    logger.info(f"[Speedtest] === Speedtest Complete ===")
    logger.info(f"[Speedtest] Total URLs: {total}")
    logger.info(f"[Speedtest] Above {min_speed_kb} KB/s: {above_threshold} ({above_threshold*100//total if total else 0}%)")
    logger.info(f"[Speedtest] Newly tested this run: {newly_tested}")
    
    return cache


def filter_by_speed(channels, min_speed_kb=MIN_SPEED_KB):
    """Filter channels by minimum speed threshold."""
    min_bps = min_speed_kb * 1024
    before = len(channels)
    filtered = [ch for ch in channels if ch.get("speed_bps", 0) >= min_bps]
    after = len(filtered)
    return filtered, before - after


def sort_by_speed(channels, descending=True):
    """Sort channels by speed (fastest first)."""
    return sorted(channels, key=lambda ch: ch.get("speed_bps", 0), reverse=descending)


def main():
    """Test speedtest standalone."""
    from utils import setup_logging
    logger = setup_logging(LOG_DIR, "speedtest")
    
    # Test a few URLs if called standalone
    test_urls = [
        "https://example.com/test.m3u8",
    ]
    
    logger.info("Speedtest module - for import use")
    return {}


if __name__ == "__main__":
    main()
