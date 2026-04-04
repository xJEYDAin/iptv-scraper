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

# ─── Tier 2: Extended whitelist - adds global CDN + new HK patterns ───────────
# Tier 2 inherits Tier 1 patterns via the combined EXTENDED_WHITELIST_PATTERNS below.

_TIER2_NEW_PATTERNS: List[Pattern] = [
    # New HK-specific patterns not in Tier 1
    re.compile(r'^https?://([^/]+\.)*rthktv\.com/', re.IGNORECASE),   # RTHK official
    re.compile(r'^https?://hoytv\.com/', re.IGNORECASE),              # HOY TV
    # Domestic reliable CDN / mirrors (not in Tier 1)
    re.compile(r'^https?://v2h\.jdshipin\.com/'),
    re.compile(r'^https?://php\.jdshipin\.com/'),
    # Global CDN (official / highly reliable)
    re.compile(r'^https?://([^/]+\.)*akamaized\.net/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*cloudfront\.net/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*fastly\.net/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*直播\.tv/', re.IGNORECASE),
    re.compile(r'^https?://([^/]+\.)*pstatic\.net/', re.IGNORECASE),
]

# Combined: Tier 1 + Tier 2 (no duplicates)
EXTENDED_WHITELIST_PATTERNS: List[Pattern] = HK_CDN_PATTERNS + _TIER2_NEW_PATTERNS

HK_CDN_WHITELIST_PATTERNS = HK_CDN_PATTERNS


def is_whitelisted(url: str) -> bool:
    """Check if URL matches any whitelist pattern."""
    for pattern in EXTENDED_WHITELIST_PATTERNS:
        if pattern.match(url):
            return True
    return False


is_hk_cdn_whitelisted = is_whitelisted

# 代理域名黑名单（返回网页而非视频流）
PROXY_BLACKLIST_DOMAINS = [
    "jdshipin.com",
    "jiduo.me",
    "v2h.jdshipin.com",
    "php.jdshipin.com",
]


def is_proxy_domain(url: str) -> bool:
    """检测是否为代理/播放器页面 URL"""
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc.lower()
        return any(proxy in domain for proxy in PROXY_BLACKLIST_DOMAINS)
    except:
        return False
