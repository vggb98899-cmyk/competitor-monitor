"""
任务一入口：执行38家店铺探测 → 输出《38家店铺数据可信度探测报告》

运行方式：
  python task1_probe.py

输出：
  output/38家店铺数据可信度探测报告.xlsx
"""
import time
from pathlib import Path
from stores import STORES
from probe import probe_store
from utils import save_probe_report, logger
from config import BASE_DIR


def main():
    logger.info("=" * 60)
    logger.info("  《38家店铺数据可信度探测》开始")
    logger.info(f"  共 {len(STORES)} 家店铺")
    logger.info("=" * 60)

    all_results = []

    for i, store in enumerate(STORES, 1):
        logger.info(f"\n[{i}/{len(STORES)}] {store['name']}")

        # 执行探测
        result = probe_store(store["url"], store["name"])

        # 补充店铺信息（用于Excel报表）
        result["category"] = store["category"]
        result["is_key"] = store["is_key"]

        all_results.append(result)

        # 每家店之间间隔2秒，避免触发限流
        if i < len(STORES):
            logger.info(f"  等待2秒，准备探测下一家...")
            time.sleep(2)

    # 输出报告
    output_path = BASE_DIR / "output" / "38家店铺数据可信度探测报告.xlsx"
    save_probe_report(all_results, output_path)

    # 统计摘要
    a_count = sum(1 for r in all_results if r.get("data_level") == "A")
    b_count = sum(1 for r in all_results if r.get("data_level") == "B")
    c_count = sum(1 for r in all_results if r.get("data_level") == "C")
    accessible = sum(1 for r in all_results if r.get("api", {}).get("api_accessible"))

    logger.info("\n" + "=" * 60)
    logger.info("  📊 探测完成！结果摘要：")
    logger.info(f"  ✅ 接口可访问: {accessible}/{len(STORES)} 家")
    logger.info(f"  🅰️  A类（有销量）: {a_count} 家")
    logger.info(f"  🅱️  B类（有评分）:  {b_count} 家")
    logger.info(f"  🅲  C类（基础字段）: {c_count} 家")
    logger.info(f"  📁 报告文件: {output_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
