#!/usr/bin/env python3
"""Channel categorization and grouping logic."""
import re
from typing import Dict, List


# ──────────────────────────────────────────────────────────────
#  各省关键词（优先精确匹配）
# ──────────────────────────────────────────────────────────────
PROVINCE_KEYWORDS = {
    "📺 北京":          [r"北京卫视", r"北京科教", r"北京文艺", r"北京影视", r"北京财经", r"北京新闻", r"北京生活", r"北京青年", r"北京文艺频道"],
    "📺 上海":          [r"上海卫视", r"上海东方", r"上海新闻", r"上海都市", r"上海第一", r"上海艺术", r"上海生活", r"上海外语", r"上海综艺"],
    "📺 广东":          [r"广东卫视", r"广东珠江", r"广东新闻", r"广东体育", r"广东影视", r"广东综艺", r"广州卫视", r"广州新闻"],
    "📺 深圳":          [r"深圳卫视", r"深圳娱乐", r"深圳都市", r"深圳新闻", r"深圳公共", r"深圳财经"],
    "📺 浙江":          [r"浙江卫视", r"浙江新闻", r"浙江钱江", r"浙江经济", r"浙江教育", r"浙江影视", r"浙江民生", r"浙江体育"],
    "📺 江苏":          [r"江苏卫视", r"江苏新闻", r"江苏城市", r"江苏综艺", r"江苏影视", r"江苏体育", r"江苏教育", r"江苏公共"],
    "📺 湖南":          [r"湖南卫视", r"湖南新闻", r"湖南经视", r"湖南都市", r"湖南娱乐", r"湖南电视剧", r"湖南公共", r"湖南教育"],
    "📺 安徽":          [r"安徽卫视", r"安徽新闻", r"安徽经济", r"安徽综艺", r"安徽影视", r"安徽公共", r"安徽科教"],
    "📺 山东":          [r"山东卫视", r"山东新闻", r"山东齐鲁", r"山东体育", r"山东综艺", r"山东影视", r"山东公共", r"山东农科"],
    "📺 四川":          [r"四川卫视", r"四川新闻", r"四川经济", r"四川文旅", r"四川影视", r"四川综艺", r"四川公共", r"四川科教"],
    "📺 湖北":          [r"湖北卫视", r"湖北新闻", r"湖北经视", r"湖北综合", r"湖北影视", r"湖北教育", r"湖北公共", r"湖北垄上"],
    "📺 福建":          [r"福建卫视", r"福建东南", r"福建新闻", r"福建综合", r"福建经济", r"福建海峡", r"厦门卫视", r"厦门综合"],
    "📺 陕西":          [r"陕西卫视", r"陕西新闻", r"陕西都市", r"陕西文艺", r"陕西体育", r"陕西农林卫视", r"陕西音乐"],
    "📺 黑龙江":        [r"黑龙江卫视", r"黑龙江新闻", r"黑龙江都市", r"黑龙江文艺", r"黑龙江公共", r"黑龙江农业"],
    "📺 吉林":          [r"吉林卫视", r"吉林新闻", r"吉林都市", r"吉林乡村", r"吉林公共", r"吉林影视"],
    "📺 辽宁":          [r"辽宁卫视", r"辽宁新闻", r"辽宁都市", r"辽宁综合", r"辽宁经济", r"辽宁青少", r"辽宁体育"],
    "📺 河北":          [r"河北卫视", r"河北新闻", r"河北经济", r"河北都市", r"河北影视", r"河北公共", r"河北农民"],
    "📺 河南":          [r"河南卫视", r"河南新闻", r"河南都市", r"河南法治", r"河南公共", r"河南民生", r"河南乡村", r"河南经济"],
    "📺 江西":          [r"江西卫视", r"江西新闻", r"江西都市", r"江西经济", r"江西影视", r"江西公共", r"江西农业"],
    "📺 山西":          [r"山西卫视", r"山西新闻", r"山西黄河", r"山西公共", r"山西科教", r"山西文体"],
    "📺 内蒙古":        [r"内蒙古卫视", r"内蒙古新闻", r"内蒙古文体", r"内蒙古牧区"],
    "📺 宁夏":          [r"宁夏卫视", r"宁夏新闻", r"宁夏公共", r"宁夏经济", r"宁夏文旅"],
    "📺 青海":          [r"青海卫视", r"青海新闻", r"青海经济", r"青海综合"],
    "📺 甘肃":          [r"甘肃卫视", r"甘肃新闻", r"甘肃经济", r"甘肃文化", r"甘肃公共", r"甘肃都市"],
    "📺 新疆":          [r"新疆卫视", r"新疆新闻", r"新疆经济", r"新疆文体", r"新疆兵团"],
    "📺 西藏":          [r"西藏卫视", r"西藏新闻", r"西藏综合", r"西藏文化"],
    "📺 贵州":          [r"贵州卫视", r"贵州新闻", r"贵州综合", r"贵州经济", r"贵州公共", r"贵州影视"],
    "📺 云南":          [r"云南卫视", r"云南新闻", r"云南都市", r"云南经济", r"云南文旅", r"云南公共", r"云南娱乐"],
    "📺 广西":          [r"广西卫视", r"广西新闻", r"广西综合", r"广西综艺", r"广西都市", r"广西公共", r"广西资讯"],
    "📺 海南":          [r"海南卫视", r"海南新闻", r"海南综合", r"海南文旅", r"海南经济", r"海南公共"],
    "📺 重庆":          [r"重庆卫视", r"重庆新闻", r"重庆都市", r"重庆科教", r"重庆文体", r"重庆娱乐", r"重庆生活"],
    "📺 天津":          [r"天津卫视", r"天津新闻", r"天津文艺", r"天津科教", r"天津体育", r"天津都市", r"天津公共"],
}

