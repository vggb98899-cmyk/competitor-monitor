"""
入口：采集竞品 → 价格+评分历史 → MySQL → Excel → 钉钉推送
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
from database import init_database, save_store_data, save_run_log
from ebay_crawler import crawl_ebay
from alert import check_alerts
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

    all_products = []
    price_changes = {}
    total_count = 0
    stores_ok = 0
    stores_fail = 0

    for store in STORES:
        name = store["name"]
        url = store["url"]
        logger.info(f"\n{'─'*40}")
        logger.info(f"  🔍 {name} ({url})")
        logger.info(f"{'─'*40}")

        try:
            raw_products = fetch_store_products(url)
        except Exception as e:
            logger.error(f"  ❌ {name} 拉取失败: {e}")
            stores_fail += 1
            continue

        if not raw_products:
            stores_fail += 1
            continue

        products = extract_products(raw_products, name)
        logger.info(f"  提取 {len(products)} 个商品字段")
        count_by_category(raw_products)

        # 爬评分
        to_rate = products[:MAX_RATING_PRODUCTS]
        logger.info(f"  爬取评分: {len(to_rate)} 个")
        for i, p in enumerate(to_rate, 1):
            handle = p.get("handle", "")
            if handle:
                rating = fetch_rating(url, handle)
                p["rating"] = rating
                store_rh = rating_history.setdefault(name, {})
                product_rh = store_rh.setdefault(p["title"], {})
                product_rh[today_str] = rating if rating else ""
                if i < len(to_rate):
                    time.sleep(RATING_INTERVAL)
            if i % 5 == 0:
                logger.info(f"    → {i}/{len(to_rate)}")

        # 价格历史
        store_price_history = price_history.get(name, {})
        today_prices = {}
        for p in products:
            key = p["title"]
            today_prices[key] = p["price"]
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

        store_price_history[today_str] = today_prices
        price_history[name] = store_price_history

        # 存 MySQL
        save_store_data(name, products, date.today())

        # 新品发现
        discovery_history = update_discovery(discovery_history, products, name, today_str)

        stores_ok += 1
        all_products.extend(products)
        total_count += len(products)
        logger.info(f"  ✅ {name} 完成")

    # ─── 采集eBay数据 ───
    ebay_products = crawl_ebay()
    if ebay_products:
        all_products.extend(ebay_products)
        total_count += len(ebay_products)
        logger.info(f"  📦 eBay: {len(ebay_products)} 个商品已加载")

    save_price_history(PRICE_HISTORY_FILE, price_history)
    save_rating_history(RATING_HISTORY_FILE, rating_history)
    save_discovery_history(DISCOVERY_HISTORY_FILE, discovery_history)

    save_competitor_excel(
        all_products=all_products,
        file_path=OUTPUT_FILE,
        rating_history=rating_history,
        discovery_history=discovery_history,
        price_changes=price_changes,
    )

    send_dingtalk_notify(product_count=total_count, keyword_count=len(STORES))

    # ─── 告警检查 ───
    check_alerts(all_products, today_str)

    # ─── 记录运行日志到MySQL ───
    save_run_log(
        run_date=date.today(),
        stores_ok=stores_ok,
        stores_fail=stores_fail,
        total_products=total_count,
        alerts_count=len([p for p in all_products if p.get("price")]),
    )

    in_sale = sum(1 for p in all_products if p.get("status") == "在售")
    sold_out = sum(1 for p in all_products if p.get("status") == "售罄")
    has_rating = sum(1 for p in all_products if p.get("rating"))
    logger.info(f"\n  ✅ 共 {total_count} 个商品 | 在售: {in_sale} | 售罄: {sold_out} | 有评分: {has_rating} 个")
    logger.info(f"  📁 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()