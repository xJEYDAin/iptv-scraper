# 🌐 Global IPTV Auto Scraper

> Automatically scrape IPTV live streams from 40+ countries worldwide.

---

## 📡 Data Sources

**20 data sources** by priority:

| Priority | Source | Notes |
|----------|--------|-------|
| 1-2 | sammy0101, xiweiwong, zhi35, freetv-fun, epg-pw | HK CDN / Full logos |
| 3-4 | fanmingming, CCSH, gitee-why006, iptv-org | Official / General |
| 5 | vbskycn, hujingguang, suxuang | IPv6 / Regional |

---

## 📤 Output

| File | Channels | Description |
|------|----------|-------------|
| `hk_merged.m3u` | ~80 | HK/TW/MO channels |
| `all_merged.m3u` | ~1650 | Global channels |

---

## 🏗️ Architecture

```
iptv-scraper (03:00) → pull cache → run → push output/filtered
iptv-validator (03:30) → pull filtered → validate → push cache
```

**Cache:** validator results → scraper uses cache to skip validation

---

## 🚀 Quick Start

```bash
# Fast mode (uses cache)
SKIP_VALIDATION=1 python3 main.py

# Full scrape
python3 main.py
```

---

## 📄 License

MIT License