# ──────────────────────────────────────────────────────────────
#  Helper
# ──────────────────────────────────────────────────────────────
def _match(name_lower: str, group_lower: str, patterns: list) -> bool:
    """Return True if any pattern matches in name or group.
    
    Uses case-insensitive search. Note: Python's \\b word boundary treats
    CJK chars as \\w (word chars), so \\b fails at ASCII/CJK boundaries.
    Patterns should NOT use trailing \\b before possible CJK chars.
    """
    full = name_lower + " " + group_lower
    return any(re.search(p, full, re.IGNORECASE) for p in patterns)


def _excluded(name_lower: str, group_lower: str) -> bool:
    """Patterns that disqualify a channel from specialized categories.
    
    Note: \\b word boundaries don't work at ASCII/CJK boundaries (CJK is \\w).
    Patterns use simple substring matching instead.
    """
    # clang-format off
    exclude = [
        r"cctv", r"cetv",
        r"aljazeera", r"al jazeera",
        r"bbc", r"cnn",
        r"fox news",
        r"bloomberg", r"cnbc",
        r"16tv", r"16 tv",
        r"viutv", r"viu tv",
        r"tvb", r"翡翠台", r"明珠台", r"j2",
        r"rthk",
        r"hoy", r"hoytv",
        r"nowtv", r"now tv",
        r"cable", r"有线", r"开电视",
        r"凤凰", r"phoenix",
        r"star tv", r"startv",
        r"star movies", r"fox movies",
        r"hbo", r"cinemax", r"amc", r"paramount", r"mgm",
        r"channel v", r"channelv", r"mtv",
        r"nhk", r"tbs",
        r"disney", r"cartoon", r"nickelodeon",
        r"disney channel",
        r"espn", r"fox sports", r"beinsport", r"bein sport",
        r"african", r"africable",
        r"budapest", r"bogota", r"brasil", r"brazil",
        r"ktv",
        r"daystar",
    ]
    # clang-format on
    full = name_lower + " " + group_lower
    return any(re.search(p, full, re.IGNORECASE) for p in exclude)


# ──────────────────────────────────────────────────────────────
#  is_hk_region — 保留（其他模块仍用）
# ──────────────────────────────────────────────────────────────
def is_hk_region(name: str, group: str, cat: str = None) -> bool:
    """判断是否为港台地区频道 (HK/TW/MO)
    
    Args:
        name: channel name
        group: group-title from m3u
        cat: optional category (from categorize()) for exclusion
    """
    name_lower, group_lower = name.lower(), (group or "").lower()
    full_text = name_lower + " " + group_lower

    hk_exact = [
        r"hkdtmb", r"香港台", r"香港電視",
        r"tvb", r"翡翠台", r"明珠台", r"j2", r"j1",
        r"viutv", r"viu tv", r"viu6", r"viu 6",
        r"rthk", r"rthk tv", r"港台電視", r"港台电视", r"香港电台",
        r"hoy tv", r"hoytv",
        r"now tv", r"nowtv", r"now直播", r"now财经", r"nownews",
        r"有线电视", r"开电视", r"cable tv", r"cable_tv",
        r"凤凰卫视", r"phoenix tv",
        r"无线电视", r"无线新闻", r"星空卫视",
    ]
    tw_exact = [
        r"tvbs", r"tvbs新闻",
        r"台视主频", r"台視主頻",
        r"中视综合台", r"中視綜合台",
        r"民视无线台", r"民視無限",
        r"东森电视", r"東森電視", r"东森新闻", r"東森新聞",
        r"三立台湾台", r"三立台灣台",
        r"华视", r"華視", r"中视", r"中視", r"民视", r"民視",
        r"台视", r"台視", r"大爱", r"公视", r"公視",
        r"\\bttv\b", r"\\bftv\b", r"\\bpts\b", r"\\bcna\b",
    ]
    mo_exact = [r"澳门", r"澳視", r"\\bmacau\b", r"澳广视", r"澳亚卫视"]

    exclude = [
        r"\bcctv\b", r"\bcetv\b", r"教育台",
        r"\bcctv[_\- ]", r"\bcetv[_\- ]",
        r"\bbbc\b", r"\bcnn\b",
        r"\bal jazeera\b", r"\baljazeera\b", r"\bfrance 24\b",
        r"bloomberg", r"cnbc", r"euronews",
        r"16tv", r"16 tv",
        r"african", r"africable",
        r"budapest",
        r"bogota", r"brasil", r"brazil",
        r"\bktv\b",
        r"\bmtv\b", r"\bm tv\b",
        r"star tv", r"startv",
        r"daystar",
        r"café", r"cafe",
        r"国际频道", r"国际新闻",
        r"央视频道", r"央视新闻",
    ]

    for p in exclude:
        if re.search(p, full_text):
            return False

    # Explicitly reject CCTV/CETV (must check before positive matches)
    if re.search(r"\bcctv[\-_\s]?\d*\b", name_lower) or re.search(r"\bcetv[\-_\s]?\d*\b", name_lower):
        return False
    if "教育台" in name or "央视" in name:
        return False
    # Reject 央视频道 / 央视新闻
    if re.search(r"央视频道|央视新闻", full_text):
        return False
    # Reject non-HK group categories
    non_hk_groups = [
        "央视频道", "国际频道", "国际新闻", "新闻财经",
        "电影频道", "音乐频道", "儿童频道", "体育频道",
        "纪录片", "综艺频道", "地方频道",
        "欧洲", "北美", "拉丁美洲", "中东", "非洲", "大洋洲",
        "日本", "韩国", "亚洲（东南亚）", "亚洲（其他）", "印度",
        "🌐 国际",
    ]
    check_text = (group or "") + " " + (cat or "")
    if any(g in check_text for g in non_hk_groups):
        return False

    for p in hk_exact + tw_exact + mo_exact:
        if re.search(p, full_text):
            return True

    return False


