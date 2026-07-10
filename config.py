"""
配置文件：所有可调整的参数都放这里
"""
import os
from pathlib import Path
from datetime import date, timedelta

# ─── 目标店铺 ───
BASE_URL = "https://www.manduka.com"

# ─── 搜索关键词（可扩展） ───
KEYWORDS = ["yoga mat", "dumbbell", "resistance band"]

# ─── 数据接口（Shopify 公开 JSON）───
PRODUCTS_API = f"{BASE_URL}/collections/all/products.json"

# ─── 项目根目录 ───
BASE_DIR = Path(__file__).parent  # 当前文件所在目录

# ─── 价格历史 ───
PRICE_HISTORY_FILE = BASE_DIR / "price_history.json"
# 跟几天前的价格比（1 = 跟昨天比）
HISTORY_LOOKBACK_DAYS = 1

# ─── 输出路径 ───
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
