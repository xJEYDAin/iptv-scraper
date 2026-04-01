#!/usr/bin/env python3
"""IPTV Source Fetcher"""
import sys
from datetime import datetime
from pathlib import Path

# Import shared config
sys.path.insert(0, str(Path(__file__).parent))
from config import SOURCES_DIR, LOG_DIR
from lib.helpers import setup_logging, fetch_sources_rate_limited

SOURCES = [
    # === 最高优先：香港本地源 ===
    {
        "name": "sammy0101",
        "url": "https://raw.gh.registry.cyou/sammy0101/hk-iptv-auto/refs/heads/main/hk_live.m3u",
        "priority": 1
    },
    # === 高优先：香港/台湾新源（2026更新）===
    # dongyubin-iptv: 仓库URL已404，暂时移除
    {
        "name": "zhi35-iptv",
        "url": "https://live.zhi35.com/iptv.m3u",
        "priority": 2
    },
    # === 中优先：i18n + 补充源 ===
    {
        "name": "iptv-org",
        "url": "https://iptv-org.github.io/iptv/index.m3u",
        "priority": 4
    },
    {
        "name": "hujingguang-iptv",
        "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8",
        "priority": 4
    },
    # === 低优先：Free-TV 各地区 ===
    {
        "name": "free-tv-hk",
        "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/lists/hong_kong.md",
        "priority": 5
    },
    {
        "name": "free-tv-tw",
        "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/lists/taiwan.md",
        "priority": 5
    },
    {
        "name": "free-tv-cn",
        "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/lists/china.md",
        "priority": 5
    },
    {
        "name": "free-tv-jp",
        "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/lists/japan.md",
        "priority": 5
    },
    {
        "name": "free-tv-kr",
        "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/lists/korea.md",
        "priority": 5
    },
    {
        "name": "vbskycn-iptv4",
        "url": "https://live.zbds.top/tv/iptv4.m3u",
        "priority": 5
    },
    {
        "name": "free-tv-us",
        "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/lists/usa.md",
        "priority": 6
    },
    {
        "name": "free-tv-uk",
        "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/lists/uk.md",
        "priority": 6
    }
]

def save_source_result(result, logger):
    """Save fetched source content to file. Called after fetch_with_retry succeeds."""
    name = result.get("name", "?")
    url = result.get("url", "")
    if not result.get("success") or "content" not in result:
        logger.error(f"FAILED {name} - {result.get('error', 'unknown')}")
        return result

    content = result["content"]
    today = datetime.now().strftime('%Y%m%d')
    filename = SOURCES_DIR / (name + "_" + today + ".m3u")
    filename.write_text(content, encoding='utf-8')
    count = content.count('#EXTINF:')
    logger.info(f"OK {name}: {count} channels -> {filename}")

    return {
        "name": name,
        "file": str(filename),
        "count": count,
        "success": True
    }


def main():
    logger = setup_logging(LOG_DIR, "fetch")
    logger.info("=" * 50)
    logger.info("Starting IPTV source fetch")
    logger.info("=" * 50)

    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    # Fix #2: rate-limited + retry + concurrency cap
    # max_workers=5 concurrent, 0.5s delay between requests, 3 retries with exponential backoff
    raw_results = fetch_sources_rate_limited(SOURCES, logger,
                                              max_workers=5,
                                              delay=0.5)

    # Save successful fetches to disk
    results = []
    for r in raw_results:
        saved = save_source_result(r, logger)
        results.append(saved)

    success_count = sum(1 for r in results if r["success"])
    total_count = sum(r.get("count", 0) for r in results if r["success"])

    logger.info("=" * 50)
    logger.info("Fetch complete: " + str(success_count) + "/" + str(len(SOURCES)) + " success")
    logger.info("Total channels: " + str(total_count))

    return results


if __name__ == "__main__":
    main()