# ──────────────────────────────────────────────────────────────
#  Logo URL 和频道名 → 国家/地区映射
# ──────────────────────────────────────────────────────────────
LOGO_REGION_PATTERNS = [
    # 中国源
    ("epg.112114.xyz/logo/TVB", "📺 TVB"),
    ("epg.112114.xyz/logo/翡翠台", "📺 TVB"),
    ("live.fanmingming.cn/tv/CH", "📺 央视频道"),
    ("gitee.com/suxuang", "🇨🇳 中国源"),
    # Astro 马来西亚
    ("ASTRO", "🇲🇾 马来西亚"),
    ("Astro", "🇲🇾 马来西亚"),
    # 澳大利亚
    ("Adelaide", "🇦🇺 澳大利亚"),
    ("Melbourne", "🇦🇺 澳大利亚"),
    ("Sydney", "🇦🇺 澳大利亚"),
]

CHANNEL_REGION_PATTERNS = [
    # Astro 马来西亚
    ("MOMOTV", "🇲🇾 马来西亚"),
    ("ASTROAOD", "🇲🇾 马来西亚"),
    # 澳大利亚
    ("Bold Adelaide", "🇦🇺 澳大利亚"),
    ("BoldAdelaide", "🇦🇺 澳大利亚"),
    # 荷兰
    ("AlmereTV", "🇳🇱 荷兰"),
    ("TwenteTV", "🇳🇱 荷兰"),
    # 宗教广播网
    ("3ABN", "🌐 宗教广播"),
    # 西班牙
    ("Televalencia", "🇪🇸 西班牙"),
    ("TeleValencia", "🇪🇸 西班牙"),
    # 意大利
    ("3Cat", "🇮🇹 意大利"),
    # 俄罗斯
    ("канал", "🇷🇺 俄罗斯"),
    # 北欧
    ("TV2", "🇳🇴 北欧"),
    # 非洲
    ("DSTV", "🌍 非洲"),
    ("Mnet", "🌍 非洲"),
    # 拉丁美洲 - 常见频道名模式
    ("TVCorrientes", "🌎 拉丁美洲"),
    ("TV Chile", "🌎 拉丁美洲"),
    ("Canal 13", "🌎 拉丁美洲"),
    ("Canal13", "🌎 拉丁美洲"),
    ("TV Brasil", "🌎 拉丁美洲"),
    ("TV Cultura", "🌎 拉丁美洲"),
    ("TV UNAM", "🌎 拉丁美洲"),
    ("VTV", "🌎 拉丁美洲"),
    # 波兰
    ("TVP", "🌍 欧洲"),
    ("Polsat", "🌍 欧洲"),
    ("TVN", "🌍 欧洲"),
]


