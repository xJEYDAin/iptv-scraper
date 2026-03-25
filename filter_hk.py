#!/usr/bin/env python3
from config import SOURCES_DIR, FILTERED_DIR, LOG_DIR
"""
IPTV Filter - 筛选香港频道
"""
import re
import logging
import sys
from datetime import datetime
from pathlib import Path

WHITELIST_KEYWORDS = [
    "TVB", "Jade", "Pearl", "翡翠", "明珠", "无线", "新闻台", "J2", 
    "ViuTV", "ViuTVsix", "Viu TV",
    "RTHK", "港台", "HOY", 
    "Now TV", "Nownews", "Now直播", "Now财经",
    "Cable", "有线", "开电视", 
    "凤凰卫视", "凤凰", "星空", "Star TV", "StarTV",
    "AXN", "Sony", "BBC", "CNN", "DW",
    "HBO", "Cinemax", "Warner", "Disney",
    "体育", "体育台", "ESPN", "Fox Sports",
    "Movie", "电影", "影业",
    "高清", "HD",
    "珠江", "广州", "珠海", "深圳", "佛山", "东莞"
]

BLACKLIST_KEYWORDS = [
    "成人", "18+", "AV", "色情", "情色",
    "国内", "大陆", "CCTV", "央视频",
    "广东卫视", "广东台",
    "福建", "浙江", "江苏", "四川", "北京", "上海", "湖南",
    "山东", "河南", "河北", "湖北", "安徽", "辽宁", "吉林", "黑龙江"
]

FORCE_WHITELIST = [
    "TVB", "Jade", "Pearl", "ViuTV", "RTHK", "Now", "Cable", "凤凰"
]

FORCE_BLACKLIST = [
    "成人", "18+", "AV", "色情"
]


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime('%Y%m%d')
    log_file = str(LOG_DIR / ("filter_" + today_str + ".log"))
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
            match = re.search(r'group-title="([^"]*)"', line)
            group = match.group(1) if match else ""
            
            match = re.search(r'tvg-name="([^"]*)"', line)
            tvg_name = match.group(1) if match else ""
            
            if ',' in line:
                name = line.split(',', 1)[1].strip()
            else:
                name = tvg_name or ""
            
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    channels.append({
                        "name": name,
                        "tvg_name": tvg_name,
                        "group": group,
                        "url": url,
                        "raw_extinf": line
                    })
                    i += 2
                    continue
        i += 1
    
    return channels

def is_hk_channel(channel):
    name = channel["name"].lower()
    tvg_name = channel["tvg_name"].lower()
    group = channel["group"].lower()
    full_text = (name + " " + tvg_name + " " + group).lower()
    
    for keyword in FORCE_BLACKLIST:
        if keyword.lower() in full_text:
            return False, "force_blacklist"
    
    for keyword in FORCE_WHITELIST:
        if keyword.lower() in full_text:
            for kw in BLACKLIST_KEYWORDS:
                if kw.lower() in full_text:
                    return False, "has_blacklist_keyword"
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
                removed.append((channel, reason))
        
        output_lines = ['#EXTM3U']
        for ch in kept:
            output_lines.append(ch["raw_extinf"])
            output_lines.append(ch["url"])
        
        output_content = '\n'.join(output_lines)
        
        output_file = FILTERED_DIR / filepath.name
        output_file.write_text(output_content, encoding='utf-8')
        
        logger.info("Kept " + str(len(kept)) + "/" + str(len(channels)) + " channels -> " + output_file.name)
        
        return {
            "file": str(filepath),
            "total": len(channels),
            "kept": len(kept),
            "removed": len(removed),
            "success": True
        }
        
    except Exception as e:
        logger.error("Failed: " + str(e))
        return {"file": str(filepath), "success": False, "error": str(e)}

def main():
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("Starting HK channel filtering")
    logger.info("=" * 50)
    
    FILTERED_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y%m%d')
    source_files = list(SOURCES_DIR.glob("*_" + today + ".m3u*"))
    
    if not source_files:
        source_files = sorted(SOURCES_DIR.glob("*.m3u*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if source_files:
            logger.warning("No today's file, using latest: " + source_files[0].name)
            source_files = [source_files[0]]
        else:
            logger.error("No source files found!")
            return []
    
    results = []
    for f in source_files:
        result = filter_file(f, logger)
        results.append(result)
    
    total_kept = sum(r.get("kept", 0) for r in results)
    total_removed = sum(r.get("removed", 0) for r in results)
    
    logger.info("=" * 50)
    logger.info("Filtering complete: " + str(len(results)) + " files")
    logger.info("Kept: " + str(total_kept) + ", Removed: " + str(total_removed))
    
    return results

if __name__ == "__main__":
    main()
