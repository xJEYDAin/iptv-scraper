#!/usr/bin/env python3
"""Shared utilities for IPTV Scraper - thin shim to refactored modules.

All logic moved to:
- utils/whitelist.py   - CDN whitelist
- utils/helpers.py    - general helpers
- validate/cache.py   - cache management
- validate/validators.py - URL validation
"""
# Re-export everything for backward compatibility
from lib.whitelist import (
    is_whitelisted,
    is_hk_cdn_whitelisted,
    HK_CDN_PATTERNS,
    HK_CDN_WHITELIST_PATTERNS,
)
from lib.helpers import (
    load_aliases,
    normalize_channel_name,
    setup_logging,
    parse_m3u,
    fetch_with_retry,
    fetch_sources_rate_limited,
)
from validate.cache import load_cache, save_cache
from validate.validators import validate_url_head_first

__all__ = [
    'is_whitelisted', 'is_hk_cdn_whitelisted', 'HK_CDN_PATTERNS', 'HK_CDN_WHITELIST_PATTERNS',
    'load_aliases', 'normalize_channel_name', 'setup_logging', 'parse_m3u',
    'fetch_with_retry', 'fetch_sources_rate_limited',
    'load_cache', 'save_cache',
    'validate_url_head_first',
]
