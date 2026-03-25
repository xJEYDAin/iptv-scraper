# HK IPTV Auto Scraper

自动抓取香港 IPTV 直播源，每日更新。

## 功能

- 🤖 自动抓取多个数据源
- 🔍 筛选香港频道
- ✅ 验证直播源有效性
- 📝 分类整理（香港/台湾/大陆/电影/体育等）
- 💾 验证缓存，支持断点续传

## 数据源

| 来源 | 说明 |
|------|------|
| sammy0101/hk-iptv-auto | 香港专用，每日自动更新 |
| nthack/IPTVM3U | 港台直播源 |
| imDazui/Tvlist-awesome-m3u-m3u8 | 港台频道 |
| iptv-org/iptv | 全球最大开源库 |

## 播放列表

### 香港频道
```
https://raw.githubusercontent.com/{user}/{repo}/main/output/hk_merged.m3u
```

### 全部频道
```
https://raw.githubusercontent.com/{user}/{repo}/main/output/all_merged.m3u
```

## 使用方法

### 本地运行

```bash
# 安装依赖
pip install requests

# 运行
python main.py
```

### GitHub Actions 自动更新

1. Fork 本项目
2. 在 Actions 页面启用 workflow
3. 每天凌晨3点自动更新

## 脚本说明

| 脚本 | 功能 |
|------|------|
| fetch_sources.py | 抓取数据源 |
| filter_hk.py | 筛选香港频道 |
| validate_and_merge.py | 验证并合并 |
| generate_playlist.py | 生成播放列表 |

## 分类

- 🇭🇰 香港
- 🇹🇼 台湾
- 🇨🇳 大陆
- 🇲🇴 澳门
- 🎬 电影
- ⚽ 体育
- 🧸 儿童
- 📰 新闻
- 🎭 娱乐

## 缓存机制

- 验证结果缓存到 `cache/validation_cache.json`
- 支持断点续传
- 缓存有效期24小时

## License

MIT
