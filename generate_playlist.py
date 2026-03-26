#!/usr/bin/env python3
"""IPTV Playlist Generator - HK专区和全部频道"""
import logging
import json
import os
import requests
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import OUTPUT_DIR, FILTERED_DIR, CACHE_DIR, CACHE_FILE, LOG_DIR
from utils import setup_logging, parse_m3u

CACHE_FILE = CACHE_DIR / "validation_cache.json"

EPG_URL = "https://epg.pw/pp.xml"

IS_GITHUB = os.getenv("GITHUB_ACTIONS") == "true"
TIMEOUT = 2 if IS_GITHUB else 3
MAX_WORKERS = 10
BATCH_SIZE = 50


def is_hk_region(name, group):
    """判断是否为港台地区频道"""
    name_lower, group_lower = name.lower(), (group or "").lower()
    full_text = name_lower + " " + group_lower
    
    hk_kw = ['tvb', '翡翠', '明珠', 'jade', 'pearl', 'j2', 'viutv', 'viu tv', 'rthk', '港台', 'hoy', 'now tv', 'nowtv', 'now news', 'cable', '有线', '开电视', '凤凰', '无线', '新闻台', '星空', 'star tv', 'hooy']
    tw_kw = ['tvbs', '台视', '中视', '华视', '民视', '东森', '三立', '非凡', '大爱', '公视', '客家', '原住民']
    mo_kw = ['澳门', '澳視', 'macau', '澳广视']
    
    return any(kw in full_text for kw in hk_kw + tw_kw + mo_kw)


def categorize(name, group):
    """分类频道"""
    name_lower, group_lower = name.lower(), (group or "").lower()
    full_text = name_lower + " " + group_lower
    
    if any(kw in full_text for kw in ['tvb', '翡翠台', '明珠台', 'jade', 'pearl', 'j2']):
        return "📺 TVB"
    if any(kw in full_text for kw in ['viutv', 'viu tv', 'viu6']):
        return "📺 ViuTV"
    if any(kw in full_text for kw in ['rthk', '港台', '香港电台']):
        return "📺 RTHK"
    if any(kw in full_text for kw in ['hoy', 'hooy', 'hoytv']):
        return "📺 HOY TV"
    if any(kw in full_text for kw in ['now tv', 'nowtv', 'now news', 'now直播', 'now财经']):
        return "📺 Now TV"
    if any(kw in full_text for kw in ['cable', '有线', '开电视', 'cable TV']):
        return "📺 有线电视"
    if any(kw in full_text for kw in ['凤凰', 'phoenix']):
        return "📺 凤凰卫视"
    if any(kw in full_text for kw in ['无线', '新闻台', '星空', 'star tv']):
        return "📺 香港其他"
    if any(kw in full_text for kw in ['tvbs', '台视', '中视', '华视', '民视', '东森', '三立', '非凡', '大爱', '公视']):
        return "🇹🇼 台湾"
    if any(kw in full_text for kw in ['澳门', '澳視', 'macau', '澳广视']):
        return "🇲🇴 澳门"
    if any(kw in full_text for kw in ['news', '新闻', 'cnn', 'bbc', 'dw', '半岛']):
        return "📰 新闻"
    if any(kw in full_text for kw in ['movie', '电影', 'cinema', 'hbo', 'cinemax', '影城', '卫视电影']):
        return "🎬 电影"
    if any(kw in full_text for kw in ['sport', 'sports', '体育', 'espn', '足球', '篮球', 'fox sports', 'beinsport']):
        return "⚽ 体育"
    if any(kw in full_text for kw in ['kids', 'children', '卡通', '动画', 'anime', 'nick', '迪士尼', 'disney', 'baby']):
        return "🧸 儿童"
    if any(kw in full_text for kw in ['entertainment', '娱乐', '综艺', 'variety', '综合台', '戏剧']):
        return "🎭 综艺"
    if any(kw in full_text for kw in ['discovery', 'national geographic', '地理', '探索', 'history', 'hist', '动物']):
        return "📺 纪录片"
    if any(kw in full_text for kw in ['music', '音乐', 'mv', 'channel v', 'mtv', 'vod']):
        return "🎵 音乐"
    if group and group.strip():
        return "📺 " + group
    return "🌐 其他"


def check_url(url, session=None):
    if session is None:
        session = requests.Session()
    try:
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        return (url, r.status_code in [200, 301, 302, 303, 307, 308])
    except requests.exceptions.Timeout:
        return (url, False)
    except requests.exceptions.ConnectionError:
        return (url, False)
    except Exception:
        return (url, False)


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            logging.warning(f"Cache corrupted ({e}), deleting and rebuilding...")
            CACHE_FILE.unlink()
    return {}


def save_cache(cache):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.rename(CACHE_FILE)


