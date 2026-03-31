# 🌐 Global IPTV Auto Scraper

> Automatically scrape IPTV live streams from around the world. Supports speed testing & filtering, channel name normalization, logo injection, covering 40+ countries including Hong Kong/Taiwan, Japan/Korea, US/Europe.

[![Python 3](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌐 **Multi-Source Scraping** | Supports 12+ IPTV data sources with automatic deduplication |
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
├── validate_and_merge.py  # 🔍 Validation and merge
├── generate_playlist.py    # 📝 Playlist generation
├── legacy.py              # 🔧 Compatibility layer
│
├── lib/                    # 🛠️ Utility library
│   ├── helpers.py          # Common helper functions
│   └── whitelist.py        # CDN whitelist
│
├── fetch/                  # 🌐 Fetch module
│   ├── sources.py          # Data source definitions
│   └── download.py         # Downloader
│
├── validate/               # ✅ Validation module
│   ├── validators.py      # Speed validators
│   └── cache.py           # Cache manager
│
├── group/                  # 🗂️ Group module
│   ├── categorizer.py     # Channel categorizer
│   └── normalize.py       # Name normalizer
│
├── output/                 # 📤 Output module
│   └── playlist.py        # M3U generator
│
├── sources/                # 📥 Scraped source data
└── output/                 # 📤 Output M3U files
    ├── hk_merged.m3u      # 🇭🇰 HK & Taiwan channels
    └── all_merged.m3u     # 🌍 Global channels
```

---

## 📺 Grouping Standards

### 🇭🇰 Hong Kong Channels (`hk_merged.m3u`)

| Group | Channels |
|-------|----------|
| 📺 TVB | Pearl TV, Jade TV, J2, News Channel, etc. |
| 📺 ViuTV | ViuTV, ViuTVsix |
| 📺 RTHK | All RTHK channels |
| 📺 HOY TV | HOY TV series |
| 📺 Now TV | Now TV series |
| 🇹🇼 Taiwan | Major Taiwanese channels |
| 🇲🇴 Macau | Major Macau channels |
| 📺 Phoenix TV | Phoenix Chinese, Phoenix Info, etc. |
| 📺 Hong Kong Others | Other HK channels |

### 🌍 Global Channels (`all_merged.m3u`)

| Group | Channels |
|-------|----------|
| 📺 CCTV Channels | CCTV1-17, CETV, etc. |
| 📺 Provincial Channels | Beijing, Shanghai, Guangdong, Sichuan, etc. |
| 📡 Satellite Channels | International satellite channels |
| 📺 TVB / ViuTV / RTHK / HOY TV / Now TV | Major HK channels |
| 🇹🇼 Taiwan | Taiwanese channels |
| 🇲🇴 Macau | Macau channels |
| 🎬 Movie Channels | HBO, Star Movies, etc. |
| 🎵 Music Channels | MTV, V Channels, etc. |
| 🌐 International Channels | CNN, BBC, Al Jazeera, etc. |
| 📰 News & Finance | News and finance channels |
| 🧸 Kids Channels | Children's channels |
| 🎭 Entertainment Channels | Variety shows |
| ⚽ Sports Channels | Sports channels |
| 📺 Documentary | Documentary channels |
| 🌎 Americas / 🌏 Asia / 🌍 Europe / 🌎 Africa | Regional channels |

---

## 📊 Data Sources

| Source | Type | Est. Channels | Notes |
|--------|------|--------------|-------|
| iptv-org | M3U | ~11,000 | Largest source |
| vbskycn-iptv4 | M3U | ~600 | |
| zhi35-iptv | M3U | ~522 | |
| hujingguang-iptv | M3U | ~65 | |
| sammy0101 | M3U | ~55 | |

---

## 🚀 Quick Start

### Requirements

- Python 3.8+
- FFmpeg (for speed testing)

### Install Dependencies

```bash
pip install requests
```

### Run

```bash
# Full scrape (download + test + merge)
python3 main.py

# Skip validation (use cached data, fast testing)
SKIP_VALIDATION=1 python3 main.py

# Adjust minimum speed threshold (unit: KB/s)
MIN_SPEED_KB=50 python3 main.py

# Custom output directory
OUTPUT_DIR=/path/to/output python3 main.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKIP_VALIDATION` | `0` | Set to `1` to skip speed validation |
| `MIN_SPEED_KB` | `30` | Minimum speed threshold (KB/s) |
| `OUTPUT_DIR` | `./output` | Output directory |
| `CACHE_DIR` | `./cache` | Cache directory |

---

## 📤 Output Files

```
output/
├── hk_merged.m3u      # Hong Kong & Taiwan channels
│   ├── group-title="📺 TVB"
│   ├── group-title="📺 ViuTV"
│   └── ...
│
└── all_merged.m3u     # Global channels
    ├── group-title="📺 CCTV"
    ├── group-title="📺 Provincial"
    ├── group-title="🌐 International"
    └── ...
```

---

## 🔧 Module Details

### Fetch Module (`fetch/`)

Download M3U files from various sources:

```python
from fetch.sources import SOURCES
from fetch.download import download_all

# Download all sources
sources_data = download_all(SOURCES)
```

### Validate Module (`validate/`)

Speed test channel URLs:

```python
from validate.validators import speed_test
from validate.cache import Cache

# Speed test
result = speed_test(url, min_speed=30)
```

### Group Module (`group/`)

Channel categorization and name normalization:

```python
from group.categorizer import categorize
from group.normalize import normalize_name

# Normalize channel name
name = normalize_name("CCTV-1 综合")  # -> "CCTV1"
# Categorize channel
category = categorize(name)  # -> "CCTV Channels"
```

### Output Module (`output/`)

Generate final M3U files:

```python
from output.playlist import generate_playlist

# Generate playlist
generate_playlist(channels, output_file)
```

---

## 🗺️ Roadmap

- [ ] Add more data sources
- [ ] Support more regional groupings
- [ ] Web interface
- [ ] Docker deployment
- [ ] Auto-update mechanism

---

## ⚠️ Disclaimer

This project is for educational and research purposes only. Please comply with local laws and regulations, and do not use this project to watch copyright-protected content. Any issues arising from the use of this project are the sole responsibility of the user.

---

## 📄 License

MIT License

---

> Last updated: 2026-04-01
