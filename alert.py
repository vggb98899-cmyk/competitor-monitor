"""告警模块：价格变动>5% + 新品上架 + SKU下架 → 推钉钉"""
import json
from datetime import date, timedelta
from pathlib import Path
from config import FEISHU_WEBHOOK, PRICE_HISTORY_FILE, DISCOVERY_HISTORY_FILE, BASE_DIR
from utils import logger

PRICE_THRESHOLD = 5  # 价格变动超过5%触发告警


def check_alerts(today_products: list[dict], today_str: str):
    """
    检查三个维度：
      1. 价格变动 > 5%
      2. 新品上架（今天首次出现）
      3. 商品下架（昨天有，今天没有）

    Args:
        today_products: 今天采集的商品列表（含store/title/price字段）
        today_str: 今天的日期字符串 "2026-07-15"
    """
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    # 读取价格历史
    price_history = {}
    if PRICE_HISTORY_FILE.exists():
        with open(PRICE_HISTORY_FILE, "r", encoding="utf-8") as f:
            price_history = json.load(f)

    # 读取新品发现记录
    discovery = {}
    if DISCOVERY_HISTORY_FILE.exists():
        with open(DISCOVERY_HISTORY_FILE, "r", encoding="utf-8") as f:
            discovery = json.load(f)

    alerts = []

    # 按店铺分组
    from collections import defaultdict
    by_store = defaultdict(list)
    for p in today_products:
        by_store[p.get("store", "未知")].append(p)

    for store, products in by_store.items():
        # 获取该店铺的历史
        store_history = price_history.get(store, {})
        yesterday_prices = store_history.get(yesterday_str, {})
        today_titles = {p["title"] for p in products if p.get("title")}

        for p in products:
            title = p.get("title", "")
            price = p.get("price", "")

            # ① 价格变动 > 5%
            if title in yesterday_prices:
                try:
                    old = float(yesterday_prices[title])
                    new = float(price)
                    if old > 0:
                        change_pct = abs(new - old) / old * 100
                        if change_pct >= PRICE_THRESHOLD:
                            direction = "📈 涨价" if new > old else "📉 降价"
                            alerts.append(
                                f"{direction} | {store} | {title[:40]} | "
                                f"${old:.2f} → ${new:.2f} ({change_pct:.0f}%)"
                            )
                except ValueError:
                    pass

            # ② 新品上架
            store_discovery = discovery.get(store, {})
            if title in store_discovery and store_discovery[title] == today_str:
                alerts.append(f"🆕 新品上架 | {store} | {title[:50]} | ${price}")

        # ③ 商品下架（昨天有，今天没了）
        if yesterday_prices:
            for old_title in yesterday_prices:
                if old_title not in today_titles:
                    alerts.append(f"🗑️ 商品下架 | {store} | {old_title[:50]}")

    # 推送告警
    if alerts:
        _push_alerts(alerts[:10])  # 最多推10条，避免刷屏
        logger.info(f"🔔 触发 {len(alerts)} 条告警（已推送{min(10, len(alerts))}条）")
    else:
        logger.info(f"✅ 无异常告警")


def _push_alerts(alerts: list):
    """推送到飞书"""
    import requests

    lines = "\n".join(f"- {a}" for a in alerts)
    text = f"【竞品告警】\n\n{lines}\n\n{date.today()} 自动监测"
    message = {"msg_type": "text", "content": {"text": text}}

    try:
        resp = requests.post(FEISHU_WEBHOOK, json=message, timeout=10)
        if resp.status_code == 200:
            logger.info("✅ 告警推送成功")
    except Exception as e:
        logger.error(f"❌ 告警推送失败: {e}")
