"""
配置文件：所有可调整的参数都放这里
"""
import os
from pathlib import Path

# ─── 目标店铺 ───
BASE_URL = "https://www.manduka.com"
SEARCH_KEYWORD = "yoga mat"

# ─── 数据接口（Shopify 公开 JSON）───
PRODUCTS_API = f"{BASE_URL}/collections/all/products.json"

# ─── 输出路径 ───
BASE_DIR = Path(__file__).parent  # 当前文件所在目录
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "manduka_products.xlsx"

# ─── 请求头（伪装成普通浏览器） ───
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# ─── 请求超时（秒） ───
TIMEOUT = 30
