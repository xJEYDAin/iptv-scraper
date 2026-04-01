#!/usr/bin/env python3
"""IPTV Playlist Generator - HK专区和全部频道"""
import logging
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from config import OUTPUT_DIR, FILTERED_DIR, CACHE_DIR, CACHE_FILE, LOG_DIR, MIN_SPEED_KB, ENABLE_SPEEDTEST, SORT_BY_SPEED
from lib.speedtest import speedtest_channels, filter_by_speed, sort_by_speed, format_speed
from lib.helpers import setup_logging, parse_m3u
from lib.cache import load_cache, save_cache
from lib.whitelist import is_whitelisted as is_hk_cdn_whitelisted
from logo_map import get_logo_fuzzy
from lib.helpers import load_aliases
from group.normalize import normalize_channel_name, normalize_channels

EPG_URL = "https://epg.pw/pp.xml"

IS_GITHUB = os.getenv("GITHUB_ACTIONS") == "true"
TIMEOUT = 2 if IS_GITHUB else 3
MAX_WORKERS = 10
BATCH_SIZE = 50


def check_url(url, session=None):
    """Check URL using HEAD-first approach (fast), fallback to GET if needed."""
    if is_whitelisted(url):
        return (url, True)
    if session is None:
        session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IPTV-Scraper/1.0)"}
    try:
        r = session.head(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)
        if r.status_code in [200, 206, 301, 302, 303, 307, 308]:
            return (url, True)
    except Exception:
        pass
    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)
        return (url, r.status_code in [200, 301, 302, 303, 307, 308])
    except Exception:
        return (url, False)


def batch_validate(all_channels, logger):
    logger.info("=" * 50)
    logger.info("Starting batched validation")
    logger.info("=" * 50)

    cache = load_cache(CACHE_FILE)
    logger.info("Loaded cache: " + str(len(cache)) + " entries")

    to_validate = [ch for ch in all_channels if ch["url"] not in cache]
    logger.info("Need to validate: " + str(len(to_validate)) + " channels")
    logger.info("Already cached: " + str(len(cache)) + " channels")

    total = len(to_validate)
    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch = to_validate[batch_start:batch_end]

        logger.info("Batch " + str(batch_start//BATCH_SIZE + 1) + "/" + str((total + BATCH_SIZE - 1)//BATCH_SIZE))
        logger.info("  Progress: " + str(batch_end) + "/" + str(total))

        session = requests.Session()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_url, ch["url"], session): ch for ch in batch}
            for future in as_completed(futures):
                url, is_valid = future.result()
                cache[url] = is_valid
                if len(cache) % 200 == 0:
                    save_cache(cache, CACHE_FILE)

        save_cache(cache, CACHE_FILE)
        logger.info("  Done. Cached total: " + str(len(cache)))

    for ch in all_channels:
        ch["is_valid"] = cache.get(ch["url"], False)

    valid_count = sum(1 for ch in all_channels if ch["is_valid"])
    logger.info("=" * 50)
    logger.info("Validation complete: " + str(valid_count) + "/" + str(len(all_channels)) + " valid")

    return all_channels, cache


def categorize(name, group, logo=""):
    from group.categorizer import categorize as _cat
    return _cat(name, group, logo)


def is_hk_region(name, group, cat=None):
    from group.categorizer import is_hk_region as _hk
    return _hk(name, group, cat)


def generate_playlist(logger):
    logger.info("=" * 50)
    logger.info("Generating playlists")
    logger.info("=" * 50)

    # 加载别名映射
    aliases = load_aliases()
    logger.info("Loaded " + str(len(aliases)) + " channel aliases")

    # 读取所有过滤后的频道
    all_channels = []
    for sf in sorted(FILTERED_DIR.glob("*.m3u*"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            channels = parse_m3u(sf.read_text(encoding='utf-8'))
            all_channels.extend(channels)
            logger.info("Parsed " + str(len(channels)) + " from " + sf.name)
        except Exception as e:
            logger.warning("Failed: " + sf.name)

    # 标准化频道名称
    for ch in all_channels:
        raw_name = ch.get("tvg_name", "") or ch.get("name", "")
        ch["_normalized_name"] = normalize_channel_name(raw_name, aliases)
    logger.info("Normalized channel names")

    # 去重（按 URL）
    seen_urls = set()
    deduped = []
    for ch in all_channels:
        if ch["url"] not in seen_urls:
            seen_urls.add(ch["url"])
            deduped.append(ch)
    all_channels = deduped
    logger.info("Total channels (deduped): " + str(len(all_channels)))

    # 验证
    skip_validation = os.getenv("SKIP_VALIDATION") == "1"
    cache = load_cache(CACHE_FILE)
    if skip_validation:
        logger.info("SKIP_VALIDATION=1, using cached results + HK CDN whitelist")
        for ch in all_channels:
            ch["is_valid"] = cache.get(ch["url"], False) or is_hk_cdn_whitelisted(ch["url"])
    else:
        all_channels, cache = batch_validate(all_channels, logger)

    # Speed test (only valid channels)
    if ENABLE_SPEEDTEST and not skip_validation:
        valid_chs = [ch for ch in all_channels if ch["is_valid"]]
        logger.info(f"[Speedtest] Testing {len(valid_chs)} valid channels...")
        speedtest_channels(valid_chs, logger, min_speed_kb=MIN_SPEED_KB)
        
        before_speed = len(valid_chs)
        valid_chs, filtered_count = filter_by_speed(valid_chs, min_speed_kb=MIN_SPEED_KB)
        logger.info(f"[Speedtest] Filtered {filtered_count} slow links (< {MIN_SPEED_KB} KB/s), {len(valid_chs)} remain")
        
        valid_urls = {ch["url"] for ch in valid_chs}
        for ch in all_channels:
            ch["is_valid"] = ch["is_valid"] and ch["url"] in valid_urls
        
        if SORT_BY_SPEED:
            valid_chs = sort_by_speed(valid_chs)
            logger.info("[Speedtest] Sorted by speed (fastest first)")
    else:
        valid_chs = [ch for ch in all_channels if ch["is_valid"]]

    # 合并同名频道（保留最优 URL + 备用）
    logger.info("Merging duplicate channels...")
    valid_chs = normalize_channels(valid_chs, aliases)
    logger.info("Channels after merging: " + str(len(valid_chs)))

    # 分类所有频道
    from output.playlist import generate_playlist as gen_pl
    return gen_pl(valid_chs, MIN_SPEED_KB)


def main():
    logger = setup_logging(LOG_DIR, "generate")
    return generate_playlist(logger)


if __name__ == "__main__":
    main()
