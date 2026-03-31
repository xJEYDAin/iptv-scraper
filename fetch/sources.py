#!/usr/bin/env python3
"""Data source management for IPTV scraper."""
from pathlib import Path
from typing import List, Dict

SOURCES_DIR = Path(__file__).parent.parent / "sources"


def get_sources() -> List[Dict[str, str]]:
    """Get list of data sources from sources/ directory.
    
    Returns:
        list of dicts with 'name' and 'url' keys
    """
    # Sources are defined via .m3u files in sources/ directory
    # This is a simple implementation - sources are already fetched
    # by fetch_sources.py
    return []


def list_source_files() -> List[Path]:
    """List all M3U source files in sources/ directory."""
    if not SOURCES_DIR.exists():
        return []
    return sorted(SOURCES_DIR.glob("*.m3u*"))
