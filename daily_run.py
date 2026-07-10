"""
每日运行脚本：跑 main.py → 发钉钉通知
定时任务每天早上8点调用此脚本
"""
import sys
import subprocess
from pathlib import Path
from dingtalk_notify import send_dingtalk_notify
from config import BASE_DIR, KEYWORDS
from utils import logger


def main():
    """执行完整流程：采集数据 → 钉钉推送"""
    logger.info("=" * 50)
    logger.info("📅 每日商品采集开始")
    logger.info("=" * 50)

    # 1. 运行 main.py
    main_py = BASE_DIR / "main.py"
    logger.info(f"▶ 正在执行: {main_py}")

    result = subprocess.run(
        [sys.executable, str(main_py)],
        capture_output=True,
        text=True,
        timeout=120,  # 最长等2分钟
    )

    # 打印 main.py 的输出
    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            logger.info(f"  {line}")

    if result.returncode != 0:
        logger.error(f"❌ main.py 执行失败 (退出码: {result.returncode})")
        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                logger.error(f"  {line}")
        # 即使失败也尝试通知
        send_dingtalk_notify(product_count=0, keyword_count=len(KEYWORDS))
        return

    # 2. 解析商品数量（从日志中提取）
    product_count = 0
    for line in result.stdout.split("\n"):
        if "完成！共采集" in line:
            try:
                import re
                match = re.search(r"共采集 (\d+) 条", line)
                if match:
                    product_count = int(match.group(1))
            except:
                pass

    # 3. 发送钉钉通知
    send_dingtalk_notify(
        product_count=product_count,
        keyword_count=len(KEYWORDS),
    )

    logger.info("=" * 50)
    logger.info("✅ 每日采集流程完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
