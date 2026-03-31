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
├── validate_and_merge.py  # 🔍 验证和合并
├── generate_playlist.py    # 📝 生成播放列表
├── legacy.py              # 🔧 兼容层
│
├── lib/                    # 🛠️ 工具库
│   ├── helpers.py          # 通用辅助函数
│   └── whitelist.py        # CDN 白名单
│
├── fetch/                  # 🌐 抓取模块
│   ├── sources.py          # 数据源定义
│   └── download.py         # 下载器
│
├── validate/               # ✅ 验证模块
│   ├── validators.py      # 速度验证器
│   └── cache.py           # 缓存管理
│
├── group/                  # 🗂️ 分组模块
│   ├── categorizer.py     # 频道分类器
│   └── normalize.py       # 名称标准化
│
├── output/                 # 📤 输出模块
│   └── playlist.py        # M3U 生成器
│
├── sources/                # 📥 抓取的源数据
└── output/                 # 📤 输出的 M3U 文件
    ├── hk_merged.m3u      # 🇭🇰 香港台湾频道
    └── all_merged.m3u     # 🌍 全球频道
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

| 源 | 类型 | 预估频道数 | 备注 |
|----|------|-----------|------|
| iptv-org | M3U | ~11,000 | 最大源 |
| vbskycn-iptv4 | M3U | ~600 | |
| zhi35-iptv | M3U | ~522 | |
| hujingguang-iptv | M3U | ~65 | |
| sammy0101 | M3U | ~55 | |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- FFmpeg（用于测速）

### 安装依赖

```bash
pip install requests
```

### 运行

```bash
# 完整抓取（下载 + 测速 + 合并）
python3 main.py

# 跳过验证（使用缓存数据，适合快速测试）
SKIP_VALIDATION=1 python3 main.py

# 调整最低速度阈值（单位：KB/s）
MIN_SPEED_KB=50 python3 main.py

# 自定义输出目录
OUTPUT_DIR=/path/to/output python3 main.py
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SKIP_VALIDATION` | `0` | 设为 `1` 跳过速度验证 |
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

## 🔧 模块说明

### 抓取模块 (`fetch/`)

负责从各数据源下载 M3U 文件：

```python
from fetch.sources import SOURCES
from fetch.download import download_all

# 下载所有源
sources_data = download_all(SOURCES)
```

### 验证模块 (`validate/`)

对频道 URL 进行速度测试：

```python
from validate.validators import speed_test
from validate.cache import Cache

# 速度测试
result = speed_test(url, min_speed=30)
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
