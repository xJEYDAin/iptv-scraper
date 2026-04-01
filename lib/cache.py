#!/usr/bin/env python3
"""Unified cache management for IPTV scraper.

Supports tier-based TTL, last_validated tracking, and LRU eviction.
Cache entry format:
    {
        "url": {
            "valid": True/False,           # validation result
            "last_validated": "2026-04-01", # date string
            "tier": "hk_tw_mo",            # validation tier
            "speed": 512000,               # speed in bytes/sec (0 if not tested)
            "timestamp": 1234567890.0      # unix timestamp
        }
    }
"""
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

from config import CACHE_DIR

logger = logging.getLogger(__name__)

DEFAULT_MAX_ENTRIES = 20000
DEFAULT_TTL_DAYS = 30  # Global default for entries without tier info


class ChannelCache:
    """Unified cache for channel validation and speedtest results."""

    def __init__(self, cache_file: Path = None, max_entries: int = DEFAULT_MAX_ENTRIES,
                 ttl_days: int = DEFAULT_TTL_DAYS):
        if cache_file is None:
            cache_file = CACHE_DIR / "channel_cache.json"
        self.cache_file = Path(cache_file)
        self.max_entries = max_entries
        self.ttl_seconds = ttl_days * 86400
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        """Load cache from disk, handle corruption gracefully."""
        if self.cache_file.exists():
            try:
                data = json.loads(self.cache_file.read_text(encoding='utf-8'))
                if isinstance(data, dict):
                    self._cache = data
                else:
                    self._cache = {}
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Cache corrupted ({self.cache_file}), rebuilding: {e}")
                self.cache_file.unlink(missing_ok=True)
                self._cache = {}
        self._prune_expired()

    def _save(self):
        """Save cache atomically to disk."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.cache_file.with_suffix('.tmp')
        tmp.write_text(json.dumps(self._cache, ensure_ascii=False, indent=2), encoding='utf-8')
        tmp.rename(self.cache_file)

    def _prune_expired(self):
        """Remove expired entries based on TTL."""
        now = time.time()
        before = len(self._cache)
        self._cache = {
            k: v for k, v in self._cache.items()
            if now - v.get("timestamp", 0) < self.ttl_seconds
        }
        if before != len(self._cache):
            logger.info(f"Cache: pruned {before - len(self._cache)} expired entries")

    def _evict_lru(self):
        """Evict oldest entries if cache exceeds max_entries."""
        if len(self._cache) <= self.max_entries:
            return
        sorted_items = sorted(
            self._cache.items(),
            key=lambda x: x[1].get("timestamp", 0),
            reverse=True
        )
        self._cache = dict(sorted_items[:self.max_entries])
        logger.info(f"Cache: evicted to {len(self._cache)} entries (limit: {self.max_entries})")

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cache entry for URL."""
        entry = self._cache.get(url)
        if entry is None:
            return None
        if time.time() - entry.get("timestamp", 0) >= self.ttl_seconds:
            del self._cache[url]
            return None
        return entry

    def is_valid(self, url: str) -> bool:
        """Check if URL is cached as valid."""
        entry = self.get(url)
        return entry is not None and entry.get("valid", False)

    def get_speed(self, url: str) -> float:
        """Get cached speed for URL in bytes/sec."""
        entry = self.get(url)
        if entry is None:
            return 0.0
        return entry.get("speed", 0.0)

    def set(self, url: str, valid: bool, speed: float = 0.0,
            last_validated: str = None, tier: str = None):
        """Set cache entry for URL with full metadata."""
        from datetime import date as date_cls
        entry = {
            "valid": valid,
            "speed": speed,
            "timestamp": time.time(),
        }
        if last_validated:
            entry["last_validated"] = last_validated
        else:
            entry["last_validated"] = date_cls.today().strftime("%Y-%m-%d")
        if tier:
            entry["tier"] = tier
        self._cache[url] = entry
        if len(self._cache) > self.max_entries:
            self._evict_lru()

    def set_valid(self, url: str, last_validated: str = None, tier: str = None):
        """Mark URL as valid without changing speed."""
        from datetime import date as date_cls
        entry = self._cache.get(url, {})
        entry["valid"] = True
        entry["timestamp"] = time.time()
        if last_validated:
            entry["last_validated"] = last_validated
        elif "last_validated" not in entry:
            entry["last_validated"] = date_cls.today().strftime("%Y-%m-%d")
        if tier:
            entry["tier"] = tier
        self._cache[url] = entry

    def set_speed(self, url: str, speed: float):
        """Set speed for URL (preserves valid flag)."""
        entry = self._cache.get(url, {"valid": True})
        entry["speed"] = speed
        entry["timestamp"] = time.time()
        self._cache[url] = entry

    def save(self):
        """Persist cache to disk."""
        self._save()

    def __len__(self):
        return len(self._cache)

    def __contains__(self, url: str):
        return self.get(url) is not None


# ─── Legacy compatibility functions ──────────────────────────────────────────

def _migrate_entry(v) -> Dict[str, Any]:
    """Migrate legacy bool/simple entries to new dict format."""
    if isinstance(v, bool):
        from datetime import date as date_cls
        return {"valid": v, "last_validated": date_cls.today().strftime("%Y-%m-%d"), "tier": "global", "speed": 0}
    if isinstance(v, dict):
        # Ensure required fields exist
        v.setdefault("last_validated", None)
        v.setdefault("tier", "global")
        v.setdefault("speed", 0)
        return v
    return {"valid": bool(v), "last_validated": None, "tier": "global", "speed": 0}


def load_cache(cache_file: Path) -> Dict[str, Dict[str, Any]]:
    """Load validation_cache.json.

    Returns dict: url -> {valid, last_validated, tier, ...}
    Migrates legacy bool entries automatically.
    """
    cache_file = Path(cache_file)
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                migrated = {}
                for k, v in data.items():
                    if isinstance(v, bool):
                        migrated[k] = _migrate_entry(v)
                    elif isinstance(v, dict):
                        migrated[k] = _migrate_entry(v)
                    else:
                        migrated[k] = _migrate_entry(bool(v))
                return migrated
        except (json.JSONDecodeError, IOError):
            cache_file.unlink(missing_ok=True)
    return {}


def save_cache(cache: Dict, cache_file: Path):
    """Save validation_cache.json atomically.

    Handles both legacy (url->bool) and new (url->dict) formats.
    """
    cache_file = Path(cache_file)
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    # Prune if too large
    if len(cache) > 10000:
        sorted_items = sorted(cache.items(), key=lambda x: str(x[1]))
        cache = dict(sorted_items[:10000])
        logger.info(f"Cache pruned to {len(cache)} entries")

    tmp = cache_file.with_suffix('.tmp')
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.rename(cache_file)
