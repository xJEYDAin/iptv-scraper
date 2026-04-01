#!/usr/bin/env python3
"""IPTV Filter - 港台频道过滤（宽松模式）"""
import sys
from datetime import datetime
from pathlib import Path

from config import SOURCES_DIR, FILTERED_DIR, LOG_DIR
from lib.helpers import setup_logging, parse_m3u

BLACKLIST_KEYWORDS = [
    "成人", "18+", "AV", "色情", "情色", "sexy", "xxx",
    "onlyfans", "porn", "redtube", "xvideo",
]

FORCE_BLACKLIST = ["成人", "18+", "AV", "色情", "sexy", "xxx", "porn"]


def is_valid_channel(channel):
    name = channel.get("name", "") or ""
    tvg_name = channel.get("tvg_name", "") or ""
    group = channel.get("group", "") or ""
    full_text = (name + " " + tvg_name + " " + group).lower()
    
    for keyword in FORCE_BLACKLIST:
        if keyword.lower() in full_text:
            return False, "adult_blacklist"
    
    return True, "valid"


def filter_file(filepath, logger):
    logger.info("Filtering: " + filepath.name)
    
    try:
        content = filepath.read_text(encoding='utf-8')
        channels = parse_m3u(content)
        
        kept = []
        removed = []
        
        for channel in channels:
            is_valid, reason = is_valid_channel(channel)
            if is_valid:
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
    logger.info("Starting channel filter (permissive mode)")
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
