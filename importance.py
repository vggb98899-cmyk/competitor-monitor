"""商品重要程度判断"""
import re

# 高价值关键词（表示这个商品是品牌的主推款）
HIGH_VALUE_KEYWORDS = [
    "pro", "ultralight", "gtx", "gore-tex", "waterproof", "down", 
    "dwr", "new", "limited", "collection", "signature",
    "expedition", "alpine", "summit", "professional",
]

# 低价值关键词（配件/小件）
LOW_VALUE_KEYWORDS = [
    "strap", "bag", "cover", "case", "sack", "stake", "peg",
    "kit", "repair", "patch", "brush", "cleaner",
]


def judge_importance(title: str, price: float) -> str:
    """
    判断商品重要程度

    Returns:
        "🔥 重要" / "📌 常规" / "⚪ 普通"
    """
    title_lower = title.lower()

    # 价格高的商品更重要
    if price >= 100:
        return "🔥 重要"

    # 命中高价值关键词
    for kw in HIGH_VALUE_KEYWORDS:
        if kw in title_lower:
            return "🔥 重要"

    # 命中低价值关键词
    for kw in LOW_VALUE_KEYWORDS:
        if kw in title_lower:
            return "⚪ 普通"

    # 50-100美元的看品类
    if price >= 50:
        return "📌 常规"

    return "⚪ 普通"
