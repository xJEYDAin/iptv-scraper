#!/usr/bin/env python3
"""Shared utilities for IPTV Scraper"""
import re
import sys
import logging
from datetime import datetime
from pathlib import Path


def setup_logging(log_dir, prefix):
    """Setup logging to file and stdout."""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime('%Y%m%d')
    log_file = str(log_dir / (prefix + "_" + today_str + ".log"))
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
    """Parse M3U content and return list of channel dicts."""
    channels = []
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf = line
            name = line.split(',', 1)[1].strip() if ',' in line else ""
            tvg_name = re.search(r'tvg-name="([^"]*)"', line)
            tvg_logo = re.search(r'tvg-logo="([^"]*)"', line)
            group = re.search(r'group-title="([^"]*)"', line)
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    channels.append({
                        "name": name,
                        "tvg_name": tvg_name.group(1) if tvg_name else name,
                        "tvg_logo": tvg_logo.group(1) if tvg_logo else "",
                        "group": group.group(1) if group else "",
                        "url": url,
                        "raw_extinf": extinf
                    })
                    i += 2
                    continue
        i += 1
    return channels
