# 🌐 全球 IPTV 直播源自动爬虫

> 自动抓取全球 IPTV 直播源，支持港台/日韩/欧美等 40+ 国家。

---

## 📡 数据源

**20 个数据源**，按优先级排序：

| 优先级 | 源 | 特点 |
|--------|------|-------|
| 1-2 | sammy0101, xiweiwong, zhi35, freetv-fun, epg-pw | HK CDN / 台标完整 |
| 3-4 | fanmingming, CCSH, gitee-why006, iptv-org | 官方源 / 综合源 |
| 5 | vbskycn, hujingguang, suxuang | IPv6 / 地域特色 |

---

## 📤 输出结果

| 文件 | 频道数 | 说明 |
|------|--------|------|
| `hk_merged.m3u` | ~80 | 港澳台频道 |
| `all_merged.m3u` | ~1650 | 全球频道 |

---

## 🏗️ 架构

```
iptv-scraper (03:00) → pull cache → 运行 → push output/filtered
iptv-validator (03:30) → pull filtered → 验证 → push cache
```

**缓存机制：** validator 验证结果 → scraper 使用缓存跳过验证

---

## 🚀 快速开始

```bash
# 快速模式（使用缓存）
SKIP_VALIDATION=1 python3 main.py

# 完整抓取
python3 main.py
```

---

## 📄 许可证

MIT License
