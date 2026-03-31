#!/usr/bin/env python3
"""Channel categorization and grouping logic."""
import re
from typing import Dict, List


def is_hk_region(name: str, group: str) -> bool:
    """判断是否为港台地区频道 (HK/TW/MO)
    
    使用精确匹配避免误匹配，如 "16tv Budapest" 不会匹配 TVB
    """
    name_lower, group_lower = name.lower(), (group or "").lower()
    full_text = name_lower + " " + group_lower
    
    # HK 精确匹配
    hk_exact = [
        r"hkdtmb", r"香港台", r"香港電視",
        r"tvb",
        r"翡翠台", r"明珠台",
        r"j2", r"j1",
        r"viutv", r"viu tv", r"viu6", r"viu 6",
        r"rthk", r"rthk tv", r"港台電視", r"港台电视", r"香港电台",
        r"hoy tv", r"hoytv",
        r"now tv", r"nowtv", r"now直播", r"now财经", r"nownews",
        r"有线电视", "开电视", "cable tv", r"cable_tv",
        r"凤凰卫视", r"phoenix tv",
        r"无线电视", r"无线新闻", r"星空卫视",
    ]
    # TW 精确匹配
    tw_exact = [
        r"tvbs", r"tvbs新闻",
        r"台视主频", r"台視主頻",
        r"中视综合台", r"中視綜合台",
        r"民视无线台", r"民視無限",
        r"东森电视", r"東森電視", r"东森新闻", r"東森新聞",
        r"三立台湾台", r"三立台灣台",
        r"华视", r"華視", r"中视", r"中視", r"民视", r"民視",
        r"台视", r"台視", r"大爱", r"公视", r"公視",
        r"\\bttv\\b", r"\\bftv\\b", r"\\bpts\\b",
        r"\\bcna\\b",
    ]
    # MO 精确匹配
    mo_exact = [r"澳门", r"澳視", "\\bmacau\\b", r"澳广视", r"澳亚卫视"]
    
    # 排除项
    exclude = [
        "\\bcctv\\b", "\\bcetv\\b",
        "\\bbbc\\b", "\\bcnn\\b",
        "\\bal jazeera\\b", "\\bfrance 24\\b",
        r"16tv", "\\b16 tv\\b",
        r"african", r"africable",
        r"budapest",
        r"bogota", r"brasil", r"brazil",
        "\\bktv\\b",
        "\\bmtv\\b", "\\bm tv\\b",
        r"star tv", r"startv",
        r"daystar",
        r"café", r"cafe",
    ]
    
    for p in exclude:
        if re.search(p, full_text):
            return False
    
    for p in hk_exact + tw_exact + mo_exact:
        if re.search(p, full_text):
            return True
    
    return False


