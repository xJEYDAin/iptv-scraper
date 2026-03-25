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

# Create directories if not exist
for d in [SOURCES_DIR, FILTERED_DIR, OUTPUT_DIR, CACHE_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)
