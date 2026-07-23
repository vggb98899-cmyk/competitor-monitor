"""
配置文件示例 —— 使用前请重命名为 config.py 并填入真实值
"""
from pathlib import Path
from datetime import date, timedelta

BASE_DIR = Path(__file__).parent

# 数据接口
PRODUCTS_API_FULL = "https://你的店铺.com/collections/all/products.json?limit=250"

# MySQL 数据库
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "你的密码",
    "database": "competitor_db",
}

# 飞书推送
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/你的hook地址"

# DeepSeek AI
DEEPSEEK_API_KEY = "sk-你的key"
DEEPSEEK_MODEL = "deepseek-chat"

# 价格对比天数
HISTORY_LOOKBACK_DAYS = 1
# 评分采集数量
MAX_RATING_PRODUCTS = 10
# 请求间隔（秒）
RATING_INTERVAL = 1
