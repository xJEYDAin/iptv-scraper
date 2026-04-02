# 🌐 Global IPTV Auto Scraper

> Automatically scrape IPTV live streams from 40+ countries worldwide, with daily updates for HK/TW/MO, Japan, Korea, Europe, US and more.

---

## 📡 Data Sources

**20 data sources**, sorted by priority:

| Priority | Source | Channels | Update | Notes |
|----------|--------|----------|--------|-------|
| 1 | [sammy0101/hk-iptv-auto](https://github.com/sammy0101/hk-iptv-auto) | ~62 | Daily | HK CDN |
| 1 | [xiweiwong/hk-iptv-auto](https://github.com/xiweiwong/hk-iptv-auto) | ~100+ | Daily | HK CDN |
| 2 | [zhi35-iptv](https://live.zhi35.com/iptv.m3u) | ~80 | Daily | Full logos |
| 2 | [freetv-fun](https://t.freetv.fun/m3u/playlist.m3u) | ~150 | Daily | General |
| 2 | [epg-pw](https://epg.pw/test_channels.m3u) | ~50 | Irregular | EPG-friendly |
| 3 | [fanmingming/live](https://github.com/fanmingming/live) | ~200 | Irregular | IPv6 support |
| 3 | [CCSH/IPTV](https://github.com/CCSH/IPTV) | ~300 | Irregular | General |
| 3 | [why006/TV](https://gitee.com/why006/TV) | ~150 | Irregular | China mirror |
| 4 | [iptv-org/iptv](https://github.com/iptv-org/iptv) | ~1500+ | Irregular | Global |
| 4 | [hujingguang/ChinaIPTV](https://github.com/hujingguang/ChinaIPTV) | ~200 | Irregular | China |
| 4 | [Harbin-byte/iptv](https://github.com/Harbin-byte/iptv) | ~50 | Irregular | HK supplement |
| 4 | [suxuang/myIPTV](https://github.com/suxuang/myIPTV) | ~100 | Irregular | IPv4 first |
| 5 | [Free-TV/IPTV](https://github.com/Free-TV/IPTV) | ~1000+ | Irregular | Regional |
| 5 | [vbskycn/iptv](https://live.zbds.top/tv/iptv4.m3u) | ~80 | Irregular | IPv6 regional |

---

## 📤 Output

| File | Channels | Description |
|------|----------|-------------|
| `hk_merged.m3u` | ~80 | HK/TW/MO channels |
| `all_merged.m3u` | ~1650 | Global channels |

**Full URLs:**

- **Hong Kong:** https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/hk_merged.m3u
- **Global:** https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/all_merged.m3u

---

## 🏗️ Architecture

```
03:00  iptv-scraper  pulls cache
                ↓
         fetch all sources (merge + dedup)
                ↓
         speed test + filter quality links
                ↓
         output filtered/ → output/
                ↓
03:30  iptv-validator pulls filtered
                ↓
         concurrent URL validation
                ↓
         update validation_cache.json
```

**Cache:** validator results are saved → scraper skips already-validated links on next run.

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/xJEYDAin/iptv-scraper.git
cd iptv-scraper

# Install dependencies
pip install -r requirements.txt

# Fast mode (skip validation, use cache)
SKIP_VALIDATION=1 python3 main.py

# Full scrape (with validation)
python3 main.py
```

---

## 📄 License

MIT License
