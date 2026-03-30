# HK IPTV Auto Scraper

Automated IPTV channel scraper focused on Hong Kong, Taiwan, and Asia-Pacific regions. Runs on a schedule, validates stream availability, measures download speed, and generates optimized M3U playlists.

[![Update Schedule](https://img.shields.io/github/actions/workflow/status/xJEYDAin/iptv-scraper/update.yml?label=daily%20update&style=flat-square)](https://github.com/xJEYDAin/iptv-scraper/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)](https://www.python.org/)

## 📺 Playlists

| Playlist | URL | Description |
|----------|-----|-------------|
| **HK Channels** | `https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/hk_merged.m3u` | Hong Kong focused channels |
| **All Channels** | `https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/all_merged.m3u` | All scraped channels (HK + TW + CN + more) |

> Use any [IPTV-compatible player](https://github.com/iptv-org/awesome-iptv#apps) (VLC, mpv, Kodi, etc.) to open these links.

---

## ✨ Features

- **🤖 Automated scraping** — fetches from multiple public M3U sources daily
- **✅ Stream validation** — checks channel availability before including
- **⚡ Speed filtering** — removes slow/unresponsive streams (configurable threshold)
- **🏷️ Channel normalization** — 59+ alias rules for consistent naming across sources
- **🎨 Logo injection** — auto-matches channel logos (EPG CDN + Imgur fallback)
- **📺 VLC optimized** — includes network-caching and timeout parameters for smooth playback
- **💾 Caching** — 24h validation cache with checkpoint support for faster re-runs
- **🗓️ Daily auto-update** — GitHub Actions runs at 03:00 UTC every day

---

## 📂 Project Structure

```
iptv-scraper/
├── main.py                  # Entry point: orchestrates the full pipeline
├── config.py                # Shared settings (paths, speed thresholds, etc.)
├── fetch_sources.py         # Step 1: fetch raw M3U from data sources
├── filter_hk.py             # Step 2: filter HK / regional channels
├── validate_and_merge.py    # Step 3: validate URLs, merge results
├── speedtest.py             # Step 4: measure download speed per stream
├── generate_playlist.py     # Step 5: generate M3U with logos + VLC params
├── utils.py                 # Shared utilities (logging, file helpers)
├── alias.txt                # Channel name → canonical name mapping
├── logo_map.py              # Channel name → logo URL mapping
├── output/                  # Generated M3U playlists (git-tracked)
├── sources/                 # Raw fetched M3U files (gitignored)
├── filtered/                # Intermediate filtered results (gitignored)
├── cache/                   # Validation cache (gitignored)
└── logs/                    # Run logs (gitignored)
```

---

## 🚀 Quick Start

### Local

```bash
# 1. Clone
git clone https://github.com/xJEYDAin/iptv-scraper.git
cd iptv-scraper

# 2. Install dependencies
pip install requests

# 3. Run
python main.py
```

### Docker

```bash
# Build
docker build -t iptv-scraper .

# Run (skip speedtest for faster runs)
docker run --rm \
  -e ENABLE_SPEEDTEST=false \
  -v $(pwd)/output:/app/output \
  iptv-scraper
```

### GitHub Actions (Fork & Auto-Update)

1. Fork this repo
2. Go to **Actions** tab → enable the workflow
3. The scraper runs automatically at 03:00 UTC daily
4. Playlists are committed to `output/` on the `master` branch

To trigger manually: Actions → **Update HK IPTV** → **Run workflow**

---

## ⚙️ Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ENABLE_SPEEDTEST` | `true` | Enable/disable speed testing (`true` / `false`) |
| `MIN_SPEED_KB` | `500` | Minimum speed in KB/s; streams below this are dropped |
| `SORT_BY_SPEED` | `true` | Sort streams fastest-first (`true`) or alphabetical (`false`) |
| `SPEEDTEST_TIMEOUT` | `5` | Per-URL speed test timeout in seconds |
| `SPEEDTEST_WORKERS` | `10` | Number of parallel speed test threads |
| `SKIP_VALIDATION` | `0` | Set `1` to reuse cached validation results (faster dev runs) |
| `GITHUB_ACTIONS` | `auto` | Auto-detected; shortens timeouts when running in CI |

**Examples:**

```bash
# Skip speedtest for quick testing
ENABLE_SPEEDTEST=false python main.py

# Higher quality threshold (only fast streams)
MIN_SPEED_KB=1000 python main.py

# Use cached validation results
SKIP_VALIDATION=1 python main.py
```

---

## 🔍 Data Sources

| Source | Type | Region Focus |
|--------|------|-------------|
| [sammy0101/hk-iptv-auto](https://github.com/sammy0101/hk-iptv-auto) | M3U | 🇭🇰 HK (daily auto-update) |
| [nthack/IPTVM3U](https://github.com/nthack/IPTVM3U) | M3U | 🇭🇰 HK / 🇹🇼 TW |
| [imDazui/Tvlist-awesome-m3u-m3u8](https://github.com/imDazui/Tvlist-awesome-m3u-m3u8) | M3U | 🇭🇰 HK / 🇹🇼 TW |
| [iptv-org/iptv](https://github.com/iptv-org/iptv) | M3U | 🌍 Global |
| [Free-TV/IPTV](https://github.com/Free-TV/IPTV) | M3U | 🌍 40+ countries |

> Channels are validated and speed-tested before inclusion. Slow or broken streams are automatically removed.

---

## 📡 VLC Optimization

The generated M3U includes VLC-specific tags for reliable playback:

```
#EXTVLCOPT:network-caching=1000
#EXTVLCOPT:live-caching=1000
#EXTVLCOPT:timeout=10
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `network-caching` | 1000ms | Buffer to reduce network jitter |
| `live-caching` | 1000ms | Live stream buffer |
| `timeout` | 10s | Connection timeout |

---

## ❓ FAQ

**Q: Some channels don't work.**
A: IPTV streams are often temporary. The scraper re-validates daily — broken streams are filtered out automatically. If a channel is missing, it may have been removed from all source repositories.

**Q: How can I add a missing channel?**
A: The channel needs to exist in one of the upstream source repos. Check those projects first. You can also submit a PR to the relevant upstream source.

**Q: Can I run this more frequently than once a day?**
A: Yes — edit the cron schedule in `.github/workflows/update.yml`. Note that very frequent runs may increase load on source repos.

**Q: How does speed filtering work?**
A: Each stream URL is downloaded with a short timeout and the throughput (KB/s) is measured. Streams below `MIN_SPEED_KB` are excluded from the output.

**Q: Is this legal?**
A: This project only aggregates publicly available M3U links. It does not host or redistribute copyrighted content. Users are responsible for complying with their local laws.

---

## 🤝 Contributing

Contributions welcome! Please read the guidelines below.

### Adding / Fixing Channels

This project aggregates from upstream M3U sources. To add or fix a channel, submit a PR to the appropriate source:

- Hong Kong / Taiwan channels → [sammy0101/hk-iptv-auto](https://github.com/sammy0101/hk-iptv-auto)
- Global channels → [iptv-org/iptv](https://github.com/iptv-org/iptv) or [Free-TV/IPTV](https://github.com/Free-TV/IPTV)

### This Project

For issues specific to the scraper itself (validation logic, speed test, logo matching, etc.):

1. Open an issue describing the problem
2. Or submit a PR with the fix

### Alias / Logo Updates

To update channel name normalization or logo mappings, edit:
- `alias.txt` — channel name aliases
- `logo_map.py` — channel name → logo URL

---

## 📄 License

MIT — free to use, modify, and distribute.
