#!/usr/bin/env python3
"""IPTV Validator & Merger"""
import logging
from datetime import datetime
from pathlib import Path
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

TIMEOUT = 5
MAX_LINES_PER_CHANNEL = 3
BATCH_SIZE = 500


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
    alias_mapped_count = 0

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
                if url in cache:
                    is_valid = cache[url]
                else:
                    is_valid = validate_url(url, logger, session=session)
                    cache[url] = is_valid
                    newly_validated += 1
                    batch_count += 1

                    if batch_count % BATCH_SIZE == 0:
                        save_cache(cache, CACHE_FILE)
                        logger.info(f"  [Cache saved: {len(cache)} entries, {newly_validated} newly validated this file]")

                all_channels[name_key].append({
                    "url": url,
                    "priority": priority,
                    "raw_extinf": ch["raw_extinf"],
                    "is_valid": is_valid,
                    "original_name": original_name
                })

            if batch_count > 0:
                save_cache(cache, CACHE_FILE)
                logger.info(f"  File done: +{batch_count} validated, cache now {len(cache)} entries")

        except Exception as e:
            logger.error("  Failed " + filepath.name + ": " + str(e))

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