# ──────────────────────────────────────────────────────────────
#  recategorize_others — 对"其他"分组中的频道进行二次分类
# ──────────────────────────────────────────────────────────────
def recategorize_others(name: str, group: str, logo: str = "") -> str:
    """对"其他"分组中的频道进行二次分类，返回更精确的分组。
    
    处理：
    1. 中文频道（省级/地方台）
    2. 国际频道（按国家/地区分类）
    """
    name_lower, group_lower = name.lower(), (group or "").lower()
    full_text = name_lower + " " + group_lower
    logo_lower = logo.lower() if logo else ""

    # ── 检测是否包含中文 ─────────────────────────────────────
    def has_cjk(s: str) -> bool:
        return any('\u4e00' <= c <= '\u9fff' for c in s)

    # ══════════════════════════════════════════════════════════
    #  0. 按 Logo URL 识别国家/地区（优先）
    # ══════════════════════════════════════════════════════════
    if logo_lower:
        for pattern, region in LOGO_REGION_PATTERNS:
            if pattern.lower() in logo_lower:
                return region

    # ══════════════════════════════════════════════════════════
    #  1. 中文频道分类
    # ══════════════════════════════════════════════════════════
    if has_cjk(name):
        # 新闻/资讯 → 合并到新闻财经
        if any(kw in name for kw in ['新闻', '资讯', '信息']):
            return "📰 新闻财经"
        # TVB 变体（黄金翡翠、翡翠台变体）
        if any(kw in name for kw in ['翡翠', '明珠', 'J2', 'j2']):
            return "📺 TVB"
        # 境外卫视（星空、Now 变体）
        if any(kw in name_lower for kw in ['星空卫视', '星空台', 'now星空', 'now 星空', '黄金翡翠']):
            return "📡 卫视频道"
        # 电影频道
        if any(kw in name for kw in ['电影', '影院', '影城']):
            return "🎬 电影频道"
        # 音乐频道
        if any(kw in name for kw in ['音乐', 'MTV', 'MV']):
            return "🎵 音乐频道"
        # 台湾频道
        if any(kw in name for kw in ['台視', '台视', '中視', '中视', '民視', '民视', '華視', '华视',
                                       '公視', '公视', '東森', '东森', '三立', '非凡', '大愛', '大爱',
                                       '台灣', '台湾', '原住民']):
            return "🇹🇼 台湾"
        # CGTN 系列 → 国际新闻
        if 'cgtn' in name_lower:
            return "📰 新闻财经"
        # 港澳新闻
        if any(kw in name_lower for kw in ['无线新闻', '有线新闻', 'nownews', 'now新闻']):
            return "📰 新闻财经"
        # 儿童频道
        if any(kw in name for kw in ['少儿', '儿童', '动画', '动漫', '卡通']):
            return "🧸 儿童频道"
        # 纪录片
        if any(kw in name for kw in ['纪录', '探索', '发现', '自然']):
            return "📺 纪录片"
        # 体育
        if any(kw in name for kw in ['体育', '足球', '篮球', '高尔夫', '赛事']):
            return "⚽ 体育频道"
        # 卫视频道（各地方卫视）
        if any(kw in name for kw in ['卫视']):
            return "📡 卫视频道"
        # 综合/综艺
        if any(kw in name for kw in ['综合', '综艺', '娱乐', '戏剧', '电视剧', '人文']):
            return "🎭 综艺频道"
        # 购物/生活
        if any(kw in name for kw in ['购物', '生活', '科教', '教育', '科技', '经济', '文旅', '文体', '公共']):
            return "📺 地方频道"

        # ── 中国省级频道（更精细匹配）──────────────────────────
        province_patterns = [
            ("北京", "📺 北京"), ("北京卫视", "📺 北京"),
            ("上海", "📺 上海"), ("上海卫视", "📺 上海"),
            ("广东", "📺 广东"), ("广州", "📺 广东"),
            ("深圳", "📺 深圳"),
            ("浙江", "📺 浙江"), ("浙江卫视", "📺 浙江"),
            ("江苏", "📺 江苏"), ("江苏卫视", "📺 江苏"),
            ("湖南", "📺 湖南"), ("湖南卫视", "📺 湖南"),
            ("安徽", "📺 安徽"), ("安徽卫视", "📺 安徽"),
            ("山东", "📺 山东"), ("山东卫视", "📺 山东"),
            ("四川", "📺 四川"), ("四川卫视", "📺 四川"),
            ("湖北", "📺 湖北"), ("湖北卫视", "📺 湖北"),
            ("福建", "📺 福建"), ("陕西", "📺 陕西"),
            ("黑龙江", "📺 黑龙江"), ("吉林", "📺 吉林"),
            ("辽宁", "📺 辽宁"), ("河北", "📺 河北"),
            ("河南", "📺 河南"), ("江西", "📺 江西"),
            ("山西", "📺 山西"), ("内蒙古", "📺 内蒙古"),
            ("宁夏", "📺 宁夏"), ("青海", "📺 青海"),
            ("甘肃", "📺 甘肃"), ("新疆", "📺 新疆"),
            ("西藏", "📺 西藏"), ("贵州", "📺 贵州"),
            ("云南", "📺 云南"), ("广西", "📺 广西"),
            ("海南", "📺 海南"), ("重庆", "📺 重庆"),
            ("天津", "📺 天津"),
            # BTV 变体
            ("BTV", "📺 北京"), ("北京台", "📺 北京"),
            ("北京文艺", "📺 北京"), ("北京新闻", "📺 北京"),
        ]
        for keyword, cat in province_patterns:
            if keyword in name:
                return cat

        # 默认中文频道 → 地方频道
        return "📺 地方频道"

    # ══════════════════════════════════════════════════════════
    #  2. 非中文频道 — 按国家/地区分类
    # ══════════════════════════════════════════════════════════
    # 英文新闻关键词
    if any(kw in full_text for kw in [
        'news', 'cnn', 'bbc', 'bloomberg', 'cnbc', 'al jazeera', 'aljazeera',
        'france 24', 'france24', 'dw ', 'trt ', 'rt ', 'euronews',
        'sky news', 'abc news', 'nbc news', 'cbs news',
        'sky news', 'zdf', 'ard', 'rsi', 'rtbf', 'rtve',
        'ansa', 'afp', 'reuters',
        'fox news', 'msnbc',
    ]):
        return "🌐 国际新闻"

    # ── 按频道名识别国家/地区（优先于通用类别）────────────────
    for pattern, region in CHANNEL_REGION_PATTERNS:
        if pattern in name:
            return region

    # 音乐频道
    if any(kw in full_text for kw in [' channel ', 'music', ' pop ', 'hit ', 'radio ']):
        return "🎵 音乐频道"

    # 电影/娱乐
    if any(kw in full_text for kw in ['movie', 'cinema', 'film', 'series', 'drama', 'entertainment']):
        return "🎬 电影频道"

    # 儿童
    if any(kw in full_text for kw in [' kids', 'cartoon', 'disney', 'nick', 'boomerang', 'baby ', 'animation']):
        return "🧸 儿童频道"

    # 体育
    if any(kw in full_text for kw in ['espn', 'sports', 'football', 'soccer', 'basketball', 'nba', 'f1 ', 'racing', 'golf', 'tennis']):
        return "⚽ 体育频道"

    # 纪录片
    if any(kw in full_text for kw in ['discovery', 'national geographic', 'nat geo', 'history', 'documentary', 'science']):
        return "📺 纪录片"

    # ── 国家/地区映射 ──────────────────────────────────────────
    # 日本/韩国
    japan_korea = [
        ('japan', 'japan'), ('japanese', 'japan'),
        ('korea', 'korea'), ('korean', 'korea'),
        ('kbs', 'korea'), ('mbc', 'korea'), ('sbs', 'korea'),
        ('nhk', 'japan'), ('tbs', 'japan'), ('tvtokyo', 'japan'),
        ('tv asahi', 'japan'), ('fuji tv', 'japan'),
    ]

    # 东南亚
    se_asia = [
        ('thailand', 'se_asia'), ('vietnam', 'se_asia'),
        ('indonesia', 'se_asia'), ('malaysia', 'se_asia'),
        ('philippine', 'se_asia'), ('philippin', 'se_asia'),
        ('singapore', 'se_asia'), ('brunei', 'se_asia'),
        ('myanmar', 'se_asia'), ('cambodia', 'se_asia'),
        ('laos', 'se_asia'), ('macao', 'se_asia'),
        ('thai', 'se_asia'), ('viet', 'se_asia'),
        ('channel 3', 'se_asia'),  #泰国
        ('channel 5', 'se_asia'),  #泰国
        ('channel 7', 'se_asia'),  #泰国
        ('pptv', 'se_asia'),       #老挝
    ]

    # 印度次大陆
    india_subcontinent = [
        ('india', 'india'), ('indian', 'india'),
        ('pakistan', 'india'), ('banglades', 'india'),
        ('nepal', 'india'), ('sri lanka', 'india'),
    ]

    # 亚洲其他
    asia_other = [
        ('taiwan', 'asia_other'), ('hong kong', 'asia_other'),
    ]

    # 欧洲
    europe_countries = [
        ('uk', 'europe'), ('britain', 'europe'), ('england', 'europe'),
        ('germany', 'europe'), ('german', 'europe'),
        ('france', 'europe'), ('french', 'europe'),
        ('italy', 'europe'), ('italian', 'europe'),
        ('spain', 'europe'), ('spanish', 'europe'),
        ('portugal', 'europe'), ('portuguese', 'europe'),
        ('russia', 'europe'), ('russian', 'europe'),
        ('poland', 'europe'), ('polish', 'europe'),
        ('dutch', 'europe'), ('netherlands', 'europe'),
        ('belgium', 'europe'), ('sweden', 'europe'),
        ('norway', 'europe'), ('denmark', 'europe'),
        ('finland', 'europe'), ('austria', 'europe'),
        ('switzerland', 'europe'), ('greece', 'europe'),
        ('turkey', 'europe'), ('ukraine', 'europe'),
        ('czech', 'europe'), ('hungary', 'europe'),
        ('romania', 'europe'), ('bulgaria', 'europe'),
        ('serbia', 'europe'), ('croatia', 'europe'),
        ('slovenia', 'europe'), ('slovakia', 'europe'),
        ('latvia', 'europe'), ('estonia', 'europe'),
        ('ireland', 'europe'), ('scotland', 'europe'),
        ('wales', 'europe'), ('albania', 'europe'),
        ('bosnia', 'europe'), ('montenegro', 'europe'),
        ('budapest', 'europe'), ('moscow', 'europe'),
        ('london', 'europe'), ('paris', 'europe'), ('berlin', 'europe'),
        ('madrid', 'europe'), ('rome', 'europe'), ('lisbon', 'europe'),
        ('vienna', 'europe'), ('zurich', 'europe'), ('athens', 'europe'),
        ('warsaw', 'europe'), ('prague', 'europe'),
        ('amsterdam', 'europe'), ('brussels', 'europe'), ('oslo', 'europe'),
        ('stockholm', 'europe'), ('copenhagen', 'europe'), ('helsinki', 'europe'),
        ('geneva', 'europe'),
        # 欧洲电视台
        ('bbc one', 'europe'), ('bbc two', 'europe'), ('bbc world', 'europe'),
        ('bbc news', 'europe'), ('itv ', 'europe'), ('channel 4', 'europe'),
        ('sky one', 'europe'), ('sky news', 'europe'),
        ('zdf', 'europe'), ('ard', 'europe'), ('pro7', 'europe'),
        ('rtl', 'europe'), ('arte', 'europe'),
        ('tv5', 'europe'), ('tv5monde', 'europe'), ('france 2', 'europe'),
        ('france 3', 'europe'), ('france 4', 'europe'), ('france 5', 'europe'),
        ('rai', 'europe'), ('mediaset', 'europe'),
        ('tve', 'europe'), ('telecinco', 'europe'), ('antena 3', 'europe'),
        ('rtve', 'europe'), ('rtp', 'europe'),
        ('rtbf', 'europe'), ('vrt', 'europe'), ('één', 'europe'), ('canvas', 'europe'),
        ('nrk', 'europe'), ('dr tv', 'europe'), ('svt', 'europe'),
        ('YLE', 'europe'), ('YLE TV', 'europe'),
        ('rtvi', 'europe'), ('ntv', 'europe'), ('match tv', 'europe'),
        ('trt', 'europe'), ('trt world', 'europe'), ('trt avaz', 'europe'),
        ('pbc', 'europe'), ('prime', 'europe'),
    ]

    # 北美
    usa_canada = [
        ('usa', 'usa_canada'), ('united states', 'usa_canada'),
        ('canada', 'usa_canada'), ('canadian', 'usa_canada'),
        ('new york', 'usa_canada'), ('los angeles', 'usa_canada'),
        ('chicago', 'usa_canada'), ('miami', 'usa_canada'),
        ('toronto', 'usa_canada'), ('vancouver', 'usa_canada'),
        # 北美电视台
        ('abc ', 'usa_canada'), ('cbs ', 'usa_canada'), ('nbc ', 'usa_canada'),
        ('fox ', 'usa_canada'), ('pbs ', 'usa_canada'),
        ('hbo', 'usa_canada'), ('showtime', 'usa_canada'),
        ('cinemax', 'usa_canada'), ('starz', 'usa_canada'),
        ('cnn ', 'usa_canada'), ('msnbc', 'usa_canada'), ('fox news', 'usa_canada'),
        ('cw ', 'usa_canada'), ('tnt ', 'usa_canada'), ('tbs ', 'usa_canada'),
        ('amc ', 'usa_canada'), ('fx ', 'usa_canada'),
        ('vice', 'usa_canada'), ('voa', 'usa_canada'),
        ('global', 'usa_canada'), ('ctv', 'usa_canada'),
        ('citytv', 'usa_canada'), ('city tv', 'usa_canada'),
        ('cp24', 'usa_canada'), ('citynews', 'usa_canada'),
    ]

    # 拉丁美洲
    latam = [
        ('brazil', 'latam'), ('brazilian', 'latam'), ('brasil', 'latam'),
        ('mexico', 'latam'), ('mexican', 'latam'),
        ('argentina', 'latam'), ('colombia', 'latam'), ('bogota', 'latam'),
        ('peru', 'latam'), ('chile', 'latam'),
        ('venezuela', 'latam'), ('ecuador', 'latam'),
        ('uruguay', 'latam'), ('paraguay', 'latam'),
        ('bolivia', 'latam'), ('panama', 'latam'),
        ('costa rica', 'latam'), ('salvador', 'latam'),
        ('guatemala', 'latam'), ('honduras', 'latam'),
        ('nicaragua', 'latam'), ('cuba', 'latam'),
        ('jamaica', 'latam'), ('trinidad', 'latam'),
        ('buenos aires', 'latam'), ('mexico city', 'latam'),
        ('sao paulo', 'latam'), ('rio de janeiro', 'latam'),
        # 拉美电视台
        ('telemundo', 'latam'), ('uni', 'latam'), ('univision', 'latam'),
        ('tv azteca', 'latam'), ('canal 5', 'latam'), ('canal 13', 'latam'),
        ('globo', 'latam'), ('band', 'latam'), ('record', 'latam'),
        ('sbt', 'latam'), ('tv cultura', 'latam'),
        ('caracol', 'latam'), ('rcn', 'latam'),
        ('atv', 'latam'), ('america tv', 'latam'), ('canal 9', 'latam'),
        ('trece', 'latam'), ('tvn', 'latam'),
    ]

    # 中东
    mideast = [
        ('dubai', 'mideast'), ('uae', 'mideast'), ('qatar', 'mideast'),
        ('saudi', 'mideast'), ('egypt', 'mideast'), ('iran', 'mideast'),
        ('iraq', 'mideast'), ('israel', 'mideast'), ('jordan', 'mideast'),
        ('lebanon', 'mideast'), ('kuwait', 'mideast'), ('oman', 'mideast'),
        ('bahrain', 'mideast'), ('yemen', 'mideast'), ('syria', 'mideast'),
        ('palestin', 'mideast'),
        # 中东电视台
        ('al jazeera', 'mideast'), ('aljazeera', 'mideast'),
        ('al arabiya', 'mideast'), ('al mayadeen', 'mideast'),
        ('sky news arabia', 'mideast'), ('mbc', 'mideast'),
        ('mbc', 'mideast'), ('art', 'mideast'),
    ]

    # 非洲
    africa = [
        ('africa', 'africa'), ('nigeria', 'africa'), ('kenya', 'africa'),
        ('south africa', 'africa'), ('ghana', 'africa'),
        ('ivory coast', 'africa'), ('cameroon', 'africa'),
        ('ethiopia', 'africa'), ('tanzania', 'africa'),
        ('algeria', 'africa'), ('morocco', 'africa'), ('tunisia', 'africa'),
        # 非洲电视台
        ('sabc', 'africa'), ('dstv', 'africa'), ('mnet', 'africa'),
        ('tv5', 'africa'), ('rtga', 'africa'),
        ('nigerian', 'africa'), ('kan', 'africa'),
    ]

    # 大洋洲
    oceania = [
        ('australia', 'oceania'), ('australian', 'oceania'),
        ('new zealand', 'oceania'), ('pacific', 'oceania'),
        ('fiji', 'oceania'), ('png', 'oceania'),
        # 大洋洲电视台
        ('abc', 'oceania'), ('sbs', 'oceania'), ('nine', 'oceania'),
        ('seven', 'oceania'), ('ten', 'oceania'),
        ('sky news', 'oceania'), ('maori tv', 'oceania'),
    ]

    region_map = {
        'japan':      '🇯🇵 日本',
        'korea':      '🇰🇷 韩国',
        'se_asia':    '🌏 亚洲（东南亚）',
        'india':      '🇮🇳 印度',
        'asia_other': '🌏 亚洲（其他）',
        'europe':     '🌍 欧洲',
        'usa_canada': '🇺🇸 北美',
        'latam':      '🌎 拉丁美洲',
        'mideast':    '🌍 中东',
        'africa':     '🌍 非洲',
        'oceania':    '🌏 大洋洲',
    }

    for keyword, region_key in (japan_korea + se_asia + india_subcontinent + asia_other +
                                europe_countries + usa_canada + latam + mideast + africa + oceania):
        if keyword in full_text:
            return region_map[region_key]

    # ── 默认：未能识别的国际频道 ───────────────────────────────
    return "🌐 国际"


