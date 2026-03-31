#!/usr/bin/env python3
"""Centralized whitelist management for HK/TW/MO CDN domains."""
import re
from typing import List, Pattern

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

HK_CDN_WHITELIST_PATTERNS = HK_CDN_PATTERNS


def is_whitelisted(url: str) -> bool:
    for pattern in HK_CDN_PATTERNS:
        if pattern.match(url):
            return True
    return False


is_hk_cdn_whitelisted = is_whitelisted
