#!/usr/bin/env python3
"""Legacy compatibility layer - re-exports from refactored modules.

This allows old code to keep working while new code uses the refactored modules.
"""
# validators
from validate.validators import (
    validate_url,
    validate_batch,
    validate_url_head_first,
    check_url,
)
# cache
from validate.cache import (
    ChannelCache,
    load_cache,
    save_cache,
)
# whitelist
from lib.whitelist import (
    is_whitelisted,
    is_hk_cdn_whitelisted,
    HK_CDN_PATTERNS,
    HK_CDN_WHITELIST_PATTERNS,
)
# helpers (re-exports from utils)
from lib.helpers import (
    load_aliases,
    normalize_channel_name,
    setup_logging,
    parse_m3u,
    fetch_with_retry,
    fetch_sources_rate_limited,
)
# group
from group.categorizer import (
    is_hk_region,
    categorize,
)
# output
from output.playlist import (
    generate_playlist,
    build_extinf,
)
