#!/usr/bin/env python3
"""Shared configuration for IPTV Scraper"""
from pathlib import Path

# Base directory (where this script is located)
BASE_DIR = Path(__file__).parent.resolve()

# Directories
SOURCES_DIR = BASE_DIR / "sources"
FILTERED_DIR = BASE_DIR / "filtered"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / "cache"
LOG_DIR = BASE_DIR / "logs"

# Cache file
CACHE_FILE = CACHE_DIR / "validation_cache.json"

# Speedtest settings
MIN_SPEED_KB = 30           # Minimum speed in KB/s (filter out slow links)
SPEEDTEST_TIMEOUT = 5        # Seconds per URL
SPEEDTEST_WORKERS = 10       # Parallel workers
SPEEDTEST_USE_CURL = True    # Use curl (True) or requests (False)
ENABLE_SPEEDTEST = True      # Set False to skip speed testing
SORT_BY_SPEED = True        # Sort by speed instead of alphabetically

# Create directories if not exist
for d in [SOURCES_DIR, FILTERED_DIR, OUTPUT_DIR, CACHE_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)
