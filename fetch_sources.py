#!/usr/bin/env python3
"""IPTV Source Fetcher"""
import requests
import sys
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import shared config
sys.path.insert(0, str(Path(__file__).parent))
from config import SOURCES_DIR, LOG_DIR
from utils import setup_logging

SOURCES = [
    {
        "name": "sammy0101",
        "url": "https://raw.gh.registry.cyou/sammy0101/hk-iptv-auto/refs/heads/main/hk_live.m3u",
        "priority": 1
    },
    {
        "name": "nthack",
        "url": "https://raw.githubusercontent.com/nthack/IPTVM3U/master/HKTW.m3u",
        "priority": 2
    },
    {
        "name": "imdazui-hktw",
        "url": "https://raw.githubusercontent.com/imDazui/Tvlist-awesome-m3u-m3u8/master/m3u/%E5%8F%B0%E6%B9%BE%E9%A6%99%E6%B8%AF%E6%BE%B3%E9%97%A8202506.m3u",
        "priority": 3
    },
    {
        "name": "iptv-org",
        "url": "https://iptv-org.github.io/iptv/index.m3u",
        "priority": 4
    }
]

TIMEOUT = 10

def fetch_source(source, logger, session=None):
    name = source["name"]
    url = source["url"]
    
    logger.info("Fetching: " + name + " (" + url + ")")
    
    if session is None:
        session = requests.Session()
    
    try:
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        content = response.text
        today = datetime.now().strftime('%Y%m%d')
        filename = SOURCES_DIR / (name + "_" + today + ".m3u")
        filename.write_text(content, encoding='utf-8')
        
        count = content.count('#EXTINF:')
        logger.info("OK " + name + ": " + str(count) + " channels -> " + str(filename))
        
        return {
            "name": name,
            "file": str(filename),
            "count": count,
            "success": True
        }
        
    except requests.exceptions.Timeout:
        logger.error("TIMEOUT " + name + " (" + str(TIMEOUT) + "s)")
        return {"name": name, "success": False, "error": "timeout"}
    except requests.exceptions.RequestException as e:
        logger.error("FAILED " + name + " - " + str(e))
        return {"name": name, "success": False, "error": str(e)}
    except Exception as e:
        logger.error("ERROR " + name + " - " + str(e))
        return {"name": name, "success": False, "error": str(e)}

def main():
    logger = setup_logging(LOG_DIR, "fetch")
    logger.info("=" * 50)
    logger.info("Starting IPTV source fetch")
    logger.info("=" * 50)
    
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    
    # P0-2: parallel fetch with shared session (P0-3)
    session = requests.Session()
    results = []
    with ThreadPoolExecutor(max_workers=len(SOURCES)) as executor:
        futures = {executor.submit(fetch_source, source, logger, session): source for source in SOURCES}
        for future in as_completed(futures):
            results.append(future.result())
    
    success_count = sum(1 for r in results if r["success"])
    total_count = sum(r.get("count", 0) for r in results if r["success"])
    
    logger.info("=" * 50)
    logger.info("Fetch complete: " + str(success_count) + "/" + str(len(SOURCES)) + " success")
    logger.info("Total channels: " + str(total_count))
    
    return results

if __name__ == "__main__":
    main()
