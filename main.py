"""
入口：采集3家竞品 → 价格+评分历史 → Excel → 钉钉推送
"""
import time
from datetime import date, timedelta
from stores import STORES
from config import (
    OUTPUT_FILE, PRICE_HISTORY_FILE, RATING_HISTORY_FILE,
    DISCOVERY_HISTORY_FILE, HISTORY_LOOKBACK_DAYS,
    MAX_RATING_PRODUCTS, RATING_INTERVAL,
)
from crawler import fetch_store_products, extract_products, fetch_rating, count_by_category
from database import init_database, save_store_data
from utils import (
    logger,
    load_price_history, save_price_history,
    load_rating_history, save_rating_history,
    load_discovery_history, save_discovery_history, update_discovery,
    save_competitor_excel,
)
from dingtalk_notify import send_dingtalk_notify


def main():
    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=HISTORY_LOOKBACK_DAYS)).isoformat()

    logger.info("=" * 60)
    logger.info(f"  竞品数据采集  {today_str}")
    logger.info(f"  目标: {', '.join(s['name'] for s in STORES)}")
    logger.info("=" * 60)

    # ─── 初始化数据库 ───
    init_database()

    # ─── 读取历史数据 ───
    price_history = load_price_history(PRICE_HISTORY_FILE)
    rating_history = load_rating_history(RATING_HISTORY_FILE)
    discovery_history = load_discovery_history(DISCOVERY_HISTORY_FILE)

    all_products = []       # 所有店铺的商品汇总
    price_changes = {}      # { "店铺名::商品标题": "涨跌标签" }
    total_count = 0

    # ─── 遍历每家店铺 ───
    for store in STORES:
        name = store["name"]
        url = store["url"]
        logger.info(f"\n{'─'*40}")
        logger.info(f"  🔍 {name} ({url})")
        logger.info(f"{'─'*40}")

        # 1. 拉取商品
        try:
            raw_products = fetch_store_products(url)
        except Exception as e:
            logger.error(f"  ❌ {name} 拉取失败: {e}")
            continue

        if not raw_products:
            logger.warning(f"  ⚠️ {name} 没有商品数据")
            continue

        # 2. 提取字段
        products = extract_products(raw_products, name)
        logger.info(f"  提取 {len(products)} 个商品字段")

        # 3. 品类统计
        count_by_category(raw_products)

        # 4. 爬取评分（前N个商品）
        to_rate = products[:MAX_RATING_PRODUCTS]
        logger.info(f"  爬取评分: {len(to_rate)} 个商品（间隔{RATING_INTERVAL}秒）")
        for i, p in enumerate(to_rate, 1):
            handle = p.get("handle", "")
            if handle:
                rating = fetch_rating(url, handle)
                p["rating"] = rating
                # 更新评分历史
                store_rh = rating_history.setdefault(name, {})
                product_rh = store_rh.setdefault(p["title"], {})
                product_rh[today_str] = rating if rating else ""
                if i < len(to_rate):
                    time.sleep(RATING_INTERVAL)
            if i % 5 == 0:
                logger.info(f"    → {i}/{len(to_rate)}")

        # 5. 价格历史（分店铺）
        store_price_history = price_history.get(name, {})
        today_prices = {}
        for p in products:
            key = p["title"]
            today_prices[key] = p["price"]

            # 计算涨价跌
            yesterday_prices = store_price_history.get(yesterday_str, {})
            if key in yesterday_prices:
                try:
                    old = float(yesterday_prices[key])
                    new = float(p["price"])
                    diff = round(new - old, 2)
                    if diff > 0:
                        price_changes[f"{name}::{key}"] = f"+${diff:.2f} ↑"
                    elif diff < 0:
                        price_changes[f"{name}::{key}"] = f"-${abs(diff):.2f} ↓"
                    else:
                        price_changes[f"{name}::{key}"] = "$0.00 ="
                except ValueError:
                    price_changes[f"{name}::{key}"] = "—"
            else:
                price_changes[f"{name}::{key}"] = "—"

        # 保存今天价格到店铺历史
        store_price_history[today_str] = today_prices
        price_history[name] = store_price_history

        # 6. 存 MySQL
        save_store_data(name, products, date.today())

        # 7. 新品发现
        discovery_history = update_discovery(discovery_history, products, name, today_str)

        # 7. 汇总
        all_products.extend(products)
        total_count += len(products)
        logger.info(f"  ✅ {name} 完成")

    # ─── 保存所有历史 ───
    save_price_history(PRICE_HISTORY_FILE, price_history)
    save_rating_history(RATING_HISTORY_FILE, rating_history)
    save_discovery_history(DISCOVERY_HISTORY_FILE, discovery_history)

    # ─── 输出 Excel ───
    save_competitor_excel(
        all_products=all_products,
        file_path=OUTPUT_FILE,
        rating_history=rating_history,
        discovery_history=discovery_history,
        price_changes=price_changes,
    )

    # ─── 钉钉推送 ───
    logger.info(f"\n  推送钉钉通知...")
    send_dingtalk_notify(
        product_count=total_count,
        keyword_count=len(STORES),
    )

    # ─── 统计摘要 ───
    in_sale = sum(1 for p in all_products if p.get("status") == "在售")
    sold_out = sum(1 for p in all_products if p.get("status") == "售罄")
    has_rating = sum(1 for p in all_products if p.get("rating"))

    logger.info(f"\n{'='*60}")
    logger.info(f"  ✅ 采集完成！")
    logger.info(f"  共 {total_count} 个商品（{len(STORES)}家店铺）")
    logger.info(f"  在售: {in_sale} | 售罄: {sold_out}")
    logger.info(f"  有评分: {has_rating} 个")
    logger.info(f"  📁 {OUTPUT_FILE}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
