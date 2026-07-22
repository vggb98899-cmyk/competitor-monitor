"""周报生成器：读MySQL → DeepSeek分析 → 推飞书"""
import json
import requests
from datetime import date, timedelta
from pathlib import Path
from database import get_connection
from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, FEISHU_WEBHOOK, PRICE_HISTORY_FILE, BASE_DIR
from utils import logger


def generate_weekly_report():
    """入口：生成并推送周报"""
    logger.info("📊 生成周报...")
    today = date.today()
    week_ago = today - timedelta(days=7)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ① 本周新品
    cursor.execute("""
        SELECT store, title, category FROM products WHERE first_seen >= %s
    """, (week_ago,))
    new_products = cursor.fetchall()

    # ② 各店铺商品总数
    cursor.execute("""
        SELECT store, COUNT(*) as total FROM products GROUP BY store
    """)
    store_stats = cursor.fetchall()

    # ③ 品类分布
    cursor.execute("""
        SELECT store, category, COUNT(*) as cnt FROM products
        WHERE is_active = TRUE GROUP BY store, category ORDER BY cnt DESC
    """)
    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    # ④ 价格变动（从JSON文件读）
    price_data = {}
    if PRICE_HISTORY_FILE.exists():
        with open(PRICE_HISTORY_FILE, "r") as f:
            ph = json.load(f)
        for store, days in ph.items():
            dates = sorted(days.keys())
            if len(dates) >= 2:
                old_date = dates[-2] if dates[-2] >= week_ago.isoformat() else dates[0]
                new_date = dates[-1]
                old_prices = days[old_date]
                new_prices = days[new_date]
                changes = []
                for title, new_price in new_prices.items():
                    if title in old_prices and old_prices[title] != new_price:
                        try:
                            changes.append(f"{title[:40]}: ${old_prices[title]}→${new_price}")
                        except:
                            pass
                if changes:
                    price_data[store] = changes[:5]

    # 组装提示词
    prompt = f"""你是跨境电商运营分析师。根据过去7天的竞品监控数据，生成一份中文周报。

要求：
1. 自然语言，不要表格
2. 分4段：（1）价格变动最明显的品牌 （2）上新最多的品牌 （3）品类扩展趋势 （4）下周重点关注
3. 附一句eBay店铺状态说明
4. 如果某品牌没有数据就写"本周无明显变化"

=== 过去7天数据 ===

各店铺商品数：{', '.join(f"{s['store']}({s['total']}个)" for s in store_stats)}

本周新品（{len(new_products)}个）：
{chr(10).join(f"- {p['store']}: {p['title'][:50]}({p['category']})" for p in new_products[:20]) if new_products else "无"}

品类分布：
{chr(10).join(f"- {c['store']}: {c['category']}({c['cnt']}个)" for c in categories[:25])}

价格变动：
{chr(10).join(f"- {s}: " + "; ".join(v[:3]) for s, v in price_data.items()) if price_data else "本周无明显价格变动"}

eBay店铺状态：outdoor-gear-dude 正常采集，52个商品，仅有标题和标价数据。
"""

    # 调DeepSeek
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "输出简洁、有数据支撑的中文分析，语气专业。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1500,
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers, json=payload, timeout=60,
        )
        if resp.status_code == 200:
            report = resp.json()["choices"][0]["message"]["content"]
        else:
            report = f"AI接口异常({resp.status_code})"
            logger.error(f"DeepSeek 错误: {resp.text[:200]}")
    except Exception as e:
        report = f"网络异常({e})"
        logger.error(f"DeepSeek 异常: {e}")

    # 推飞书
    text = f"【竞品周报摘要】\n\n{report}"
    for i in range(3):
        try:
            r = requests.post(FEISHU_WEBHOOK, json={
                "msg_type": "text", "content": {"text": text},
            }, timeout=15)
            if r.status_code == 200:
                logger.info("✅ 周报推送成功")
                break
            else:
                logger.warning(f"⚠️ 推送失败(第{i+1}次)")
        except Exception as e:
            logger.warning(f"⚠️ 推送异常(第{i+1}次): {e}")
    else:
        logger.error("❌ 周报推送失败")

    logger.info("✅ 周报完成")
    return report


if __name__ == "__main__":
    generate_weekly_report()
