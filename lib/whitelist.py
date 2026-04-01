#!/usr/bin/env python3
"""Centralized whitelist management for HK/TW/MO CDN domains."""
import re
from typing import List, Pattern

# ─── Tier 1: Extended HK/TW/MO CDN Patterns ───────────────────────────────────

HK_CDN_PATTERNS: List[Pattern] = [
    re.compile(r'^https?://([^/]+\.)*hkdtmb\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*tdm\.com\.mo/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*viutv\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*now\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*tvb\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*rthk\.hk/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*hkcable\.com\.hk/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*cable-tvc\.com/', re.IGNORECASE),
    re.compile(r'^https?://61\.238\.\d+\.\d+/'),
    re.compile(r'^https?://116\.199\.\d+\.\d+'),
    re.compile(r'^https?://202\.181\.\d+\.\d+/'),
    re.compile(r'^https?://203\.186\.\d+\.\d+/'),
    re.compile(r'^https?://1\.32\.\d+\.\d+/'),
    re.compile(r'^https?://42\.2\.\d+\.\d+/'),
    re.compile(r'^https?://([^/]+\.)*jdshipin\.com/'),
    re.compile(r'^https?://([^/]+\.)*163189\.xyz/'),
    re.compile(r'^https?://([^/]+\.)*jiduo\.me/'),
    re.compile(r'^https?://aktv\.top/'),
    re.compile(r'^https?://122\.152\.\d+\.\d+/'),
    re.compile(r'^https?://8\.138\.\d+\.\d+/'),
    re.compile(r'^https?://fm1077\.serv00\.net/'),
]

# ─── Tier 2: Extended whitelist - Reliable CDN / mirror sites ─────────────────

EXTENDED_WHITELIST_PATTERNS: List[Pattern] = [
    # HK CDN
    re.compile(r'^https?://([^/]+\.)*cdn\.hkdtmb\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*hkdtmb\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*tdm\.com\.mo/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*viutv\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*now\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*tvb\.com/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*rthk\.hk/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*rthktv\.com/', re.IGNORECASE),          # RTHK official
    re.compile(r'^https?://([^/]+\.)*hkcable\.com\.hk/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*cable-tvc\.com/', re.IGNORECASE),
    re.compile(r'^https?://hoytv\.com/', re.IGNORECASE),                     # HOY TV
    re.compile(r'^https?://([^/]+\.)*cable-tvc\.com/', re.IGNORECASE),

    # HK IP ranges (static CDN)
    re.compile(r'^https?://61\.238\.\d+\.\d+/'),
    re.compile(r'^https?://116\.199\.\d+\.\d+'),
    re.compile(r'^https?://202\.181\.\d+\.\d+/'),
    re.compile(r'^https?://203\.186\.\d+\.\d+/'),
    re.compile(r'^https?://1\.32\.\d+\.\d+/'),
    re.compile(r'^https?://42\.2\.\d+\.\d+/'),
    re.compile(r'^https?://122\.152\.\d+\.\d+/'),
    re.compile(r'^https?://8\.138\.\d+\.\d+/'),

    # Domestic reliable CDN / mirrors
    re.compile(r'^https?://([^/]+\.)*jdshipin\.com/'),
    re.compile(r'^https?://([^/]+\.)*163189\.xyz/'),
    re.compile(r'^https?://v2h\.jdshipin\.com/'),
    re.compile(r'^https?://php\.jdshipin\.com/'),
    re.compile(r'^https?://([^/]+\.)*jiduo\.me/'),
    re.compile(r'^https?://aktv\.top/'),
    re.compile(r'^https?://fm1077\.serv00\.net/'),

    # Global CDN (official / highly reliable)
    re.compile(r'^https?://([^/]+\.)*akamaized\.net/', re.IGNORECASE),       # Akamai CDN
    re.compile(r'^https?://([^/]+\.)*cloudfront\.net/', re.IGNORECASE),      # AWS CloudFront
    re.compile(r'^https?://([^/]+\.)*fastly\.net/', re.IGNORECASE),          # Fastly CDN
    re.compile(r'^https?://([^/]+\.)*直播\.tv/', re.IGNORECASE),             # Chinese streaming CDN
    re.compile(r'^https?://([^/]+\.)*pstatic\.net/', re.IGNORECASE),        # Naver/CDN Park
]

HK_CDN_WHITELIST_PATTERNS = HK_CDN_PATTERNS


def is_whitelisted(url: str) -> bool:
    """Check if URL matches any whitelist pattern."""
    for pattern in EXTENDED_WHITELIST_PATTERNS:
        if pattern.match(url):
            return True
    return False


is_hk_cdn_whitelisted = is_whitelisted
