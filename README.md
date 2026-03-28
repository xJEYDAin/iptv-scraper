# HK IPTV Auto Scraper

自动抓取香港 IPTV 直播源，每日更新。

## 功能

- 🤖 自动抓取多个数据源
- 🔍 筛选香港频道
- ✅ 验证直播源有效性
- 📝 分类整理（香港/台湾/大陆/电影/体育等）
- 💾 验证缓存，支持断点续传
- 🏷️ **别名映射** - 59条频道名称标准化（alias.txt）
- ⚡ **测速过滤** - 自动过滤低速链接（默认 <500KB/s）
- 🎨 **台标注入** - 自动匹配频道台标（logo_map.py）
- 📺 **VLC 优化参数** - 输出最佳播放参数

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
https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/hk_merged.m3u
```

### 全部频道
```
https://raw.githubusercontent.com/xJEYDAin/iptv-scraper/master/output/all_merged.m3u
```

## 使用方法

### 本地运行

```bash
# 安装依赖
pip install requests

# 运行
python main.py
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MIN_SPEED_KB` | `500` | 最低网速阈值（KB/s），低于此值的链接会被过滤 |
| `ENABLE_SPEEDTEST` | `true` | 是否启用测速（`true`/`false`） |
| `SORT_BY_SPEED` | `true` | 是否按网速排序（`true`=快到慢，`false`=字母序） |
| `SPEEDTEST_TIMEOUT` | `5` | 单个 URL 测速超时（秒） |
| `SPEEDTEST_WORKERS` | `10` | 并行测速线程数 |
| `GITHUB_ACTIONS` | `auto` | 在 GitHub Actions 环境自动设为 `true`，缩短超时 |

**示例：**

```bash
# 跳过测速（快速测试）
ENABLE_SPEEDTEST=false python main.py

# 提高最低网速要求（只保留优质链接）
MIN_SPEED_KB=1000 python main.py

# 关闭按网速排序（按字母顺序）
SORT_BY_SPEED=false python main.py
```

### GitHub Actions 自动更新

1. Fork 本项目
2. 在 Actions 页面启用 workflow
3. 每天凌晨3点自动更新

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `fetch_sources.py` | 抓取数据源 |
| `filter_hk.py` | 筛选香港频道 |
| `validate_and_merge.py` | 验证并合并 |
| `speedtest.py` | 测速模块，过滤低速链接 |
| `generate_playlist.py` | 生成播放列表（含台标注入、VLC参数） |
| `logo_map.py` | 频道台标映射表 |
| `alias.txt` | 频道别名标准化映射 |
| `utils.py` | 工具函数 |

## 配置说明

### 别名映射（alias.txt）

频道名称标准化映射，统一不同数据源的同一频道命名。

**格式：**
```
原始名称 -> 标准名称
```

**示例：**
```
ViuTV -> ViuTV
viutv -> ViuTV
TVB J2 -> TVB J2
J2台 -> TVB J2
RTHK 31 -> RTHK 31
港台电视RTHK31 -> RTHK 31
```

**支持覆盖：**
- TVB 系列（翡翠台、明珠台、J2、新闻台、财经台等）
- ViuTV / ViuTVsix
- RTHK 31/32/33
- HOY TV
- Now TV 系列
- 有线电视
- 凤凰卫视
- 澳广视

### 台标注入（logo_map.py）

自动为频道匹配台标，使用 EPG CDN（epg.112114.xyz/logo/）和 Imgur 备用源。

**匹配逻辑（优先级）：**
1. 精确匹配标准化名称
2. 前缀匹配（由长到短尝试）
3. 模糊包含匹配（关键词 ≥5 字符防误匹配）

**支持的频道：**
- 📺 TVB 系列（翡翠台、明珠台、J2、新闻台、电视剧台等）
- 📺 ViuTV / ViuTVsix
- 📺 RTHK 31/32/33/34/35
- 📺 HOY TV
- 📺 Now TV 系列
- 📺 有线电视 / Cable TV
- 📺 凤凰卫视
- 📺 台湾主流频道（TVBS、台视、中视、华视、民视、东森、三立等）
- 📺 澳门频道
- 📺 国际频道（BBC、CNN、Al Jazeera、NHK 等）
- 🎬 电影频道（HBO、Star Movies、AMC 等）
- ⚽ 体育频道（ESPN、Fox Sports、BeIN 等）
- 🧸 儿童频道（Nick、Disney、Animax 等）
- 🌍 探索/纪录片（Discovery、National Geographic、History 等）

## VLC 优化参数

生成的 M3U8 文件包含 VLC 优化的播放参数，确保最佳兼容性：

```
#EXTVLCOPT:network-caching=1000
#EXTVLCOPT:live-cacheing=1000
#EXTVLCOPT:timeout=10
```

**参数说明：**

| 参数 | 值 | 说明 |
|------|-----|------|
| `network-caching` | 1000ms | 网络缓存，避免卡顿 |
| `live-caching` | 1000ms | 直播流缓存 |
| `timeout` | 10s | 连接超时时间 |

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
