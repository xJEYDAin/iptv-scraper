#!/usr/bin/env python3
from config import FILTERED_DIR, OUTPUT_DIR, LOG_DIR, CACHE_DIR, CACHE_FILE
"""IPTV Validator & Merger"""
import re
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
import requests

PRIORITY = {
    "sammy0101": 1,
    "nthack": 2,
    "joker-cold": 3
}

TIMEOUT = 10
MAX_LINES_PER_CHANNEL = 3
CACHE_FILE = CACHE_DIR / "validation_cache.json"

# Batch size for incremental cache saves (after each file)
BATCH_SIZE = 500

def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime('%Y%m%d')
    log_file = str(LOG_DIR / ("validate_" + today_str + ".log"))
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def get_source_priority(filename):
    for name, priority in PRIORITY.items():
        if name in filename:
            return priority
    return 99

def parse_m3u(content):
    channels = []
    lines = content.strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf = line

            if ',' in line:
                name = line.split(',', 1)[1].strip()
            else:
                name = ""

            match = re.search(r'tvg-name="([^"]*)"', line)
            tvg_name = match.group(1) if match else name

            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    channels.append({
                        "name": name,
                        "tvg_name": tvg_name,
                        "url": url,
                        "raw_extinf": extinf
                    })
                    i += 2
                    continue
        i += 1

    return channels

def validate_url(url, logger, timeout=TIMEOUT):
    """Validate URL using context managers to avoid resource leaks."""
    try:
        with requests.head(url, timeout=timeout, allow_redirects=True) as response:
            if response.status_code in [200, 301, 302, 303, 307, 308]:
                return True
        # Try GET for streaming servers that don't respond to HEAD
        with requests.get(url, timeout=timeout) as response:
            return response.status_code == 200
    except Exception as e:
        logger.debug(f"URL validation failed for {url}: {e}")
        return False

def load_cache():
    """Load validation cache with proper error handling.
    Corrupted cache files are deleted and重建.
    """
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            logging.warning(f"Cache corrupted ({e}), deleting and rebuilding...")
            CACHE_FILE.unlink()
    return {}

def save_cache(cache):
    """Save validation cache atomically."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # Write to temp file then rename to avoid partial writes
    tmp = CACHE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.rename(CACHE_FILE)

def validate_and_merge(logger):
    logger.info("=" * 50)
    logger.info("Starting validation and merge")
    logger.info("=" * 50)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filtered_files = sorted(
        FILTERED_DIR.glob("*.m3u*"),
        key=lambda p: get_source_priority(p.name)
    )

    if not filtered_files:
        logger.error("No filtered files found!")
        return None

    logger.info("Found " + str(len(filtered_files)) + " files to process")

    # Load validation cache
    cache = load_cache()
    logger.info("Loaded cache: " + str(len(cache)) + " entries")

    # Collect all channels by name, with their priority and URLs
    all_channels = {}  # name_key -> [(url, priority, raw_extinf, is_valid), ...]

    total_valid = 0
    total_invalid = 0
    newly_validated = 0

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

                name_key = name.strip().upper()

                if name_key not in all_channels:
                    all_channels[name_key] = []

                url = ch["url"]
                # Use cache if available, otherwise validate
                if url in cache:
                    is_valid = cache[url]
                else:
                    is_valid = validate_url(url, logger)
                    cache[url] = is_valid
                    newly_validated += 1
                    batch_count += 1

                    # P0-4: incremental cache save every BATCH_SIZE validations
                    if batch_count % BATCH_SIZE == 0:
                        save_cache(cache)
                        logger.info(f"  [Cache saved: {len(cache)} entries, {newly_validated} newly validated this file]")

                all_channels[name_key].append({
                    "url": url,
                    "priority": priority,
                    "raw_extinf": ch["raw_extinf"],
                    "is_valid": is_valid
                })

            # Save cache after each file
            if batch_count > 0:
                save_cache(cache)
                logger.info(f"  File done: +{batch_count} validated, cache now {len(cache)} entries")

        except Exception as e:
            logger.error("  Failed " + filepath.name + ": " + str(e))

    # Merge channels - keep valid ones, sorted by priority
    merged_channels = []

    for name_key, sources in all_channels.items():
        # Filter to only valid sources
        valid_sources = [s for s in sources if s["is_valid"]]
        invalid_count = len(sources) - len(valid_sources)
        total_invalid += invalid_count

        if valid_sources:
            total_valid += len(valid_sources)
            # Sort by priority
            valid_sources.sort(key=lambda x: x["priority"])
            # Take max lines
            selected = valid_sources[:MAX_LINES_PER_CHANNEL]

            # Use the highest priority extinf as template
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
    logger.info("  Cache: " + str(len(cache)) + " total entries")

    return merged_channels

def main():
    logger = setup_logging()
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