def batch_validate(all_channels, logger):
    logger.info("=" * 50)
    logger.info("Starting batched validation")
    logger.info("=" * 50)

    cache = load_cache()
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
                if len(cache) % 500 == 0:
                    save_cache(cache)

        save_cache(cache)
        logger.info("  Done. Cached total: " + str(len(cache)))

    for ch in all_channels:
        ch["is_valid"] = cache.get(ch["url"], False)

    valid_count = sum(1 for ch in all_channels if ch["is_valid"])
    logger.info("=" * 50)
    logger.info("Validation complete: " + str(valid_count) + "/" + str(len(all_channels)) + " valid")

    return all_channels, cache


def generate_playlist(logger):
    logger.info("=" * 50)
    logger.info("Generating playlists")
    logger.info("=" * 50)

    # 读取所有过滤后的频道
    all_channels = []
    for sf in sorted(FILTERED_DIR.glob("*.m3u*"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            channels = parse_m3u(sf.read_text(encoding='utf-8'))
            all_channels.extend(channels)
            logger.info("Parsed " + str(len(channels)) + " from " + sf.name)
        except Exception as e:
            logger.warning("Failed: " + sf.name)

    # 去重
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
    cache = load_cache()
    if skip_validation:
        logger.info("SKIP_VALIDATION=1, using cached results")
        for ch in all_channels:
            ch["is_valid"] = cache.get(ch["url"], False)
    else:
        all_channels, cache = batch_validate(all_channels, logger)

    # 分类所有频道
    categorized = {}
    hk_categorized = {}
    
    for ch in all_channels:
        if not ch["is_valid"]:
            continue
        cat = categorize(ch["name"], ch["group"])
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(ch)
        
        # HK 专区
        if is_hk_region(ch["name"], ch["group"]):
            if cat not in hk_categorized:
                hk_categorized[cat] = []
            hk_categorized[cat].append(ch)

    logger.info("Total valid: " + str(sum(len(v) for v in categorized.values())))
    logger.info("Total HK valid: " + str(sum(len(v) for v in hk_categorized.values())))
    logger.info("Total categories: " + str(len(categorized)))

    order = ["📺 TVB", "📺 ViuTV", "📺 RTHK", "📺 HOY TV", "📺 Now TV", "📺 有线电视", "📺 凤凰卫视", "📺 香港其他", "🇹🇼 台湾", "🇲🇴 澳门", "📰 新闻", "🎬 电影", "⚽ 体育", "🧸 儿童", "🎭 综艺", "📺 纪录片", "🎵 音乐", "🌐 其他"]
    def sort_key(c): return (0, order.index(c)) if c in order else (1, c)

    # ========== HK 频道列表 ==========
    total_hk = sum(len(v) for v in hk_categorized.values())
    
    hk_lines = ['#EXTM3U x-tvg-url="' + EPG_URL + '"',
                '#PLAYLIST:HK & TW IPTV ' + datetime.now().strftime('%Y-%m-%d'),
                '# Total: ' + str(total_hk) + ' channels, ' + str(len(hk_categorized)) + ' categories',
                '']
    
    for cat, chs in sorted(hk_categorized.items(), key=lambda x: sort_key(x[0])):
        hk_lines.append('#EXTGRP:' + cat + ' (' + str(len(chs)) + ')')
        for ch in chs:
            hk_lines.extend([ch["raw_extinf"], ch["url"]])
        hk_lines.append('')
    
    hk_file = OUTPUT_DIR / "hk_merged.m3u"
    hk_file.write_text('\n'.join(hk_lines), encoding='utf-8')
    logger.info("HK Playlist -> " + str(hk_file) + " (" + str(total_hk) + " channels)")

    # ========== 全部频道列表 ==========
    total_all = sum(len(v) for v in categorized.values())
    all_lines = ['#EXTM3U x-tvg-url="' + EPG_URL + '"',
                 '#PLAYLIST:All IPTV ' + datetime.now().strftime('%Y-%m-%d'),
                 '# Total: ' + str(total_all) + ' channels, ' + str(len(categorized)) + ' categories',
                 '']

    for cat, chs in sorted(categorized.items(), key=lambda x: sort_key(x[0])):
        all_lines.append('#EXTGRP:' + cat + ' (' + str(len(chs)) + ')')
        for ch in chs[:100]:
            all_lines.extend([ch["raw_extinf"], ch["url"]])
        if len(chs) > 100:
            all_lines.append('# ... and ' + str(len(chs) - 100) + ' more')
        all_lines.append('')

    all_file = OUTPUT_DIR / "all_merged.m3u"
    all_file.write_text('\n'.join(all_lines), encoding='utf-8')
    logger.info("ALL Playlist -> " + str(all_file) + " (" + str(total_all) + " channels)")

    return {
        "hk": {"file": str(hk_file), "channels": total_hk, "groups": len(hk_categorized)},
        "all": {"file": str(all_file), "channels": total_all, "groups": len(categorized)}
    }


def main():
    logger = setup_logging(LOG_DIR, "generate")
    return generate_playlist(logger)


if __name__ == "__main__":
    main()
