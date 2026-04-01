# 🌐 Global IPTV Auto Scraper

> Automatically scrape IPTV live streams from around the world. Supports speed testing & filtering, channel name normalization, logo injection, covering 40+ countries including Hong Kong/Taiwan, Japan/Korea, US/Europe.

[![Python 3](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌐 **Multi-Source Scraping** | Supports 20+ IPTV data sources with automatic deduplication |
| ⚡ **Auto Speed Test** | CDN whitelist skips testing, others are speed-tested and filtered |
| 🇭🇰 **HK Filtering** | Auto-detect & categorize Hong Kong channels (TVB/ViuTV/RTHK/HOY TV/Now TV) |
| 🏷️ **Name Normalization** | 760+ channel alias mappings to eliminate duplicates |
| 🔗 **Channel Merge** | Same-name channels keep the best URL, auto-select fastest source |
| 🎨 **Logo Injection** | Integrated EPG logos for channel icons in players |
| 🔄 **Backup Channels** | Up to 3 backup sources per channel with auto-failover |

---

## 📁 Project Structure

```
iptv-scraper/
├── main.py                 # 🚀 Main entry point
├── fetch_sources.py        # 📡 Data source configuration
├── filter_hk.py           # 🇭🇰 HK channel filtering
├── generate_playlist.py    # 📝 Playlist generation (validation + speedtest)
│
├── lib/                    # 🛠️ Utility library
│   ├── cache.py           # Unified cache management
│   ├── helpers.py          # Common helper functions
│   ├── speedtest.py       # Speed test (fallback when iptv-validator unavailable)
│   └── whitelist.py       # CDN whitelist
│
├── fetch/                  # 🌐 Fetch module
│   ├── sources.py          # Data source definitions
│   └── download.py         # Downloader
│
├── group/                  # 🗂️ Group module
│   ├── categorizer.py     # Channel categorizer
│   └── normalize.py       # Name normalizer
│
├── output/                 # 📤 Output module
│   └── playlist.py        # M3U generator
│
├── cache/                  # 💾 Cache
├── sources/                # 📥 Scraped source data
└── output/                 # 📤 Output M3U files
    ├── hk_merged.m3u      # 🇭🇰 HK/TW/MO channels
    └── all_merged.m3u     # 🌍 Global channels
```


