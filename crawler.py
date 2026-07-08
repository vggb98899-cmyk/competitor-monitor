"""
爬虫模块：从 Shopify JSON 接口获取商品数据
"""
import requests
from config import PRODUCTS_API, HEADERS, TIMEOUT, SEARCH_KEYWORD
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


def filter_by_keyword(products: list[dict], keyword: str) -> list[dict]:
    """
    按关键词过滤商品（标题中是否包含关键词，不区分大小写）

    Args:
        products: 原始商品列表
        keyword: 搜索关键词

    Returns:
        过滤后的商品列表
    """
    keyword_lower = keyword.lower()
    matched = []
    for p in products:
        title = p.get("title", "")
        if keyword_lower in title.lower():
            matched.append(p)
    logger.info(f"关键词 '{keyword}' 匹配到 {len(matched)} 个商品")
    return matched


def extract_fields(products: list[dict]) -> list[dict]:
    """
    从原始商品数据中提取需要的字段

    Args:
        products: 原始商品列表

    Returns:
        精简后的列表，每项含 title / price / sales
    """
    results = []
    for p in products:
        # 取第一个变体的价格作为商品价格
        variants = p.get("variants", [])
        price = variants[0].get("price", "") if variants else ""

        results.append({
            "title": p.get("title", ""),
            "price": price,
            # Shopify 原生数据不含月销量，留空
            "sales": "",
        })

    logger.info(f"提取了 {len(results)} 条商品数据")
    return results
