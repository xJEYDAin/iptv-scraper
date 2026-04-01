#!/usr/bin/env python3
"""IPTV Validator & Merger - with tier-based layered validation."""
import logging
import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional

import requests

from config import FILTERED_DIR, OUTPUT_DIR, LOG_DIR, CACHE_DIR, CACHE_FILE
from lib.helpers import setup_logging, parse_m3u, load_aliases, normalize_channel_name
from validate.cache import load_cache, save_cache
from validate.validators import validate_url_head_first

PRIORITY = {
    "sammy0101": 1,
    "nthack": 2,
    "joker-cold": 3
}

TIMEOUT = 3
MAX_LINES_PER_CHANNEL = 3
BATCH_SIZE = 500

# ─── Validation Tiers ───────────────────────────────────────────────────────────

VALIDATE_TIERS = {
    "hk_tw_mo": {
        "name": "HK / TW / MO",
        "patterns": [
            "tvb", "viutv", "rthk", "nowtv", "hoytv", "cable",
            "凤凰", "澳视", "台视", "中视", "华视", "民视", "东森",
            "viu", "rthktv", "tdm", "tvb", "hkcable",
        ],
        "validate_days": 1,   # Daily validation
    },
    "china": {
        "name": "China Mainland",
        "patterns": [
            "cctv", "cetv", "卫视", "北京", "上海", "广东", "浙江",
            "江苏", "四川", "山东", "湖南", "安徽", "福建", "黑龙江",
            "吉林", "辽宁", "河北", "河南", "湖北", "江西", "山西",
            "陕西", "甘肃", "青海", "宁夏", "新疆", "内蒙古", "广西",
            "贵州", "云南", "海南", "天津", "重庆", "深圳",
        ],
        "validate_days": 7,   # Weekly validation
    },
    "global": {
        "name": "Global",
        "patterns": [],        # Default tier - no specific patterns
        "validate_days": 30,  # Monthly validation
    },
}


def get_url_tier(url: str) -> str:
    """Determine the validation tier for a URL based on channel name patterns."""
    # Try to extract channel name from URL (some URLs embed channel names)
    url_lower = url.lower()

    for tier_name, tier_cfg in VALIDATE_TIERS.items():
        if tier_name == "global":
            continue  # Global is the fallback
        for pattern in tier_cfg["patterns"]:
            # Match pattern in URL path or as substring
            if pattern.lower() in url_lower:
                return tier_name

    return "global"


def should_validate_url(url: str, cache: Dict) -> bool:
    """Decide if a URL should be validated based on tier and cache state.

    Returns False (skip) if:
      1. URL is in whitelist
      2. URL is cached as valid AND within tier's validate_days period
    Returns True otherwise:
      - New URL
      - URL not in cache
      - Cache expired for its tier
      - URL was previously invalid
      - FORCE_VALIDATION=1 is set
    """
    from lib.whitelist import is_whitelisted

    # 0. Force validation mode
    if os.getenv("FORCE_VALIDATION") == "1":
        return True

    # 1. Whitelist check - skip validation
    if is_whitelisted(url):
        return False

    # 2. Cache check
    today = date.today()

    if url in cache:
        entry = cache[url]

        # If previously invalid, always revalidate
        if not entry.get("valid", True):
            return True

        # Check tier-based expiration
        last_validated_str = entry.get("last_validated")
        if last_validated_str:
            try:
                last_validated = datetime.strptime(last_validated_str, "%Y-%m-%d").date()
                tier = entry.get("tier", "global")
                days_since = (today - last_validated).days
                tier_days = VALIDATE_TIERS.get(tier, {}).get("validate_days", 30)
                if days_since < tier_days:
                    return False  # Still within valid period
            except ValueError:
                pass  # Invalid date format, revalidate

    # 3. Not in cache or expired - needs validation
    return True


def get_source_priority(filename):
    for name, priority in PRIORITY.items():
        if name in filename:
            return priority
    return 99


def validate_url(url, logger, timeout=TIMEOUT, session=None):
    """Validate URL using HEAD first → GET fallback."""
    return validate_url_head_first(url, session=session, timeout=timeout, logger=logger)


