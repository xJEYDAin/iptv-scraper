#!/usr/bin/env python3
"""Shared configuration for IPTV Scraper"""
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

SOURCES_DIR = BASE_DIR / "sources"
FILTERED_DIR = BASE_DIR / "filtered"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / "cache"
LOG_DIR = BASE_DIR / "logs"

CACHE_FILE = CACHE_DIR / "validation_cache.json"

MIN_SPEED_KB = 30
SPEEDTEST_TIMEOUT = 5
SPEEDTEST_WORKERS = 10
SPEEDTEST_USE_CURL = True
ENABLE_SPEEDTEST = True
SORT_BY_SPEED = True

EPG_URL = "https://epg.pw/pp.xml"

for d in [SOURCES_DIR, FILTERED_DIR, OUTPUT_DIR, CACHE_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)
