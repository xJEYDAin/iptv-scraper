# HK IPTV 自动爬虫

自动化的 IPTV 频道爬虫，专注覆盖香港、台湾及亚太地区。支持定时运行、流媒体可用性验证、下载速度测试，并生成优化过的 M3U 播放列表。

[![更新计划](https://img.shields.io/github/actions/workflow/status/xJEYDAin/iptv-scraper/update.yml?label=daily%20update&style=flat-square)](https://github.com/xJEYDAin/iptv-scraper/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)](https://www.python.org/)

## 📺 播放列表

| 列表 | 链接 | 说明 |
|------|------|------|
| **香港频道** | `https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/hk_merged.m3u` | 专注香港地区频道 |
| **全部频道** | `https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/all_merged.m3u` | 所有抓取的频道（港 + 台 + 陆 + 更多） |

> 可使用任意支持 IPTV 的播放器打开这些链接，如 [VLC](https://www.videolan.org/)、[mpv](https://mpv.io/)、[Kodi](https://kodi.tv/) 等。参见 [awesome-iptv](https://github.com/iptv-org/awesome-iptv#apps)。

---

## ✨ 功能特性

- **🤖 自动抓取** — 每日从多个公开 M3U 数据源拉取频道
- **✅ 流媒体验证** — 上线前检查每个频道的可用性
- **⚡ 速度过滤** — 自动移除响应慢或无响应的流（阈值可配置）
- **🏷️ 频道名称标准化** — 59+ 条别名规则，确保跨源命名一致
- **🎨 台标自动匹配** — 自动匹配频道台标（EPG CDN + Imgur 备用）
- **📺 VLC 优化** — 内置 network-caching 和超时参数，播放更流畅
- **💾 缓存机制** — 24 小时验证缓存 + 检查点支持，加快重复运行
- **🗓️ 每日自动更新** — GitHub Actions 每日 03:00 UTC 执行

---

## 📂 项目结构

```
iptv-scraper/
├── main.py                  # 入口文件：协调整个处理流程
├── config.py                # 共享配置（路径、速度阈值等）
├── fetch_sources.py         # 步骤 1：从数据源抓取原始 M3U
├── filter_hk.py             # 步骤 2：过滤港台及地区频道
├── validate_and_merge.py    # 步骤 3：验证 URL 并合并结果
├── speedtest.py             # 步骤 4：测试每个流的下载速度
├── generate_playlist.py     # 步骤 5：生成带台标和 VLC 参数的 M3U
├── utils.py                 # 共享工具（日志、文件操作）
├── alias.txt                # 频道名 → 标准名映射
├── logo_map.py              # 频道名 → 台标 URL 映射
├── output/                  # 生成的 M3U 播放列表（git 跟踪）
├── sources/                 # 原始抓取的 M3U 文件（git 忽略）
├── filtered/                # 中间过滤结果（git 忽略）
├── cache/                   # 验证缓存（git 忽略）
└── logs/                    # 运行日志（git 忽略）
```

---

## 🚀 快速上手

### 本地运行

```bash
# 1. 克隆项目
git clone https://github.com/xJEYDAin/iptv-scraper.git
cd iptv-scraper

# 2. 安装依赖
pip install requests

# 3. 运行
python main.py
```

### Docker 运行

```bash
# 构建镜像
docker build -t iptv-scraper .

# 运行（跳过速度测试可加快执行）
docker run --rm \
  -e ENABLE_SPEEDTEST=false \
  -v $(pwd)/output:/app/output \
  iptv-scraper
```

### GitHub Actions（Fork 后自动更新）

1. Fork 本仓库
2. 进入 **Actions** 页面，开启工作流
3. 爬虫将每日 03:00 UTC 自动运行
4. 播放列表会自动提交到 `master` 分支的 `output/` 目录

手动触发：Actions → **Update HK IPTV** → **Run workflow**

---

## ⚙️ 配置项

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `ENABLE_SPEEDTEST` | `true` | 是否启用速度测试（`true` / `false`） |
| `MIN_SPEED_KB` | `500` | 最低速度阈值（KB/s），低于此值的流会被丢弃 |
| `SORT_BY_SPEED` | `true` | 按速度从快到慢排序（`true`）或按字母排序（`false`） |
| `SPEEDTEST_TIMEOUT` | `5` | 每个 URL 速度测试的超时时间（秒） |
| `SPEEDTEST_WORKERS` | `10` | 并行速度测试的线程数 |
| `SKIP_VALIDATION` | `0` | 设为 `1` 可复用缓存的验证结果（加快开发调试） |
| `GITHUB_ACTIONS` | `auto` | 自动检测；在 CI 环境中会自动缩短超时 |

**使用示例：**

```bash
# 跳过速度测试，快速测试
ENABLE_SPEEDTEST=false python main.py

# 提高速度阈值（只保留快速流）
MIN_SPEED_KB=1000 python main.py

# 复用缓存的验证结果
SKIP_VALIDATION=1 python main.py
```

---

## 🔍 数据来源

| 来源 | 类型 | 地区覆盖 |
|------|------|----------|
| [sammy0101/hk-iptv-auto](https://github.com/sammy0101/hk-iptv-auto) | M3U | 🇭🇰 香港（每日自动更新） |
| [nthack/IPTVM3U](https://github.com/nthack/IPTVM3U) | M3U | 🇭🇰 香港 / 🇹🇼 台湾 |
| [imDazui/Tvlist-awesome-m3u-m3u8](https://github.com/imDazui/Tvlist-awesome-m3u-m3u8) | M3U | 🇭🇰 香港 / 🇹🇼 台湾 |
| [iptv-org/iptv](https://github.com/iptv-org/iptv) | M3U | 🌍 全球 |
| [Free-TV/IPTV](https://github.com/Free-TV/IPTV) | M3U | 🌍 40+ 国家 |

> 频道在收录前都会经过验证和测速。速度过慢或失效的流会被自动移除。

---

## 📡 VLC 播放优化

生成的 M3U 文件内置了 VLC 专用标签，确保稳定播放：

```
#EXTVLCOPT:network-caching=1000
#EXTVLCOPT:live-caching=1000
#EXTVLCOPT:timeout=10
```

| 参数 | 值 | 作用 |
|------|-----|------|
| `network-caching` | 1000ms | 减少网络抖动缓冲 |
| `live-caching` | 1000ms | 直播流缓冲 |
| `timeout` | 10s | 连接超时时间 |

---

## ❓ 常见问题

**Q: 有些频道打不开怎么办？**
A: IPTV 频道经常是临时性的，爬虫每日重新验证，失效频道会被自动过滤。如果某个频道缺失，可能是因为它已从所有上游仓库中移除。

**Q: 想添加一个缺失的频道怎么办？**
A: 频道需要先出现在上游数据源中。可以去相应的上游仓库提交 PR。

**Q: 可以改成每天多次运行吗？**
A: 可以——修改 `.github/workflows/update.yml` 中的 cron 表达式即可。不过过于频繁的运行可能会增加上游仓库的负担。

**Q: 速度过滤是怎么工作的？**
A: 每个流 URL 都会在短超时内下载，测量其吞吐量（KB/s）。低于 `MIN_SPEED_KB` 的流不会出现在输出结果中。

**Q: 这个项目合法吗？**
A: 本项目仅聚合公开可用的 M3U 链接，不托管或二次分发受版权保护的内容。用户需自行遵守当地法律法规。

---

## 🤝 参与贡献

欢迎提交贡献！请先阅读以下指南。

### 添加或修复频道

本项目聚合自上游 M3U 数据源。如需添加或修复频道，请向上游仓库提交 PR：

- 香港 / 台湾频道 → [sammy0101/hk-iptv-auto](https://github.com/sammy0101/hk-iptv-auto)
- 全球频道 → [iptv-org/iptv](https://github.com/iptv-org/iptv) 或 [Free-TV/IPTV](https://github.com/Free-TV/IPTV)

### 本项目自身的问题

如遇到爬虫本身的问题（验证逻辑、速度测试、台标匹配等）：

1. 开 Issue 描述问题
2. 或直接提交 PR 修复

### 更新别名 / 台标映射

如需更新频道名称标准化规则或台标映射，请编辑：
- `alias.txt` — 频道名别名
- `logo_map.py` — 频道名 → 台标 URL

---

## 📄 开源许可

MIT — 可自由使用、修改和分发。
