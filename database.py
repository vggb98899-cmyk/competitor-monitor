"""
数据库模块：MySQL建表 + 数据存储
"""
import mysql.connector
from datetime import date
from utils import logger

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "competitor_db",
}


def get_connection():
    """获取MySQL连接"""
    return mysql.connector.connect(**DB_CONFIG)


def init_database():
    """
    初始化数据库和表

    两张表：
      products  → 商品主信息（每个商品只存一条）
      snapshots → 快照记录（每天一条，存价格/评分/状态变化）
    """
    # 先连MySQL（不指定数据库），创建数据库
    config = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` "
                   f"DEFAULT CHARACTER SET utf8mb4")
    cursor.close()
    conn.close()

    # 连到指定数据库，建表
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            store VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            handle VARCHAR(255) DEFAULT '',
            category VARCHAR(100) DEFAULT '',
            url VARCHAR(500) DEFAULT '',
            first_seen DATE NOT NULL,
            last_seen DATE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE KEY uk_store_title (store, title)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            price DECIMAL(10,2),
            rating DECIMAL(3,2),
            status VARCHAR(20) DEFAULT '',
            captured_at DATE NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id),
            UNIQUE KEY uk_product_date (product_id, captured_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("✅ 数据库初始化完成（products + snapshots）")


def save_store_data(store_name: str, products: list[dict], capture_date: date):
    """
    批量保存一家店铺的商品数据

    逻辑：
      - 商品不存在 → 插入新商品，记录first_seen
      - 商品已存在 → 更新last_seen
      - 每天插入一条snapshot记录（价格/评分/状态）

    Args:
        store_name: 店铺名
        products: 商品列表，每项含 title/handle/category/price/rating/status
        capture_date: 采集日期
    """
    conn = get_connection()
    cursor = conn.cursor()

    saved = 0
    for p in products:
        title = p.get("title", "")
        if not title:
            continue

        handle = p.get("handle", "")
        category = p.get("category", "")
        price = p.get("price", "")
        rating = p.get("rating", "")
        status = p.get("status", "")

        # 插入或更新商品
        cursor.execute("""
            INSERT INTO products (store, title, handle, category, first_seen, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE last_seen = %s, handle = %s, category = %s
        """, (store_name, title, handle, category, capture_date, capture_date,
              capture_date, handle, category))

        # 获取商品ID
        cursor.execute("SELECT id FROM products WHERE store = %s AND title = %s",
                       (store_name, title))
        row = cursor.fetchone()
        if not row:
            continue
        product_id = row[0]

        # 插入快照（价格/评分/状态）
        price_val = None
        try:
            price_val = float(price) if price else None
        except ValueError:
            pass

        rating_val = None
        try:
            rating_val = float(rating) if rating else None
        except ValueError:
            pass

        cursor.execute("""
            INSERT INTO snapshots (product_id, price, rating, status, captured_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE price = %s, rating = %s, status = %s
        """, (product_id, price_val, rating_val, status, capture_date,
              price_val, rating_val, status))

        saved += 1

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"  💾 MySQL: {store_name} 保存 {saved}/{len(products)} 条")


def get_product_count() -> dict:
    """查询各店铺的商品数量"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT store, COUNT(*) FROM products
        WHERE is_active = TRUE
        GROUP BY store ORDER BY store
    """)
    result = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return result
