#!/usr/bin/env python3
"""Shared utilities for IPTV Scraper"""
import re
import sys
import logging
from datetime import datetime
from pathlib import Path


def load_aliases(alias_file=None):
    """Load channel alias mapping from alias.txt.
    
    Format: 原始名称 -> 标准名称
    Returns a dict: {alias_name: canonical_name}
    """
    if alias_file is None:
        alias_file = Path(__file__).parent / "alias.txt"
    else:
        alias_file = Path(alias_file)
    
    if not alias_file.exists():
        return {}
    
    aliases = {}
    try:
        content = alias_file.read_text(encoding='utf-8')
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '->' in line:
                parts = line.split('->', 1)
                alias_name = parts[0].strip()
                canonical = parts[1].strip()
                if alias_name and canonical:
                    aliases[alias_name] = canonical
    except Exception as e:
        logging.warning(f"Failed to load aliases from {alias_file}: {e}")
    
    return aliases


def normalize_channel_name(name, aliases):
    """Normalize a channel name using alias mapping.
    
    If the name matches an alias, return the canonical name.
    Otherwise return the original name stripped.
    """
    if not name:
        return name
    name_stripped = name.strip()
    return aliases.get(name_stripped, name_stripped)


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
