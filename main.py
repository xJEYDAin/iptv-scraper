#!/usr/bin/env python3
"""HK IPTV Scraper - Main Entry Point"""
import sys
from datetime import datetime
from pathlib import Path

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from fetch_sources import main as fetch_main
from filter_hk import main as filter_main
from validate_and_merge import main as validate_main
from generate_playlist import main as generate_main
from lib.helpers import setup_logging

LOG_DIR = Path(__file__).parent / "logs"

def main():
    logger = setup_logging(LOG_DIR, "main")
    
    banner = """
╔══════════════════════════════════════════════════╗
║       HK IPTV Auto Scraper v3.0                ║
║   Fetch → Filter → Validate → SpeedTest → Gen   ║
╚══════════════════════════════════════════════════╝
    """
    logger.info(banner)
    
    start_time = datetime.now()
    logger.info("Start: " + start_time.strftime('%Y-%m-%d %H:%M:%S'))
    
    # Step 1: Fetch
    logger.info("\n[Step 1/5] Fetching sources...")
    fetch_results = fetch_main()
    
    # Step 2: Filter HK
    logger.info("\n[Step 2/5] Filtering HK channels...")
    filter_results = filter_main()
    
    # Step 3: Validate & Merge
    logger.info("\n[Step 3/5] Validating and merging...")
    merged_channels = validate_main()
    
    # Step 4: Generate playlists (now includes speedtest + VLC opts)
    logger.info("\n[Step 4/5] Generating playlists with speedtest + VLC optimization...")
    generate_results = generate_main()
    
    # Step 5: Done
    logger.info("\n[Step 5/5] Complete!")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("\n" + "=" * 50)
    logger.info("Done in {:.1f} seconds".format(duration))
    logger.info("=" * 50)
    
    return {
        "fetch": fetch_results,
        "filter": filter_results,
        "merged": merged_channels,
        "generate": generate_results
    }

if __name__ == "__main__":
    main()
