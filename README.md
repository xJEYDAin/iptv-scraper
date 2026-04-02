# 🌐 全球 IPTV 直播源自动爬虫

> 自动抓取全球 IPTV 直播源，汇聚港澳台、日韩、欧美等 40+ 国家频道，每日定时更新。

---

## 📡 数据源

**20 个数据源**，按优先级排序：

| 优先级 | 源 | 频道数 | 更新 | 特点 |
|--------|------|--------|------|-------|
| 1 | [sammy0101/hk-iptv-auto](https://github.com/sammy0101/hk-iptv-auto) | ~62 | 每日 | HK CDN |
| 1 | [xiweiwong/hk-iptv-auto](https://github.com/xiweiwong/hk-iptv-auto) | ~100+ | 每日 | HK CDN |
| 2 | [zhi35-iptv](https://live.zhi35.com/iptv.m3u) | ~80 | 每日 | 台标完整 |
| 2 | [freetv-fun](https://t.freetv.fun/m3u/playlist.m3u) | ~150 | 每日 | 综合频道 |
| 2 | [epg-pw](https://epg.pw/test_channels.m3u) | ~50 | 不定期 | EPG 友好 |
| 3 | [fanmingming/live](https://github.com/fanmingming/live) | ~200 | 不定期 | IPv6 支持 |
| 3 | [CCSH/IPTV](https://github.com/CCSH/IPTV) | ~300 | 不定期 | 综合频道 |
| 3 | [why006/TV](https://gitee.com/why006/TV) | ~150 | 不定期 | 国内镜像 |
| 4 | [iptv-org/iptv](https://github.com/iptv-org/iptv) | ~1500+ | 不定期 | 全球综合 |
| 4 | [hujingguang/ChinaIPTV](https://github.com/hujingguang/ChinaIPTV) | ~200 | 不定期 | 中国频道 |
| 4 | [Harbin-byte/iptv](https://github.com/Harbin-byte/iptv) | ~50 | 不定期 | HK 补充 |
| 4 | [suxuang/myIPTV](https://github.com/suxuang/myIPTV) | ~100 | 不定期 | IPv4 优先 |
| 5 | [Free-TV/IPTV](https://github.com/Free-TV/IPTV) | ~1000+ | 不定期 | 各地区分库 |
| 5 | [vbskycn/iptv](https://live.zbds.top/tv/iptv4.m3u) | ~80 | 不定期 | IPv6 特色 |

---

## 📤 输出结果

| 文件 | 频道数 | 说明 |
|------|--------|------|
| `hk_merged.m3u` | ~80 | 港澳台频道 |
| `all_merged.m3u` | ~1650 | 全球频道 |

**完整地址：**

- **香港:** https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/hk_merged.m3u
- **全球:** https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/all_merged.m3u

---

## 🏗️ 架构流程

```
03:00  iptv-scraper  拉取缓存
                ↓
         抓取所有数据源（去重合并）
                ↓
         速度测试 + 筛选优质链路
                ↓
         输出 filtered/ → output/
                ↓
03:30  iptv-validator 拉取 filtered
                ↓
         并发验证 URL 可用性
                ↓
         更新 validation_cache.json
```

**缓存机制：** validator 验证结果存入缓存 → scraper 运行时跳过已验证链路，加速生成。

---

## 🚀 快速开始

```bash
# 克隆
git clone https://github.com/xJEYDAin/iptv-scraper.git
cd iptv-scraper

# 安装依赖
pip install -r requirements.txt

# 快速模式（跳过验证，使用缓存）
SKIP_VALIDATION=1 python3 main.py

# 完整抓取（含验证）
python3 main.py
```

---

## 📄 许可证

MIT License
