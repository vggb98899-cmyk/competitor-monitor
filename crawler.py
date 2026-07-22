"""
爬虫模块：从 Shopify JSON 接口获取商品 + 从页面提取评分
"""
import re
from curl_cffi import requests
from utils import logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html",
}


def fetch_store_products(store_url: str) -> list[dict]:
    """
    拉取某家店铺的全部商品（/products.json?limit=250）

    Args:
        store_url: 店铺首页URL

    Returns:
        原始商品字典列表
    """
    api_url = f"{store_url.rstrip('/')}/collections/all/products.json?limit=250"
    logger.info(f"  正在请求: {api_url}")

    resp = requests.get(api_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    products = resp.json().get("products", [])
    logger.info(f"  → 拉取到 {len(products)} 个商品")
    return products


def check_status(variants: list) -> str:
    """
    判断单个商品的状态

    Args:
        variants: 商品变体列表

    Returns:
        "在售" / "售罄"
    """
    for v in variants:
        if v.get("available") is True:
            return "在售"
    return "售罄"


def fetch_rating(store_url: str, handle: str) -> str:
    """
    从商品详情页提取评分

    两种方式：
      1. 搜索 JSON-LD 结构化数据中的 "ratingValue"
      2. 搜索页面上评分元素附近的数字

    Args:
        store_url: 店铺首页URL
        handle: 商品handle

    Returns:
        评分数值字符串（如 "4.5"），没找到返回空字符串
    """
    page_url = f"{store_url.rstrip('/')}/products/{handle}"

    try:
        resp = requests.get(page_url, headers=HTML_HEADERS, timeout=15)
        if resp.status_code != 200:
            return ""

        html = resp.text

        # 方法1：搜 JSON-LD 结构化数据
        # 格式: "ratingValue": "4.5"
        match = re.search(r'"ratingValue"\s*:\s*"([\d.]+)"', html)
        if match:
            return match.group(1)

        # 方法2：搜 "ratingValue": 4.5（不带引号的值）
        match = re.search(r'"ratingValue"\s*:\s*([\d.]+)', html)
        if match:
            return match.group(1)

        # 方法3：搜 "averageRating": 4.5
        match = re.search(r'"averageRating"\s*:\s*([\d.]+)', html)
        if match:
            return match.group(1)

        # 方法4：搜页面文本 "X 条评价" 或 "X reviews" 前面的评分
        # 比如 "4.5 · 94 reviews"
        rating_patterns = [
            r'([\d.]+)\s*[★☆⭐]',
            r'([\d.]+)\s*out of\s*5',
            r'([\d.]+)\s*/\s*5',
        ]
        for pattern in rating_patterns:
            match = re.search(pattern, html)
            if match:
                val = float(match.group(1))
                if 0 <= val <= 5:
                    return str(val)

        return ""

    except Exception as e:
        err_name = type(e).__name__
        if 'Timeout' in err_name or 'timeout' in str(e).lower():
            logger.warning(f"  评分请求超时: {page_url[:60]}")
        else:
            logger.warning(f"  评分提取失败: {e}")
        return ""
        logger.warning(f"  评分提取失败: {e}")
        return ""


# 品类映射：当商品product_type为空时，根据标题关键词判断
CATEGORY_KEYWORDS = [
    ("Tent", ["tent", "shelter", "tarp", "canopy", "awning", "帐篷"]),
    ("Sleeping Bag", ["sleeping bag", "睡袋"]),
    ("Sleeping Pad", ["sleeping pad", "sleep pad", "mattress", "camp bed", "cot"]),
    ("Backpack", ["backpack", "pack", "rucksack", "背包"]),
    ("Chair", ["chair", "stool", "seat", "椅子"]),
    ("Table", ["table", "desk", "桌子"]),
    ("Cookware", ["pot", "pan", "cookware", "stove", "burner", "kettle", "mess kit", "餐具", "锅"]),
    ("Water Bottle", ["water bottle", "bottle", "hydration", "水壶", "水杯"]),
    ("Lighting", ["light", "lamp", "lantern", "headlamp", "灯"]),
    ("Apparel", ["jacket", "pants", "shirt", "hoodie", "gloves", "hat", "socks", "衣服", "服装"]),
    ("Pillow", ["pillow", "枕头"]),
    ("Trekking Pole", ["pole", "stick", "trekking", "登山杖"]),
    ("Bag", ["bag", "dry bag", "防水袋", "收纳"]),
    ("Accessories", ["accessory", "strap", "hook", "stake", "peg", "配件"]),
]


def map_category(title: str, product_type: str) -> str:
    """如果product_type是未分类，用标题关键词匹配品类"""
    if product_type and product_type != "未分类":
        return product_type
    title_lower = title.lower()
    for cat, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in title_lower:
                return cat
    return "未分类"


def extract_products(products: list[dict], store_name: str) -> list[dict]:
    """
    从原始商品数据中提取需要的字段

    Args:
        products: 原始商品列表
        store_name: 店铺名称

    Returns:
        精简列表，每项含 title / price / category / status / store
    """
    results = []
    for p in products:
        variants = p.get("variants", [])
        price = variants[0].get("price", "") if variants else ""
        status = check_status(variants)
        raw_type = p.get("product_type", "未分类") or "未分类"
        category = map_category(p.get("title", ""), raw_type)

        results.append({
            "title": p.get("title", ""),
            "price": price,
            "category": category,
            "status": status,
            "store": store_name,
            "handle": p.get("handle", ""),
        })

    return results


def count_by_category(products: list[dict]) -> list[dict]:
    """
    按品类统计商品数量，按数量降序排列

    Returns:
        排行列表，每项含 category / count
    """
    category_map = {}
    for p in products:
        pt = p.get("product_type", "未分类") or "未分类"
        category_map[pt] = category_map.get(pt, 0) + 1

    sorted_cats = sorted(category_map.items(), key=lambda x: -x[1])
    result = [{"category": k, "count": v} for k, v in sorted_cats]

    logger.info(f"  品类统计: 共 {len(result)} 个品类")
    for item in result:
        logger.info(f"    {item['category']}: {item['count']} 个")
    return result
