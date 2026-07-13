"""
探测模块：对单个店铺执行接口探测 + 页面HTML探测

三个探测函数：
  1. probe_json_api(url)       → 检查 products.json 是否可访问
  2. probe_product_page(url)   → 检查商品详情页是否有销量文本和评分
  3. probe_store(url)          → 整合以上两个，输出完整探测结果
"""
import re
import time
import requests
from utils import logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# 销量关键词（在HTML中搜索这些词）
SALES_KEYWORDS = [
    "sold", "purchased", "bought", "sales", "sold in last",
    "sold last month", "monthly sales", "total sales",
]

# 评分关键词（在HTML中搜索）
RATING_KEYWORDS = [
    "aggregateRating", "ratingValue", "reviewCount",
    "star-rating", "star_rating", "rating-number",
    "average rating",
]


def probe_json_api(url: str) -> dict:
    """
    探测 /products.json 接口

    检查三项：
      1. 接口是否能访问
      2. 是否返回了商品数据
      3. 返回的数据里是否有月销量字段

    Args:
        url: 店铺首页URL（如 https://www.manduka.com）

    Returns:
        {
            "api_accessible": True/False,       # 接口是否可访问
            "product_count": 数字,               # 商品数量（0表示没拿到）
            "has_sales_field": True/False,       # JSON里是否有月销量字段
            "sales_field_name": "字段名"或"",     # 具体的月销量字段名
            "error": "报错信息"或"",              # 如果有错误
        }
    """
    api_url = f"{url.rstrip('/')}/collections/all/products.json?limit=1"

    result = {
        "api_accessible": False,
        "product_count": 0,
        "has_sales_field": False,
        "sales_field_name": "",
        "error": "",
    }

    try:
        resp = requests.get(api_url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            result["error"] = f"HTTP {resp.status_code}"
            return result

        data = resp.json()
        products = data.get("products", [])
        result["api_accessible"] = True
        result["product_count"] = len(products)

        # 检查是否有月销量字段
        if products:
            product = products[0]
            result["has_sales_field"], result["sales_field_name"] = (
                _check_sales_field(product)
            )

    except requests.Timeout:
        result["error"] = "请求超时"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"

    return result


def _check_sales_field(product: dict) -> tuple:
    """
    检查一个商品数据里是否有月销量字段

    搜索范围：
      - product 顶层字段
      - variants[0] 的字段

    Returns:
        (has_field: bool, field_name: str)
    """
    # 检查product顶层字段
    for key in product.keys():
        key_lower = key.lower()
        if any(word in key_lower for word in ["sold", "sales", "popular", "purchased", "bought"]):
            return True, key

    # 检查variants
    variants = product.get("variants", [])
    if variants:
        for key in variants[0].keys():
            key_lower = key.lower()
            if any(word in key_lower for word in ["sold", "sales", "popular", "purchased", "bought"]):
                return True, key

    return False, ""


def probe_product_page(url: str, handle: str) -> dict:
    """
    探测商品详情页HTML

    检查两项：
      1. 页面是否显示销量文本（如 "X sold"）
      2. 页面是否有评分信息

    Args:
        url: 店铺首页URL
        handle: 商品handle（从products.json取第一个）

    Returns:
        {
            "page_accessible": True/False,   # 页面能否打开
            "has_sales_text": True/False,    # 页面是否有销量文本
            "sales_text": "找到的文本"或"",    # 具体的销量文本
            "has_rating": True/False,        # 是否有评分
            "rating_text": "找到的文本"或"",   # 具体的评分信息
            "error": "报错信息"或"",
        }
    """
    page_url = f"{url.rstrip('/')}/products/{handle}"

    result = {
        "page_accessible": False,
        "has_sales_text": False,
        "sales_text": "",
        "has_rating": False,
        "rating_text": "",
        "error": "",
    }

    try:
        resp = requests.get(
            page_url,
            headers={
                "User-Agent": HEADERS["User-Agent"],
                "Accept": "text/html",
            },
            timeout=15,
        )
        if resp.status_code != 200:
            result["error"] = f"HTTP {resp.status_code}"
            return result

        result["page_accessible"] = True
        html = resp.text

        # 搜索销量文本
        sales_found = _search_html(html, SALES_KEYWORDS)
        if sales_found:
            result["has_sales_text"] = True
            result["sales_text"] = sales_found[:100]  # 截取前100字符

        # 搜索评分信息
        rating_found = _search_html(html, RATING_KEYWORDS)
        if rating_found:
            result["has_rating"] = True
            result["rating_text"] = rating_found[:100]

    except requests.Timeout:
        result["error"] = "请求超时"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"

    return result


def _search_html(html: str, keywords: list) -> str:
    """
    在HTML中搜索关键词，返回匹配的上下文文本

    Args:
        html: 页面HTML源码
        keywords: 要搜索的关键词列表

    Returns:
        找到的上下文文本，没找到返回空字符串
    """
    for keyword in keywords:
        # 找到关键词在HTML中的位置
        idx = html.lower().find(keyword.lower())
        if idx != -1:
            # 取关键词前后一段文本（共200字符）
            start = max(0, idx - 50)
            end = min(len(html), idx + 150)
            context = html[start:end]
            # 清理HTML标签，保留可读文本
            clean = re.sub(r'<[^>]+>', ' ', context)
            clean = re.sub(r'\s+', ' ', clean).strip()
            return f"[{keyword}] {clean}"
    return ""


def judge_data_level(probe_result: dict) -> str:
    """
    根据探测结果判断数据等级

    A类：有月销量 → 可直接计算销售额
    B类：无月销量，有评分 → 评分替代，销售额标"估算值"
    C类：都无 → 只采集基础字段

    Args:
        probe_result: probe_store() 返回的完整探测结果

    Returns:
        "A" / "B" / "C"
    """
    api = probe_result.get("api", {})
    page = probe_result.get("page", {})

    has_sales = api.get("has_sales_field") or page.get("has_sales_text")
    has_rating = page.get("has_rating")

    if has_sales:
        return "A"
    elif has_rating:
        return "B"
    else:
        return "C"


def probe_store(url: str, name: str = "") -> dict:
    """
    对单个店铺执行完整探测

    流程：
      1. 探测JSON接口
      2. 如果接口可用，取第一个商品的handle
      3. 探测商品详情页HTML
      4. 判断数据等级

    Args:
        url: 店铺URL
        name: 店铺名称（仅用于日志）

    Returns:
        {
            "name": 店铺名,
            "url": 店铺URL,
            "api": { 接口探测结果 },
            "page": { 页面探测结果 },
            "data_level": "A/B/C",
        }
    """
    label = name or url
    logger.info(f"🔍 正在探测: {label}")

    result = {
        "name": name,
        "url": url,
    }

    # 1. 探测接口
    api_result = probe_json_api(url)
    result["api"] = api_result
    logger.info(f"  接口: {'✅' if api_result['api_accessible'] else '❌'} "
                f"商品数={api_result['product_count']} "
                f"月销量字段={api_result['has_sales_field']}")

    # 2. 如果接口可用，探测商品详情页
    if api_result["api_accessible"] and api_result["product_count"] > 0:
        # 从接口拿到第一个商品的handle
        try:
            api_url = f"{url.rstrip('/')}/collections/all/products.json?limit=1"
            resp = requests.get(api_url, headers=HEADERS, timeout=15)
            products = resp.json().get("products", [])
            if products:
                handle = products[0].get("handle", "")
                if handle:
                    time.sleep(2)  # 间隔2秒，避免限流
                    page_result = probe_product_page(url, handle)
                    result["page"] = page_result
                    logger.info(f"  页面: {'✅' if page_result['page_accessible'] else '❌'} "
                                f"销量文本={'✅' if page_result['has_sales_text'] else '❌'} "
                                f"评分={'✅' if page_result['has_rating'] else '❌'}")
                else:
                    result["page"] = {"page_accessible": False, "error": "无handle"}
            else:
                result["page"] = {"page_accessible": False, "error": "无商品数据"}
        except Exception as e:
            result["page"] = {"page_accessible": False, "error": f"{type(e).__name__}: {e}"}
    else:
        result["page"] = {"page_accessible": False, "error": "接口不可用，跳过页面探测"}

    # 3. 判断数据等级
    result["data_level"] = judge_data_level(result)

    level_label = {"A": "✅ A类(有销量)", "B": "🟡 B类(有评分)", "C": "⚪ C类(基础)"}
    logger.info(f"  等级: {level_label.get(result['data_level'], '未知')}")

    return result
