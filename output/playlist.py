#!/usr/bin/env python3
"""M3U playlist generation."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from config import OUTPUT_DIR, EPG_URL
from group.categorizer import categorize, is_hk_region

logger = logging.getLogger(__name__)

EPG_URL = "https://epg.pw/pp.xml"

# Category sort order
CATEGORY_ORDER = [
    "📺 TVB", "📺 ViuTV", "📺 RTHK", "📺 HOY TV", "📺 Now TV",
    "📺 有线电视", "📺 凤凰卫视", "📺 香港其他",
    "🇹🇼 台湾", "🇲🇴 澳门",
    "📰 新闻", "🎬 电影", "⚽ 体育", "🧸 儿童", "🎭 综艺",
    "📺 纪录片", "🎵 音乐", "🌐 其他"
]


def build_extinf(ch: dict) -> str:
    """Rebuild EXTINF line with tvg-logo injected via logo_map.
    
    Priority: logo_map fuzzy match > existing tvg_logo > ''
    """
    from logo_map import get_logo_fuzzy

    # 1. Determine logo
    mapped_logo = get_logo_fuzzy(ch["name"])
    if mapped_logo:
        logo = mapped_logo
    elif ch.get("tvg_logo"):
        logo = ch["tvg_logo"]
    else:
        logo = ""

    # 2. Determine group
    group = ch.get("cat", "") or ch.get("group", "") or ""

    # 3. tvg-name
    tvg_name = ch.get("tvg_name", "") or ch.get("name", "") or ""

    # 4. Build EXTINF
    attrs = []
    if tvg_name:
        attrs.append(f'tvg-name="{tvg_name}"')
    if logo:
        attrs.append(f'tvg-logo="{logo}"')
    if group:
        attrs.append(f'group-title="{group}"')

    attr_str = " ".join(attrs)
    return f"#EXTINF:-1 {attr_str},{ch['name']}"


def sort_key(cat: str) -> tuple:
    """Sort key for category ordering."""
    try:
        return (0, CATEGORY_ORDER.index(cat))
    except ValueError:
        return (1, cat)


def generate_playlist(valid_chs: List[dict], min_speed_kb: int) -> Dict[str, dict]:
    """Generate HK and ALL playlists from valid channels.
    
    Returns:
        dict with keys 'hk' and 'all', each containing file path and channel count
    """
    # Categorize
    categorized = {}
    hk_categorized = {}
    
    for ch in valid_chs:
        cat = categorize(ch["name"], ch["group"])
        ch["cat"] = cat
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(ch)
        
        if is_hk_region(ch["name"], ch["group"]):
            if cat not in hk_categorized:
                hk_categorized[cat] = []
            hk_categorized[cat].append(ch)

    total_hk = sum(len(v) for v in hk_categorized.values())
    total_all = sum(len(v) for v in categorized.values())

    # ========== HK Playlist ==========
    hk_lines = [
        '#EXTM3U x-tvg-url="' + EPG_URL + '"',
        '#EXTVLCOPT:network-caching=1000',
        '#EXTVLCOPT:live-cache=1000',
        '#EXTVLCOPT:ttl=5',
        '#PLAYLIST:HK & TW IPTV ' + datetime.now().strftime('%Y-%m-%d'),
        f'# Total: {total_hk} channels, {len(hk_categorized)} categories, min speed: {min_speed_kb} KB/s',
        '']
    
    for cat, chs in sorted(hk_categorized.items(), key=lambda x: sort_key(x[0])):
        hk_lines.append(f'#EXTGRP:{cat} ({len(chs)})')
        for ch in chs:
            speed_comment = f'# speed: {ch.get("speed_str", "N/A")}'
            hk_lines.append(speed_comment)
            hk_lines.extend([build_extinf(ch), ch["url"]])
        hk_lines.append('')
    
    hk_file = OUTPUT_DIR / "hk_merged.m3u"
    hk_file.write_text('\n'.join(hk_lines), encoding='utf-8')
    logger.info(f"HK Playlist -> {hk_file} ({total_hk} channels)")

    # ========== ALL Playlist ==========
    all_lines = [
        '#EXTM3U x-tvg-url="' + EPG_URL + '"',
        '#EXTVLCOPT:network-caching=1000',
        '#EXTVLCOPT:live-cache=1000',
        '#EXTVLCOPT:ttl=5',
        '#PLAYLIST:All IPTV ' + datetime.now().strftime('%Y-%m-%d'),
        f'# Total: {total_all} channels, {len(categorized)} categories, min speed: {min_speed_kb} KB/s',
        '']

    for cat, chs in sorted(categorized.items(), key=lambda x: sort_key(x[0])):
        all_lines.append(f'#EXTGRP:{cat} ({len(chs)})')
        for ch in chs[:100]:
            all_lines.extend([build_extinf(ch), ch["url"]])
        if len(chs) > 100:
            all_lines.append(f'# ... and {len(chs) - 100} more')
        all_lines.append('')

    all_file = OUTPUT_DIR / "all_merged.m3u"
    all_file.write_text('\n'.join(all_lines), encoding='utf-8')
    logger.info(f"ALL Playlist -> {all_file} ({total_all} channels)")

    return {
        "hk": {"file": str(hk_file), "channels": total_hk, "groups": len(hk_categorized)},
        "all": {"file": str(all_file), "channels": total_all, "groups": len(categorized)}
    }
