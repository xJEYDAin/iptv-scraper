#!/usr/bin/env python3
"""Unified cache management for IPTV scraper.

Combines validation_cache and speedtest_cache into a single store.
Supports TTL expiration and LRU eviction.
"""
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

from config import CACHE_DIR

logger = logging.getLogger(__name__)

DEFAULT_MAX_ENTRIES = 20000
DEFAULT_TTL_DAYS = 7


class ChannelCache:
    """Unified cache for channel validation and speedtest results.
    
    Cache entry format:
        {
            "url": {
                "valid": True/False,       # validation result
                "speed": 512000,            # speed in bytes/sec (0 if not tested)
                "timestamp": 1234567890.0   # last update time
            }
        }
    """

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
                # Validate structure
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
        # Sort by timestamp, keep newest max_entries
        sorted_items = sorted(
            self._cache.items(),
            key=lambda x: x[1].get("timestamp", 0),
            reverse=True
        )
        self._cache = dict(sorted_items[:self.max_entries])
        logger.info(f"Cache: evicted to {len(self._cache)} entries (limit: {self.max_entries})")

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cache entry for URL.
        
        Returns:
            dict with keys: valid, speed, timestamp or None if not found/expired
        """
        entry = self._cache.get(url)
        if entry is None:
            return None
        # Check TTL
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

    def set(self, url: str, valid: bool, speed: float = 0.0):
        """Set cache entry for URL.
        
        Args:
            url: Channel URL
            valid: Whether URL passed validation
            speed: Speed in bytes/sec (from speedtest)
        """
        self._cache[url] = {
            "valid": valid,
            "speed": speed,
            "timestamp": time.time()
        }
        if len(self._cache) > self.max_entries:
            self._evict_lru()

    def set_valid(self, url: str):
        """Mark URL as valid without changing speed."""
        entry = self._cache.get(url, {})
        entry["valid"] = True
        entry["timestamp"] = time.time()
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


# ─── Legacy compatibility functions ─────────────────────────────────────────

def load_cache(cache_file: Path) -> Dict[str, bool]:
    """Legacy: load validation_cache.json.
    
    Returns dict: url -> is_valid (bool)
    """
    cache_file = Path(cache_file)
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                # Convert to bool-only format
                return {k: bool(v) if not isinstance(v, bool) else v
                        for k, v in data.items()}
        except (json.JSONDecodeError, IOError):
            cache_file.unlink(missing_ok=True)
    return {}


def save_cache(cache: Dict[str, bool], cache_file: Path):
    """Legacy: save validation_cache.json atomically.
    
    Accepts dict: url -> is_valid (bool)
    """
    cache_file = Path(cache_file)
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if len(cache) > 10000:
        sorted_items = sorted(cache.items(), key=lambda x: str(x[1]))
        cache = dict(sorted_items[:10000])
        logger.info(f"Cache pruned to {len(cache)} entries")

    tmp = cache_file.with_suffix('.tmp')
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.rename(cache_file)
