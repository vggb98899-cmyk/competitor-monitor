"""
入口文件：编排整个流程，不超过50行
"""
from config import SEARCH_KEYWORD, OUTPUT_FILE
from crawler import fetch_all_products, filter_by_keyword, extract_fields
from utils import save_to_excel, logger


def main():
    """主流程：拉取数据 → 过滤 → 提取字段 → 存 Excel"""
    logger.info("========== Manduka 商品采集开始 ==========")

    # 1. 拉取所有商品
    raw_products = fetch_all_products()

    # 2. 按关键词过滤
    matched = filter_by_keyword(raw_products, SEARCH_KEYWORD)

    # 3. 提取需要的字段
    products = extract_fields(matched)

    # 4. 保存到 Excel
    file_path = save_to_excel(products, OUTPUT_FILE)

    logger.info(f"✅ 完成！共采集 {len(products)} 条商品")
    logger.info(f"📁 Excel 文件: {file_path}")
    logger.info("========== Manduka 商品采集结束 ==========")


if __name__ == "__main__":
    main()
