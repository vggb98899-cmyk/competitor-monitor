"""
爬虫模块：从 Shopify JSON 接口获取商品数据
"""
import requests
from config import PRODUCTS_API, PRODUCTS_API_FULL, HEADERS, TIMEOUT, KEYWORDS
from utils import logger


def fetch_all_products() -> list[dict]:
    """
    从 Shopify /products.json 拉取所有商品

    Returns:
        原始商品字典列表（含所有字段）

    Raises:
        requests.RequestException: 网络请求失败时抛出
    """
    logger.info(f"正在请求商品数据: {PRODUCTS_API}")
    resp = requests.get(PRODUCTS_API, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()  # 状态码不是200就抛异常

    data = resp.json()
    products = data.get("products", [])
    logger.info(f"拉取到 {len(products)} 个商品")
    return products


def filter_by_keywords(products: list[dict]) -> list[dict]:
    """
    按多个关键词过滤，每个商品标记所属品类，自动去重

    Returns:
        带品类标记的精简列表，每项含 title / price / sales / category
    """
    seen_handles = set()
    all_results = []

    for keyword in KEYWORDS:
        keyword_lower = keyword.lower()
        matched_count = 0

        for p in products:
            handle = p.get("handle", "")
            title = p.get("title", "")

            # 跳过已匹配的商品（去重）
            if handle in seen_handles:
                continue

            # 标题包含关键词则匹配
            if keyword_lower in title.lower():
                # 提取价格
                variants = p.get("variants", [])
                price = variants[0].get("price", "") if variants else ""

                all_results.append({
                    "title": title,
                    "price": price,
                    "sales": "",
                    "category": keyword,
                })
                seen_handles.add(handle)
                matched_count += 1

        logger.info(f"关键词 '{keyword}' → 匹配 {matched_count} 个商品")

    logger.info(f"共计 {len(all_results)} 条商品（已去重）")
    return all_results


def fetch_all_products_full() -> list[dict]:
    """
    拉取全量商品（limit=250，确保全部拿到）

    Returns:
        原始商品字典列表
    """
    logger.info(f"正在拉取全量数据: {PRODUCTS_API_FULL}")
    resp = requests.get(PRODUCTS_API_FULL, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    products = resp.json().get("products", [])
    logger.info(f"全量拉取到 {len(products)} 个商品")
    return products


def count_by_category(products: list[dict]) -> list[dict]:
    """
    按品类统计商品数量，按数量降序排列

    Returns:
        排行列表，每项含 category / count，例如 [{"category": "Mats", "count": 28}, ...]
    """
    category_map = {}
    for p in products:
        pt = p.get("product_type", "未分类") or "未分类"
        category_map[pt] = category_map.get(pt, 0) + 1

    sorted_cats = sorted(category_map.items(), key=lambda x: -x[1])
    result = [{"category": k, "count": v} for k, v in sorted_cats]

    logger.info(f"品类统计完成，共 {len(result)} 个品类")
    for item in result:
        logger.info(f"  {item['category']}: {item['count']} 个")
    return result
