#!/usr/bin/env python3
from config import OUTPUT_DIR, FILTERED_DIR, CACHE_DIR, CACHE_FILE
"""IPTV Playlist Generator - Reuses validate_and_merge.py results for HK channels"""
import re
import logging
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

CACHE_FILE = CACHE_DIR / "validation_cache.json"

EPG_URL = "https://epgshare01.online/epgshare01/epg_48h.xml"

BATCH_SIZE = 500
MAX_WORKERS = 20
TIMEOUT = 3
BATCH_DELAY = 1

def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime('%Y%m%d')
    log_file = str(LOG_DIR / ("generate_" + today_str + ".log"))
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
                        "group": group.group(1) if group else "HK",
                        "url": url,
                        "raw_extinf": extinf
                    })
                    i += 2
                    continue
        i += 1
    return channels

def categorize(name, group):
    name_lower, group_lower = name.lower(), (group or "").lower()
    hk_kw = ['tvb', 'jade', 'pearl', 'viu', 'rthk', 'hoy', 'now tv', 'now news', 'cable', '无线', '翡翠', '明珠', '港台', '新闻台', 'j2', '开电视', 'hooy', 'star tv']
    tw_kw = ['tvbs', '台', '台湾', '中視', '華視', '民視', '東森', '三立', '非凡', '大愛', 'news', '綜合', '戲劇', '綜合台']
    cn_kw = ['cctv', 'cbn', '北京', '上海', '广东', '广州', '深圳', '浙江', '江苏', '四川', '湖南', '山东', '安徽', '福建', '凤凰', 'phtv', 'btv', 'sjtv']
    for kw in hk_kw:
        if kw in name_lower or kw in group_lower: return "🇭🇰 香港"
    for kw in tw_kw:
        if kw in name_lower: return "🇹🇼 台湾"
    for kw in cn_kw:
        if kw in name_lower: return "🇨🇳 大陆"
    if '澳门' in name or '澳視' in name or 'macau' in name_lower: return "🇲🇴 澳门"
    if any(kw in name_lower for kw in ['movie', '电影', '影城', 'cinema', 'hbo', 'cinemax']): return "🎬 电影"
    if any(kw in name_lower for kw in ['sport', 'sports', '体育', 'espn', '足球', '篮球']): return "⚽ 体育"
    if any(kw in name_lower for kw in ['kids', 'children', '卡通', '动画', 'anime', 'nick', '迪士尼', 'disney']): return "🧸 儿童"
    if any(kw in name_lower for kw in ['news', '新闻', 'cnn', 'bbc']): return "📰 新闻"
    if any(kw in name_lower for kw in ['entertainment', '娱乐', '综艺', 'variety']): return "🎭 娱乐"
    if any(kw in name_lower for kw in ['discovery', 'national geographic', '地理', '探索', 'history']): return "📺 纪录片"
    if any(kw in name_lower for kw in ['music', '音乐', 'mv', 'channel v', ' MTV']): return "🎵 音乐"
    if group and group.strip(): return "📺 " + group
    return "🌐 其他"

def check_url(url):
    """Validate URL with proper resource cleanup (no stream=True needed for HEAD)."""
    import requests
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return (url, r.status_code in [200, 301, 302, 303, 307, 308])
    except:
        return (url, False)

def load_cache():
    """Load validation cache with proper error handling.
    Corrupted cache files are deleted and rebuilt.
    """
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            logging.warning(f"Cache corrupted ({e}), deleting and rebuilding...")
            CACHE_FILE.unlink()
    return {}