def categorize(name: str, group: str) -> str:
    """分类频道，返回分组名称"""
    name_lower, group_lower = name.lower(), (group or "").lower()
    full_text = name_lower + " " + group_lower
    
    # TVB 系列 - 只匹配真正的TVB频道
    tvb_patterns = ['tvb', '翡翠台', '明珠台', 'j2']
    if any(kw in full_text for kw in tvb_patterns):
        # 排除非HK频道 - 这些也包含 jade/tv 但不是TVB
        non_hk_patterns = [
            'aljadeed', 'al jadeed',  # 黎巴嫩
            'pearl fm', 'pearl',      # 广播电台
            'citytv', 'city tv',       # 哥伦比亚
            '16tv', '16 tv',          # 布达佩斯
            'conectv',                 # 巴西
            'creatv', 'crea tv',      # Bay Voice TV
            'canal30', 'canal 30',    # Bethel TV
        ]
        for p in non_hk_patterns:
            if p in full_text:
                return "🌐 其他"  # 不匹配TVB
        return "📺 TVB"
    if any(kw in full_text for kw in ['viutv', 'viu tv', 'viu6']):
        return "📺 ViuTV"
    if any(kw in full_text for kw in ['rthk', 'rthk tv', '港台電視', '港台電台', '香港电台', '香港電台']):
        return "📺 RTHK"
    if any(kw in full_text for kw in ['hoy', 'hooy', 'hoytv']):
        return "📺 HOY TV"
    if any(kw in full_text for kw in ['now tv', 'nowtv', 'now news', 'now直播', 'now财经']):
        return "📺 Now TV"
    if any(kw in full_text for kw in ['cable', '有线', '开电视', 'cable TV']):
        return "📺 有线电视"
    if any(kw in full_text for kw in ['凤凰', 'phoenix']):
        return "📺 凤凰卫视"
    # 台湾必须放在香港其他之前
    if any(kw in full_text for kw in ['tvbs', '台视', '中视', '华视', '民视', '东森', '三立', '非凡', '大爱', '公视', '華視', '中視', '民視', '台視', '公視']):
        return "🇹🇼 台湾"
    if any(kw in full_text for kw in ['澳门', '澳視', 'macau', '澳广视']):
        return "🇲🇴 澳门"
    if any(kw in full_text for kw in ['无线', '星空', 'star tv']):
        return "📺 香港其他"
    if any(kw in full_text for kw in ['news', '新闻', 'cnn', 'bbc', 'dw', '半岛']):
        return "📰 新闻"
    if any(kw in full_text for kw in ['movie', '电影', 'cinema', 'hbo', 'cinemax', '影城', '卫视电影']):
        return "🎬 电影"
    if any(kw in full_text for kw in ['sport', 'sports', '体育', 'espn', '足球', '篮球', 'fox sports', 'beinsport']):
        return "⚽ 体育"
    if any(kw in full_text for kw in ['kids', 'children', '卡通', '动画', 'anime', 'nick', '迪士尼', 'disney', 'baby']):
        return "🧸 儿童"
    if any(kw in full_text for kw in ['entertainment', '娱乐', '综艺', 'variety', '综合台', '戏剧']):
        return "🎭 综艺"
    if any(kw in full_text for kw in ['discovery', 'national geographic', '地理', '探索', 'history', 'hist', '动物']):
        return "📺 纪录片"
    if any(kw in full_text for kw in ['music', '音乐', 'mv', 'channel v', 'mtv', 'vod']):
        return "🎵 音乐"
    # 对原始 group 进行规范化
    if group and group.strip():
        normalized_group = group.strip()
        # 规范化分组名
        group_mapping = {
            "Animation": "动漫",
            "Auto": "汽车",
            "Business": "商业",
            "Classic": "经典",
            "Comedy": "喜剧",
            "Culture": "文化",
            "Documentary": "纪录片",
            "Education": "教育",
            "Family": "家庭",
            "Food": "美食",
            "General": "综合",
            "Health": "健康",
            "History": "历史",
            "Hobby": "爱好",
            "Home": "家居",
            "Kids": "儿童",
            "Legislative": "立法",
            "Lifestyle": "生活方式",
            "Movies": "电影",
            "Music": "音乐",
            "News": "新闻",
            "Outdoor": "户外",
            "Public": "公共",
            "Religious": "宗教",
            "Science": "科学",
            "Series": "剧集",
            "Shop": "购物",
            "Sports": "体育",
            "Travel": "旅游",
            "Weather": "天气",
            "Animation;Series": "动漫",
            "Auto;Series": "汽车",
            "Business;Culture": "商业",
            "Business;Documentary": "商业",
            "Business;Series": "商业",
            "Classic;Comedy;Public;Series": "经典",
            "Comedy;Public": "喜剧",
            "Comedy;Series": "喜剧",
            "Culture;Documentary": "文化",
            "Culture;Education": "文化",
            "Culture;General": "文化",
            "Culture;Public": "文化",
            "Education;General": "教育",
            "Education;Outdoor": "教育",
            "Family;General": "家庭",
            "General;Legislative": "综合",
            "General;Public": "综合",
            "General;Religious": "综合",
            "Lifestyle;Relax": "生活方式",
            "Public;Weather": "公共",
            "Cooking": "美食",
            "Relax": "休闲",
        }
        
        if normalized_group in group_mapping:
            return "📺 " + group_mapping[normalized_group]
        elif "Hong Kong" in normalized_group or "hk" in normalized_group.lower():
            return "📺 香港其他"
        elif "Taiwan" in normalized_group or "tw" in normalized_group.lower():
            return "🇹🇼 台湾"
        elif "Macau" in normalized_group or "mo" in normalized_group.lower():
            return "🇲🇴 澳门"
        elif ";" in normalized_group:
            # 多类别分组只取第一个
            first_cat = normalized_group.split(";")[0].strip()
            if first_cat in group_mapping:
                return "📺 " + group_mapping[first_cat]
            return "📺 " + first_cat
        else:
            return "📺 " + normalized_group
    return "🌐 其他"
