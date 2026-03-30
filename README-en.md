# HK IPTV Auto Scraper

Automated IPTV channel scraper focused on Hong Kong, Taiwan, and Asia-Pacific regions. Supports scheduled runs, stream availability validation, speed testing, and generates optimized M3U playlists.

[![Daily Update](https://img.shields.io/github/actions/workflow/status/xJEYDAin/iptv-scraper/update.yml?label=daily%20update&style=flat-square)](https://github.com/xJEYDAin/iptv-scraper/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)](https://www.python.org/)

## 📺 Playlists

| List | Link | Description |
|------|------|-------------|
| **Hong Kong** | `https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/hk_merged.m3u` | HK-focused channels |
| **All Channels** | `https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/all_merged.m3u` | All scraped channels (HK + TW + CN + more) |

> Open these links with any IPTV-compatible player: [VLC](https://www.videolan.org/), [mpv](https://mpv.io/), [Kodi](https://kodi.tv/). See [awesome-iptv](https://github.com/iptv-org/awesome-iptv#apps).

---

## ✨ Features

- **🤖 Auto Scraping** — Daily fetch from multiple public M3U sources
- **✅ Stream Validation** — Check each channel availability before publishing
- **⚡ Speed Filtering** — Auto-remove slow or unresponsive streams (configurable threshold)
- **🏷️ Name Standardization** — 220+ alias rules for consistent naming across sources
- **🎨 Auto Logo Matching** — Automatic channel logo matching (EPG CDN + Imgur fallback)
- **📺 VLC Optimization** — Built-in network-caching and timeout parameters for smoother playback
- **💾 Caching** — 24-hour validation cache + checkpoint support for faster re-runs
- **🗓️ Daily Auto Update** — GitHub Actions runs daily at 03:00 UTC

---

## 📂 Project Structure

```
iptv-scraper/
├── main.py                  # Entry point: orchestrates the full pipeline
├── config.py               # Shared config (paths, speed threshold, etc.)
├── fetch_sources.py       # Step 1: Fetch raw M3U from sources
├── filter_hk.py           # Step 2: Filter HK/TW regional channels
├── validate_and_merge.py   # Step 3: Validate URLs and merge results
├── speedtest.py            # Step 4: Test download speed for each stream
├── generate_playlist.py    # Step 5: Generate M3U with logos and VLC params
├── utils.py               # Shared utilities (logging, file ops)
├── alias.txt               # Channel name → Standard name mapping
├── logo_map.py             # Channel name → Logo URL mapping
├── output/                # Generated M3U playlists (git-tracked)
├── sources/                # Raw scraped M3U files (git-ignored)
├── filtered/               # Intermediate filter results (git-ignored)
├── cache/                  # Validation cache (git-ignored)
└── logs/                   # Run logs (git-ignored)
```

---

## 🚀 Quick Start

### Local Run

```bash
# 1. Clone the repo
git clone https://github.com/xJEYDAin/iptv-scraper.git
cd iptv-scraper

# 2. Install dependencies
pip install requests

# 3. Run
python main.py
```

### Docker

```bash
# Build image
docker build -t iptv-scraper .

# Run (skip speed test to speed up)
docker run --rm \
  -e ENABLE_SPEEDTEST=false \
  -v $(pwd)/output:/app/output \
  iptv-scraper
```

### GitHub Actions (Auto-update after Fork)

1. Fork this repo
2. Go to **Actions** tab, enable workflows
3. Scraper runs daily at 03:00 UTC
4. Playlists auto-commit to `output/` on `master`

Manual trigger: Actions → **Update HK IPTV** → **Run workflow**

---

## ⚙️ Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ENABLE_SPEEDTEST` | `true` | Enable speed testing (`true` / `false`) |
| `MIN_SPEED_KB` | `500` | Min speed threshold (KB/s), streams below are dropped |
| `SORT_BY_SPEED` | `true` | Sort channels by speed (fastest first) |
| `SKIP_VALIDATION` | `false` | Skip validation (use cache only, for debugging) |

---

## 🔍 Data Sources

| Source | Region | Update |
|--------|--------|--------|
| sammy0101/hk-iptv-auto | HK | Daily |
| nthack/IPTVM3U | HK/TW | Daily |
| imDazui/Tvlist-awesome-m3u | HK/TW | Daily |
| iptv-org/iptv | Global | Daily |
| Free-TV/IPTV | 40+ countries | Daily |

---

## 📡 VLC Optimization

The generated M3U includes optimized VLC parameters:

```
#EXTVLCOPT:network-caching=1000
#EXTVLCOPT:max-time=10
```

| Parameter | Value | Description |
|-----------|-------|-------------|
| network-caching | 1000ms | Buffer size for network streams |
| max-time | 10s | Max time to wait for stream response |

---

## ❓ FAQ

**Q: Why do some channels show as "unavailable"?**
A: IPTV streams go offline frequently. The scraper tests each stream and filters out slow/unresponsive ones. Run daily to keep the list fresh.

**Q: Can I add more channels?**
A: Edit `fetch_sources.py` to add new M3U source URLs. PRs welcome!

**Q: How to contribute?**
A: 1. Fork the repo
2. Make your changes
3. Submit a PR with clear description

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

**Note:** All data sourced from public M3U feeds. Respect source attribution.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

*Maintained by [xJEYDAin](https://github.com/xJEYDAin) | Star History: https://star-history.com/#xJEYDAin/iptv-scraper*
