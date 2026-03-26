#!/usr/bin/env python3
"""IPTV Filter - 筛选港台频道"""
import sys
from datetime import datetime
from pathlib import Path

from config import SOURCES_DIR, FILTERED_DIR, LOG_DIR
from utils import setup_logging, parse_m3u

WHITELIST_KEYWORDS = [
    "TVB", "Jade", "Pearl", "翡翠", "明珠", "无线", "新闻台", "J2",
    "ViuTV", "ViuTVsix", "Viu TV",
    "RTHK", "港台", "HOY",
    "Now TV", "Nownews", "Now直播", "Now财经",
    "Cable", "有线", "开电视",
    "凤凰卫视", "凤凰", "星空", "Star TV", "StarTV",
    "TVBS", "台视", "中视", "华视", "民视", "东森", "三立", "非凡", "大爱", "公视",
    "澳门", "澳視", "macau",
]

BLACKLIST_KEYWORDS = [
    "成人", "18+", "AV", "色情", "情色", "sexy", "xxx",
    "CCTV", "央视频",
    "浙江卫视", "江苏卫视", "四川卫视", "北京卫视", "上海卫视", "湖南卫视",
    "广东卫视", "广东台",
    "HBO", "Cinemax", "Warner", "Disney",
    "BBC", "CNN", "DW", "Al Jazeera",
    "ESPN", "Fox Sports",
]

FORCE_WHITELIST = ["TVB", "Jade", "Pearl", "ViuTV", "RTHK", "Now", "Cable", "凤凰", "TVBS", "台视", "中视", "华视", "民视", "东森", "三立", "无线", "新闻"]
FORCE_BLACKLIST = ["成人", "18+", "AV", "色情", "sexy", "xxx", "CCTV"]


def is_hk_channel(channel):
    name = channel.get("name", "") or ""
    tvg_name = channel.get("tvg_name", "") or ""
    group = channel.get("group", "") or ""
    full_text = (name + " " + tvg_name + " " + group).lower()
    
    for keyword in FORCE_BLACKLIST:
        if keyword.lower() in full_text:
            return False, "force_blacklist"
    
    for keyword in FORCE_WHITELIST:
        if keyword.lower() in full_text:
            for kw in BLACKLIST_KEYWORDS:
                if kw.lower() in full_text:
                    return False, "has_blacklist"
            return True, "force_whitelist"
    
    whitelist_match = any(kw.lower() in full_text for kw in WHITELIST_KEYWORDS)
    blacklist_match = any(kw.lower() in full_text for kw in BLACKLIST_KEYWORDS)
    
    if whitelist_match and not blacklist_match:
        return True, "whitelist_match"
    
    return False, "not_matched"


def filter_file(filepath, logger):
    logger.info("Filtering: " + filepath.name)
    
    try:
        content = filepath.read_text(encoding='utf-8')
        channels = parse_m3u(content)
        
        kept = []
        removed = []
        
        for channel in channels:
            is_hk, reason = is_hk_channel(channel)
            if is_hk:
                kept.append(channel)
            else:
                removed.append((channel.get("name") or channel.get("tvg_name", "Unknown"), reason))
        
        logger.info(f"  Kept: {len(kept)}, Removed: {len(removed)}")
        
        if kept:
            output_path = FILTERED_DIR / filepath.name
            output_path.write_text(content, encoding='utf-8')
            logger.info(f"  -> {output_path.name} ({len(kept)} channels)")
        
        return kept, removed
        
    except Exception as e:
        logger.error("  Error: " + str(e))
        return [], []


def main():
    logger = setup_logging(LOG_DIR, "filter")
    logger.info("=" * 50)
    logger.info("Starting HK/TW/MO channel filter")
    logger.info("=" * 50)
    
    FILTERED_DIR.mkdir(parents=True, exist_ok=True)
    
    source_files = list(SOURCES_DIR.glob("*.m3u*"))
    
    if not source_files:
        logger.error("No source files found!")
        return
    
    total_kept = 0
    total_removed = 0
    
    for filepath in sorted(source_files):
        kept, removed = filter_file(filepath, logger)
        total_kept += len(kept)
        total_removed += len(removed)
    
    logger.info("=" * 50)
    logger.info(f"Filter complete: {total_kept} kept, {total_removed} removed")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