# ──────────────────────────────────────────────────────────────
#  categorize — 完全重写
# ──────────────────────────────────────────────────────────────
def categorize(name: str, group: str, logo: str = "") -> str:
    """分类频道，返回分组名称（按新规范）"""

    name_lower, group_lower = name.lower(), (group or "").lower()
    full_text = name_lower + " " + group_lower

    # ── 1. 央视频道 ──────────────────────────────────────────
    if re.search(r"\bcctv[\-_ ]?(\d+|news|english|4k|15|16|17)\b", full_text):
        return "📺 央视频道"
    if re.search(r"\bcetv[\-_ ]?(\d+|1|2|3|4)\b", full_text):
        return "📺 央视频道"
    if "cetv" in full_text or "教育台" in full_text:
        return "📺 央视频道"

    # ── 2. 各省频道 ──────────────────────────────────────────
    for cat, patterns in PROVINCE_KEYWORDS.items():
        if _match(name_lower, group_lower, patterns):
            return cat

    # ── 3. 卫视频道（境外/境外中文） ──────────────────────────
    overseas_satellite = [
        r"凤凰卫视", r"phoenix",
        r"星空卫视", r"star tv", r"startv",
        r"华视",           # 华视 (CTV Taiwan)
        r"法国中文", r"法国电视",
        r"中文电视", r"中文台",
        r"亚洲电视", r"atv",
        r"卫视中文",
    ]
    if _match(name_lower, group_lower, overseas_satellite):
        return "📡 卫视频道"

    # ── 4. 港澳台 ─────────────────────────────────────────────
    # TVB
    tvb_kw = [r"tvb", r"翡翠台", r"明珠台", r"j2", r"j1", r"tvbjade", r"tvbpearl"]
    if _match(name_lower, group_lower, tvb_kw):
        # 排除误匹配
        non_hk = [r"aljadeed", r"al jadeed", r"pearl fm", r"citytv", r"city tv",
                  r"16tv", r"conectv", r"creatv", r"canal30"]
        if _match(name_lower, group_lower, non_hk):
            return recategorize_others(name, group, logo)
        return "📺 TVB"

    # ViuTV
    if _match(name_lower, group_lower, [r"viutv", r"viu tv", r"viu6", r"viu 6"]):
        return "📺 ViuTV"

    # RTHK
    if _match(name_lower, group_lower, [r"rthk", r"rthk tv", r"港台電視", r"香港電台", r"香港电台"]):
        return "📺 RTHK"

    # HOY TV
    if _match(name_lower, group_lower, [r"hoy tv", r"hoytv", r"hoy"]):
        return "📺 HOY TV"

    # Now TV
    if _match(name_lower, group_lower, [r"now tv", r"nowtv", r"now直播", r"now财经", r"nownews"]):
        return "📺 Now TV"

    # 有线电视
    if _match(name_lower, group_lower, [r"有线电视", r"开电视", r"cable tv", r"cable_tv"]):
        return "📺 有线电视"

    # 台湾
    tw_kw = [
        r"tvbs", r"tvbs新闻",
        r"台视", r"台視", r"台视主频", r"台視主頻",
        r"中视", r"中視", r"中视综合台", r"中視綜合台",
        r"民视", r"民視", r"民视无线台", r"民視無限",
        r"东森", r"東森", r"东森新闻", r"東森新聞",
        r"三立台湾", r"三立台灣",
        r"华视", r"華視",
        r"大爱", r"公视", r"公視",
        r"非凡", r"非視",
        r"ttv", r"ftv", r"pts", r"cna",
        r"台湾台", r"台灣台",
    ]
    if _match(name_lower, group_lower, tw_kw):
        return "🇹🇼 台湾"

    # 澳门
    if _match(name_lower, group_lower, [r"澳门", r"澳視", r"macau", r"澳广视", r"澳亚卫视"]):
        return "🇲🇴 澳门"

    # ── 5. 电影频道 ───────────────────────────────────────────
    movie_kw = [
        # 英文电影频道（不用\b，因为中文旁边不算boundary）
        r"hbo", r"cinemax", r"amc", r"paramount", r"mgm",
        r"star movies", r"fox movies",
        r"cinema",                       # cinema 不加\b，避免被 cinemax 意外匹配
        r"电影频道", r"电影台", r"好莱坞电影",
        r"fx movie", r"fxmovie",
        r"好莱坞", r"影视", r"影城",
        r"movie",                        # 英文 movie
        r"凤凰电影", r"卫视电影",
    ]
    if _match(name_lower, group_lower, movie_kw):
        return "🎬 电影频道"

    # ── 6. 音乐频道 ───────────────────────────────────────────
    music_kw = [
        r"channel v", r"channelv",
        r"mtv", r"m tv",
        r"音乐电视", r"音乐频道", r"音乐台",
        r"vmv", r"v mv",
        r"华语音乐", r"中文音乐", r"流行音乐",
    ]
    if _match(name_lower, group_lower, music_kw):
        return "🎵 音乐频道"

    # ── 7. 国际频道 ───────────────────────────────────────────
    intl_kw = [
        r"bbc", r"cnn", r"al jazeera", r"aljazeera",
        r"nhk", r"tbs",
        r"france 24", r"france24",
        r"dw", r"trt", r"tv5", r"tv5monde",
        r"澳大利亚", r"澳洲电视",
        r"德国电视", r"德国之声",
        r"意大利", r"西班牙电视",
        r"韩国频道", r"韩流", r"韩国广播",
        r"日本频道", r"日本电视",
        r"泰国频道", r"越南频道",
        r"印度频道", r"印度新闻",
        r"国际频道", r"海外频道",
    ]
    if _match(name_lower, group_lower, intl_kw):
        return "🌐 国际频道"

    # ── 8. 新闻财经 ──────────────────────────────────────────
    news_kw = [
        r"bloomberg", r"cnbc",
        r"财经", r"金融", r"证券",
        r"新闻频道", r"新闻台",
        r"cnn", r"bbc news",
        r"半岛新闻", r"半岛电视台",
        r"euronews",
        r"香港新闻", r"香港财经",
        r"凤凰财经", r"凤凰新闻",
    ]
    if _match(name_lower, group_lower, news_kw):
        return "📰 新闻财经"

    # ── 9. 儿童频道 ──────────────────────────────────────────
    kids_kw = [
        r"cartoon network", r"cartoon",
        r"disney channel", r"disney",
        r"nickelodeon", r"nick",
        r"少儿频道", r"儿童频道", r"少儿台",
        r"儿童动画", r"动漫频道", r"卡通频道",
        r"baby tv", r"babytv",
        r"boomerang",
        r"儿童电影", r"动画电影",
    ]
    if _match(name_lower, group_lower, kids_kw):
        return "🧸 儿童频道"

    # ── 10. 综艺频道 ──────────────────────────────────────────
    variety_kw = [
        r"综艺", r"综合台", r"综合频道",
        r"娱乐频道", r"娱乐台", r"娱乐节目",
        r"戏剧频道", r"戏剧台",
        r"电视剧", r"电视剧场",
        r"真人秀", r"综艺频道",
        r"曲艺", r"相声",
    ]
    if _match(name_lower, group_lower, variety_kw):
        return "🎭 综艺频道"

    # ── 11. 体育频道 ──────────────────────────────────────────
    sport_kw = [
        r"espn", r"espn2",
        r"fox sports", r"foxsports",
        r"beinsport", r"bein sport",
        r"体育频道", r"体育台",
        r"足球频道", r"足球台",
        r"篮球频道", r"篮球台",
        r"高尔夫", r"网球频道",
        r"赛车", r"搏击", r"格斗",
        r"直播频道", r"直播台",
        r"卫视体育", r"体育新闻",
        r"nba", r"cba",
        r"欧冠", r"英超", r"意甲", r"西甲", r"德甲", r"法甲",
        r"中超", r"亚冠",
        r"奥运", r"体育赛事",
    ]
    if _match(name_lower, group_lower, sport_kw):
        return "⚽ 体育频道"

    # ── 12. 纪录片 ────────────────────────────────────────────
    doc_kw = [
        r"discovery", r"national geographic", r"nat geo",
        r"地理频道", r"探索频道", r"探索",
        r"history channel", r"历史频道",
        r"动物频道", r"野生频道",
        r"science channel", r"科学频道",
        r"documentary", r"纪录片",
    ]
    if _match(name_lower, group_lower, doc_kw):
        return "📺 纪录片"

    # ── 13. 未能分类 → 其他（二次分类）─────────────────────────
    return recategorize_others(name, group, logo)