def save_cache(cache):
    """Save validation cache atomically."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.rename(CACHE_FILE)

def get_latest_merged_hk():
    """Find the latest hk_merged_YYYYMMDD.m3u from validate_and_merge.py output."""
    files = sorted(OUTPUT_DIR.glob("hk_merged_*.m3u"), key=lambda p: p.stat().st_mtime, reverse=True)
    if files:
        return files[0]
    return None

def batch_validate(all_channels, logger):
    """Validate channels in batches with caching. Saves cache incrementally per URL."""
    logger.info("=" * 50)
    logger.info("Starting batched validation")
    logger.info("=" * 50)

    cache = load_cache()
    logger.info("Loaded cache: " + str(len(cache)) + " entries")

    # Find channels to validate
    to_validate = []
    for ch in all_channels:
        if ch["url"] not in cache:
            to_validate.append(ch)

    logger.info("Need to validate: " + str(len(to_validate)) + " channels")
    logger.info("Already cached: " + str(len(cache)) + " channels")

    # Process in batches
    total = len(to_validate)

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch = to_validate[batch_start:batch_end]

        logger.info("Batch " + str(batch_start//BATCH_SIZE + 1) + "/" + str((total + BATCH_SIZE - 1)//BATCH_SIZE))
        logger.info("  Progress: " + str(batch_end) + "/" + str(total))

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_url, ch["url"]): ch for ch in batch}
            for future in as_completed(futures):
                url, is_valid = future.result()
                cache[url] = is_valid
                # P0-4: incremental cache save - update after each URL
                save_cache(cache)

        logger.info("  Done. Cached total: " + str(len(cache)))

        if batch_end < total:
            time.sleep(BATCH_DELAY)

    # Update channels with validation results
    for ch in all_channels:
        ch["is_valid"] = cache.get(ch["url"], False)

    valid_count = sum(1 for ch in all_channels if ch["is_valid"])
    logger.info("=" * 50)
    logger.info("Validation complete: " + str(valid_count) + "/" + str(len(all_channels)) + " valid")

    return all_channels, cache

def generate_playlist(logger):
    logger.info("=" * 50)
    logger.info("Generating final playlist")
    logger.info("=" * 50)

    today_str = datetime.now().strftime('%Y%m%d')

    # --- HK Channels: Reuse validate_and_merge.py output (already validated) ---
    hk_channels = []
    hk_source = get_latest_merged_hk()

    if hk_source:
        logger.info("Reading HK channels from validated merge: " + hk_source.name)
        try:
            channels = parse_m3u(hk_source.read_text(encoding='utf-8'))
            for ch in channels:
                ch["is_valid"] = True  # Already validated by validate_and_merge.py
            hk_channels = channels
            logger.info("Loaded " + str(len(hk_channels)) + " HK channels (pre-validated)")
        except Exception as e:
            logger.error("Failed to read HK merge file: " + str(e))
            hk_channels = []
    else:
        logger.warning("No hk_merged_YYYYMMDD.m3u found! Falling back to filtered/ HK channels.")
        for sf in sorted(FILTERED_DIR.glob("*.m3u*"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                channels = parse_m3u(sf.read_text(encoding='utf-8'))
                hk_channels.extend(channels)
            except Exception as e:
                logger.warning("Failed: " + sf.name)

    # --- Non-HK Channels: Batch validate from filtered/ ---
    # Read all channels from filtered/ that are not HK
    non_hk_channels = []
    for sf in sorted(FILTERED_DIR.glob("*.m3u*"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            channels = parse_m3u(sf.read_text(encoding='utf-8'))
            non_hk_channels.extend(channels)
            logger.info("Parsed " + str(len(channels)) + " from " + sf.name)
        except Exception as e:
            logger.warning("Failed: " + sf.name)

    # Remove duplicates by URL, prioritize first-seen
    seen_urls = set()
    deduped_non_hk = []
    for ch in non_hk_channels:
        if ch["url"] not in seen_urls:
            seen_urls.add(ch["url"])
            deduped_non_hk.append(ch)
    non_hk_channels = deduped_non_hk
    logger.info("Non-HK channels (deduped): " + str(len(non_hk_channels)))

    # Batch validate non-HK channels
    non_hk_channels, cache = batch_validate(non_hk_channels, logger)

    # Filter valid non-HK channels
    valid_non_hk = [ch for ch in non_hk_channels if ch["is_valid"]]
    logger.info("Valid non-HK channels: " + str(len(valid_non_hk)))

    # Categorize non-HK channels
    categorized = {}
    for ch in valid_non_hk:
        cat = categorize(ch["name"], ch["group"])
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(ch)

    # Add HK channels to categorized (pre-validated, no re-validation needed)
    categorized_hk = {}
    for ch in hk_channels:
        cat = "🇭🇰 香港"
        if cat not in categorized_hk:
            categorized_hk[cat] = []
        categorized_hk[cat].append(ch)

    logger.info("HK channels (from merge): " + str(len(hk_channels)))
    logger.info("Non-HK categories: " + str(len(categorized)))

    # Sort categories
    order = ["🇭🇰 香港", "🇹🇼 台湾", "🇨🇳 大陆", "🇲🇴 澳门", "🎬 电影", "⚽ 体育", "🧸 儿童", "📰 新闻", "🎭 娱乐", "📺 纪录片", "🎵 音乐", "🌐 其他"]
    def sort_key(c): return (0, order.index(c)) if c in order else (1, c)

    # --- Generate HK playlist (from pre-validated merge) ---
    hk_lines = ['#EXTM3U x-tvg-url="' + EPG_URL + '"',
                '#PLAYLIST:HK IPTV ' + datetime.now().strftime('%Y-%m-%d'), '']
    hk_lines.append('#EXTGRP:🇭🇰 香港 (' + str(len(hk_channels)) + ')')
    for ch in hk_channels:
        hk_lines.extend([ch["raw_extinf"], ch["url"]])
    hk_file = OUTPUT_DIR / "hk_merged.m3u"
    hk_file.write_text('\n'.join(hk_lines), encoding='utf-8')
    logger.info("HK Playlist -> " + str(hk_file) + " (" + str(len(hk_channels)) + " channels)")

    # --- Generate ALL playlist ---
    total_valid = len(hk_channels) + len(valid_non_hk)
    all_lines = ['#EXTM3U x-tvg-url="' + EPG_URL + '"',
                 '#PLAYLIST:All IPTV ' + datetime.now().strftime('%Y-%m-%d'),
                 '# Total: ' + str(total_valid) + ' (HK: ' + str(len(hk_channels)) + ', Non-HK: ' + str(len(valid_non_hk)) + '), Cache: ' + str(len(cache)),
                 '']

    # HK first
    for cat, chs in sorted(categorized_hk.items(), key=lambda x: sort_key(x[0])):
        all_lines.append('#EXTGRP:' + cat + ' (' + str(len(chs)) + ')')
        for ch in chs:
            all_lines.extend([ch["raw_extinf"], ch["url"]])
        all_lines.append('')

    # Other categories
    for cat, chs in sorted(categorized.items(), key=lambda x: sort_key(x[0])):
        all_lines.append('#EXTGRP:' + cat + ' (' + str(len(chs)) + ')')
        for ch in chs[:100]:
            all_lines.extend([ch["raw_extinf"], ch["url"]])
        if len(chs) > 100:
            all_lines.append('# ... and ' + str(len(chs) - 100) + ' more')
        all_lines.append('')

    all_file = OUTPUT_DIR / "all_merged.m3u"
    all_file.write_text('\n'.join(all_lines), encoding='utf-8')
    logger.info("ALL Playlist -> " + str(all_file) + " (" + str(total_valid) + " channels, " + str(len(categorized) + len(categorized_hk)) + " categories)")

    return {
        "hk": {"file": str(hk_file), "channels": len(hk_channels), "groups": len(categorized_hk)},
        "all": {"file": str(all_file), "channels": total_valid, "groups": len(categorized) + len(categorized_hk), "cache": len(cache)}
    }

def main():
    logger = setup_logging()
    return generate_playlist(logger)

if __name__ == "__main__":
    main()
