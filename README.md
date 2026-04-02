# 🌐 全球 IPTV 直播源自动爬虫

> Global IPTV Auto Scraper — 自动抓取全球 IPTV 直播源，支持测速过滤、别名标准化、台标注入，覆盖港台/日韩/欧美等 40+ 国家。

[![Python 3](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ 功能特点

| 功能 | 说明 |
|------|------|
| 🌐 **多源抓取** | 支持 12+ 个 IPTV 数据源，自动去重 |
| ⚡ **自动测速** | CDN 白名单跳过测速，其他进行速度测试过滤慢速源 |
| 🇭🇰 **HK 过滤** | 自动识别和归类香港频道（TVB/ViuTV/RTHK/HOY TV/Now TV） |
| 🏷️ **别名标准化** | 760+ 频道别名映射，消除重复频道 |
| 🔗 **频道合并** | 同名频道保留最佳 URL，自动选择最快源 |
| 🎨 **台标注入** | 集成 EPG 台标，播放器内显示频道图标 |
| 🔄 **备用频道** | 每频道最多 3 个备用源，自动切换 |

---

## 📁 项目结构

```
iptv-scraper/
├── main.py                 # 🚀 主入口
├── fetch_sources.py        # 📡 数据源配置
├── filter_hk.py           # 🇭🇰 HK 频道过滤
├── generate_playlist.py   # 📝 生成播放列表（含验证 + 测速）
│
├── lib/                    # 🛠️ 工具库
│   ├── cache.py           # 统一缓存管理
│   ├── helpers.py         # 通用辅助函数
│   ├── speedtest.py       # 测速（iptv-validator 不可用时的 fallback）
│   └── whitelist.py       # CDN 白名单
│
├── fetch/                  # 🌐 抓取模块
│   ├── sources.py          # 数据源定义
│   └── download.py         # 下载器
│
├── group/                  # 🗂️ 分组模块
│   ├── categorizer.py     # 频道分类器
│   └── normalize.py       # 名称标准化
│
├── output/                 # 📤 输出模块
│   └── playlist.py        # M3U 生成器
│
├── cache/                  # 💾 缓存
├── sources/               # 📥 抓取的源数据
└── output/                 # 📤 输出的 M3U 文件
    ├── hk_merged.m3u      # 🇭🇰 香港台湾频道
    └── all_merged.m3u     # 🌍 全球频道
```

---

## 🔄 工作流

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py (主入口)                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │  1. fetch_sources   │  从多个数据源下载 M3U
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │  2. filter_hk      │  过滤 HK/TW/MO 频道
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────────────────────────┐
        │  3. generate_playlist                   │
        │  ┌─────────────────────────────────┐   │
        │  │  SKIP_VALIDATION=0:             │   │
        │  │    → batch_validate (HEAD+GET)  │   │
        │  │    → speedtest_channels (curl)   │   │
        │  │    → filter + sort by speed      │   │
        │  │                                  │   │
        │  │  SKIP_VALIDATION=1:             │   │
        │  │    → 使用缓存 + CDN 白名单        │   │
        │  │    → speedtest fallback           │   │
        │  └─────────────────────────────────┘   │
        └─────────────────┬────────────────────┘
                          │
              ┌───────────▼───────────┐
              │  output/hk_merged.m3u │
              │  output/all_merged.mu │
              └───────────────────────┘
```

---

## 📺 分组规范

### 🇭🇰 香港频道 (`hk_merged.m3u`)

| 分组 | 包含频道 |
|------|----------|
| 📺 TVB | 翡翠台、明珠台、J2、新闻台等 |
| 📺 ViuTV | ViuTV、ViuTVsix |
| 📺 RTHK | 香港电台所有频道 |
| 📺 HOY TV | HOY TV 系列 |
| 📺 Now TV | Now TV 系列 |
| 🇹🇼 台湾 | 台湾主要频道 |
| 🇲🇴 澳门 | 澳门主要频道 |
| 📺 凤凰卫视 | 凤凰卫视中文台、资讯台等 |
| 📺 香港其他 | 其他香港频道 |

### 🌍 全球频道 (`all_merged.m3u`)

| 分组 | 包含频道 |
|------|----------|
| 📺 央视频道 | CCTV1-17、CETV 等 |
| 📺 各省频道 | 北京、上海、广东、四川等各省份频道 |
| 📡 卫视频道 | 境外卫视 |
| 📺 TVB / ViuTV / RTHK / HOY TV / Now TV | 香港主要频道 |
| 🇹🇼 台湾 | 台湾频道 |
| 🇲🇴 澳门 | 澳门频道 |
| 🎬 电影频道 | HBO、Star Movies 等 |
| 🎵 音乐频道 | MTV、V Channels 等 |
| 🌐 国际频道 | CNN、BBC、Al Jazeera 等 |
| 📰 新闻财经 | 新闻财经频道 |
| 🧸 儿童频道 | 儿童频道 |
| 🎭 综艺频道 | 综艺娱乐 |
| ⚽ 体育频道 | 体育频道 |
| 📺 纪录片 | 纪录片频道 |
| 🌎 美洲 / 🌏 亚洲 / 🌍 欧洲 / 🌎 非洲 | 地区频道 |

---

## 📊 数据源

当前配置 **20 个数据源**，按优先级排序：

| 优先级 | 源 | 频道数 | 更新 | 特点 |
|--------|------|--------|------|-------|
| 1 | [sammy0101](https://github.com/sammy0101/hk-iptv-auto) | ~62 | 每日 | HK CDN |
| 2 | [xiweiwong-hk-iptv](https://github.com/xiweiwong/hk-iptv-auto) | ~100+ | 每日 | HK CDN |
| 2 | [zhi35-iptv](https://live.zhi35.com/iptv.m3u) | ~522 | 不定期 | 台标 |
| 2 | [freetv-fun](https://t.freetv.fun/m3u/playlist.m3u) | ~4187 | 每日 | 最大综合 |
| 2 | [epg-pw](https://epg.pw/test_channels.m3u) | ~4084 | 每日 | 测试源 |
| 3 | [fanmingming-live](https://github.com/fanmingming/live) | ~82 | 每日 | 官方源 |
| 3 | [CCSH-iptv](https://github.com/CCSH/IPTV) | ~4414 | 每日 | 综合源 |
| 3 | [gitee-why006-TV](https://gitee.com/why006/TV) | ~1162 | 每日2次 | Gitee |
| 4 | [iptv-org](https://github.com/iptv-org/iptv) | ~11000+ | 社区 | 全球最大 |
| 4 | [hujingguang-iptv](https://github.com/hujingguang/ChinaIPTV) | ~100+ | 不定期 | 湖南台 |
| 4 | [Harbin-byte-iptv](https://github.com/Harbin-byte/iptv) | ~50+ | 不定期 | 质量优先 |
| 4 | [suxuang-myIPTV](https://github.com/suxuang/myIPTV) | ~1271 | 不定期 | 手动 |
| 5 | [vbskycn-iptv4](https://live.zbds.top/tv/iptv4.m3u) | ~800+ | 每6小时 | IPv4/IPv6 |

**Free-TV 系列**（按地区）: [HK](https://github.com/Free-TV/IPTV/tree/master/lists) · [TW](https://github.com/Free-TV/IPTV/tree/master/lists) · [CN](https://github.com/Free-TV/IPTV/tree/master/lists) · [JP](https://github.com/Free-TV/IPTV/tree/master/lists) · [KR](https://github.com/Free-TV/IPTV/tree/master/lists) · [US](https://github.com/Free-TV/IPTV/tree/master/lists) · [UK](https://github.com/Free-TV/IPTV/tree/master/lists)


## 🚀 快速开始

### 环境要求

- Python 3.8+
- FFmpeg（用于测速）
- curl（用于速度测试）

### 安装依赖

```bash
pip install requests
```

### 运行

```bash
# 完整抓取（下载 + 验证 + 测速 + 合并）
python3 main.py

# 快速模式：跳过验证，使用缓存 + CDN 白名单
SKIP_VALIDATION=1 python3 main.py

# 调整最低速度阈值（单位：KB/s）
MIN_SPEED_KB=50 python3 main.py

# 自定义输出目录
OUTPUT_DIR=/path/to/output python3 main.py
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SKIP_VALIDATION` | `0` | 设为 `1` 跳过验证，使用缓存数据 |
| `MIN_SPEED_KB` | `30` | 最低速度阈值（KB/s） |
| `OUTPUT_DIR` | `./output` | 输出目录 |
| `CACHE_DIR` | `./cache` | 缓存目录 |

---

## 📤 输出文件

```
output/
├── hk_merged.m3u      # 香港台湾频道列表
│   ├── group-title="📺 TVB"
│   ├── group-title="📺 ViuTV"
│   └── ...
│
└── all_merged.m3u     # 全球频道列表
    ├── group-title="📺 央视频道"
    ├── group-title="📺 各省频道"
    ├── group-title="🌐 国际频道"
    └── ...
```

---



---

## 🏗️ 架构说明

本项目采用 **iptv-scraper + iptv-validator** 分离架构：

```
┌─────────────────────────────────────────────────────────────┐
│ iptv-scraper (每天 03:00 AM)                              │
│                                                              │
│ 1. 从 iptv-validator pull 验证缓存                         │
│ 2. 运行 scraper（SKIP_VALIDATION=1，使用缓存验证结果）     │
│ 3. Push output/ + filtered/ → iptv-scraper                 │
└─────────────────────────────────────────────────────────────┘
                              ↓ filtered/
┌─────────────────────────────────────────────────────────────┐
│ iptv-validator (每天 03:30 AM)                             │
│                                                              │
│ 1. 从 iptv-scraper pull filtered 文件                      │
│ 2. 并发验证 URL（100 workers）                             │
│ 3. Push cache → iptv-validator                              │
└─────────────────────────────────────────────────────────────┘
```

### 优势

| 优势 | 说明 |
|------|------|
| ⚡ **快速抓取** | scraper 不做验证，只负责抓取和输出 |
| ✅ **准确验证** | validator 专门做 URL 验证，支持并发 |
| 🔒 **权限安全** | 每个项目只推送自己的仓库，无跨仓库权限问题 |
| 📊 **分级调度** | HK: 1天 / China: 7天 / Global: 30天 |

### 缓存机制

- **iptv-validator** 生成 `cache/validation_cache.json`
- **iptv-scraper** 使用该缓存跳过验证
- 缓存格式：URL → {valid, last_validated, tier}

### 独立运行

如需单独运行 scraper：

```bash
# 使用 iptv-validator 的缓存（推荐）
SKIP_VALIDATION=1 python main.py

# 不使用缓存（使用内置 speedtest fallback）
python main.py
```

---

## 🔧 模块说明

### 抓取模块 (`fetch/`)

负责从各数据源下载 M3U 文件：

```python
from fetch.sources import SOURCES
from fetch.download import download_all

# 下载所有源
sources_data = download_all(SOURCES)
```

### 生成播放列表 (`generate_playlist.py`)

核心模块，包含验证、测速、合并逻辑：

```python
from generate_playlist import main as generate_main

# 生成播放列表（自动验证 + 测速）
generate_main()
```

### 测速 fallback（`lib/speedtest.py`）

当 iptv-validator 不可用时，使用 curl/requests 进行速度测试：

```python
from lib.speedtest import speedtest_channels, filter_by_speed

# 测速所有频道
cache = speedtest_channels(channels, logger, min_speed_kb=30)
```

### CDN 白名单（`lib/whitelist.py`）

已知的可靠 CDN 域名列表，跳过验证和测速：

```python
from lib.whitelist import is_whitelisted

if is_whitelisted(url):
    # 可信 CDN，无需验证
    pass
```

### 分组模块 (`group/`)

频道分类和名称标准化：

```python
from group.categorizer import categorize
from group.normalize import normalize_name

# 标准化频道名
name = normalize_name("CCTV-1 综合")  # -> "CCTV1"
# 分类频道
category = categorize(name)  # -> "央视频道"
```

### 输出模块 (`output/`)

生成最终 M3U 文件：

```python
from output.playlist import generate_playlist

# 生成播放列表
generate_playlist(channels, output_file)
```

---

## 🗺️ 路线图

- [ ] 添加更多数据源
- [ ] 支持更多地区分组
- [ ] Web 界面
- [ ] Docker 部署
- [ ] 自动更新机制

---

## ⚠️ 免责声明

本项目仅供学习和研究使用。请遵守当地法律法规，不要使用本项目观看受版权保护的内容。使用本项目产生的任何问题由使用者自行承担。

---

## 📄 许可证

MIT License

---

> 最后更新：2026-04-01
