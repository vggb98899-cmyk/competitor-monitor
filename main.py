"""
入口文件：编排整个流程，不超过50行
"""
from datetime import date, timedelta
from config import KEYWORDS, OUTPUT_FILE, PRICE_HISTORY_FILE, HISTORY_LOOKBACK_DAYS
from crawler import fetch_all_products, fetch_all_products_full, filter_by_keywords, count_by_category
from utils import (
    save_to_excel,
    load_price_history,
    save_price_history,
    attach_price_changes,
    update_history,
    logger,
)


def main():
    """主流程：拉取数据 → 多关键词过滤 → 价格对比 → 存 Excel"""
    logger.info("========== Manduka 商品采集开始 ==========")
    logger.info(f"搜索关键词: {', '.join(KEYWORDS)}")

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=HISTORY_LOOKBACK_DAYS)).isoformat()

    # 1. 拉取全量商品
    all_products = fetch_all_products_full()

    # 2. 品类排行统计
    category_summary = count_by_category(all_products)

    # 3. 按关键词过滤（从全量里过滤，数据更多）
    products = filter_by_keywords(all_products)

    # 4. 读取价格历史
    history = load_price_history(PRICE_HISTORY_FILE)

    # 5. 计算价格变化
    products = attach_price_changes(products, history, today_str, yesterday_str)

    # 6. 保存今天的价格到历史
    history = update_history(history, products, today_str)
    save_price_history(PRICE_HISTORY_FILE, history)

    # 7. 保存到 Excel（含品类排行Sheet）
    file_path = save_to_excel(products, OUTPUT_FILE, category_summary)

    logger.info(f"✅ 完成！共采集 {len(products)} 条商品，覆盖 {len(KEYWORDS)} 个关键词")
    logger.info(f"📁 Excel 文件: {file_path}")
    logger.info("========== Manduka 商品采集结束 ==========")


if __name__ == "__main__":
    main()