def validate_and_merge(logger):
    logger.info("=" * 50)
    if os.getenv("SKIP_VALIDATION") == "1":
        logger.info("SKIP_VALIDATION=1, skipping validation and merge")
        return None
    logger.info("Starting validation and merge")
    logger.info("=" * 50)

    aliases = load_aliases()
    logger.info("Loaded " + str(len(aliases)) + " channel aliases")
    if aliases:
        logger.info("Sample aliases: " + str(dict(list(aliases.items())[:5])))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filtered_files = sorted(
        FILTERED_DIR.glob("*.m3u*"),
        key=lambda p: get_source_priority(p.name)
    )

    if not filtered_files:
        logger.error("No filtered files found!")
        return None

    logger.info("Found " + str(len(filtered_files)) + " files to process")

    cache = load_cache(CACHE_FILE)
    logger.info("Loaded cache: " + str(len(cache)) + " entries")

    session = requests.Session()

    all_channels = {}

    total_valid = 0
    total_invalid = 0
    newly_validated = 0
    skipped_validation = 0
    alias_mapped_count = 0

    today_str = date.today().strftime("%Y-%m-%d")

    for filepath in filtered_files:
        priority = get_source_priority(filepath.name)
        logger.info("Processing " + filepath.name + " (priority: " + str(priority) + ")")

        try:
            content = filepath.read_text(encoding='utf-8')
            channels = parse_m3u(content)
            logger.info("  Parsed " + str(len(channels)) + " channels")

            batch_count = 0
            for ch in channels:
                name = ch["name"] or ch["tvg_name"]
                if not name:
                    continue

                original_name = name.strip()
                normalized_name = normalize_channel_name(original_name, aliases)
                if normalized_name != original_name:
                    alias_mapped_count += 1
                    logger.debug(f"  Alias: '{original_name}' -> '{normalized_name}'")

                name_key = normalized_name.strip().upper()

                if name_key not in all_channels:
                    all_channels[name_key] = []

                url = ch["url"]
                tier = get_url_tier(url)

                # ── Tier-aware validation decision ─────────────────────────────────
                if should_validate_url(url, cache):
                    is_valid = validate_url(url, logger, session=session, timeout=TIMEOUT)
                    # Update cache with new structure
                    cache[url] = {
                        "valid": is_valid,
                        "last_validated": today_str,
                        "tier": tier,
                    }
                    newly_validated += 1
                    batch_count += 1
                else:
                    # Use cached result (must be valid + within tier period or whitelisted)
                    entry = cache.get(url)
                    if entry:
                        is_valid = entry.get("valid", False)
                    else:
                        # Whitelisted URL not in cache - treat as valid
                        is_valid = True
                        cache[url] = {
                            "valid": True,
                            "last_validated": today_str,
                            "tier": tier,
                        }
                    skipped_validation += 1

                all_channels[name_key].append({
                    "url": url,
                    "priority": priority,
                    "raw_extinf": ch["raw_extinf"],
                    "is_valid": is_valid,
                    "original_name": original_name
                })

                if batch_count % BATCH_SIZE == 0:
                    save_cache(cache, CACHE_FILE)
                    logger.info(f"  [Cache saved: {len(cache)} entries, {newly_validated} newly validated]")

            if batch_count > 0:
                save_cache(cache, CACHE_FILE)
                logger.info(f"  File done: +{batch_count} validated, cache now {len(cache)} entries")

        except Exception as e:
            logger.error("  Failed " + filepath.name + ": " + str(e))

    # ── Merge channels ──────────────────────────────────────────────────────────

    merged_channels = []

    for name_key, sources in all_channels.items():
        valid_sources = [s for s in sources if s["is_valid"]]
        invalid_count = len(sources) - len(valid_sources)
        total_invalid += invalid_count

        if valid_sources:
            total_valid += len(valid_sources)
            valid_sources.sort(key=lambda x: x["priority"])
            selected = valid_sources[:MAX_LINES_PER_CHANNEL]

            template_extinf = selected[0]["raw_extinf"]
            clean_name = name_key.title()

            merged_channels.append({
                "name": clean_name,
                "urls": [s["url"] for s in selected],
                "template_extinf": template_extinf,
                "source_count": len(selected)
            })

    merged_channels.sort(key=lambda x: x["name"])

    logger.info("=" * 50)
    logger.info("Validation complete:")
    logger.info("  Valid streams: " + str(total_valid))
    logger.info("  Invalid streams: " + str(total_invalid))
    logger.info("  Merged channels: " + str(len(merged_channels)))
    logger.info("  Aliases mapped: " + str(alias_mapped_count))
    logger.info("  Newly validated: " + str(newly_validated))
    logger.info("  Skipped (cached): " + str(skipped_validation))
    logger.info("  Cache: " + str(len(cache)) + " total entries")

    return merged_channels


def main():
    logger = setup_logging(LOG_DIR, "validate")
    merged = validate_and_merge(logger)

    if merged:
        output_file = OUTPUT_DIR / ("hk_merged_" + datetime.now().strftime('%Y%m%d') + ".m3u")

        lines = ['#EXTM3U']
        for ch in merged:
            for i, url in enumerate(ch["urls"]):
                if i == 0:
                    lines.append(ch["template_extinf"])
                else:
                    lines.append('#EXTINF:-1 group-title="HK",' + ch["name"] + " (Backup" + str(i) + ")")
                lines.append(url)

        content = '\n'.join(lines)
        output_file.write_text(content, encoding='utf-8')

        logger.info("Merge complete -> " + str(output_file))

    return merged


if __name__ == "__main__":
    main()
