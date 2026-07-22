"""周报生成器：读MySQL → DeepSeek分析 → 推飞书"""
import json
import requests
from datetime import date, timedelta
from database import get_connection
from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL, FEISHU_WEBHOOK
from utils import logger


def get_weekly_data():
    """从MySQL读取过去7天的数据"""
    today = date.today()
    week_ago = today - timedelta(days=7)
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ① 本周新品
    cursor.execute("""
        SELECT store, title, category, price FROM snapshots s
        JOIN products p ON s.product_id = p.id
        WHERE s.captured_at >= %s AND p.first_seen >= %s
        ORDER BY store
    """, (week_ago, week_ago))
    new_products = cursor.fetchall()

    # ② 本周价格变动（取最新快照和7天前的快照对比）
    cursor.execute("""
        SELECT p.store, p.title, p.category,
               MIN(s.price) as old_price,
               MAX(s.price) as new_price
        FROM snapshots s
        JOIN products p ON s.product_id = p.id
        WHERE s.captured_at >= %s
        GROUP BY p.id
        HAVING old_price != new_price AND old_price > 0
        ORDER BY ABS(new_price - old_price) / old_price DESC
        LIMIT 20
    """, (week_ago,))
    price_changes = cursor.fetchall()

    # ③ 品类分布
    cursor.execute("""
        SELECT store, category, COUNT(*) as cnt
        FROM products WHERE is_active = TRUE
        GROUP BY store, category
        ORDER BY store, cnt DESC
    """)
    categories = cursor.fetchall()

    # ④ 各店铺商品总数
    cursor.execute("""
        SELECT store, COUNT(*) as total,
               SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active
        FROM products
        GROUP BY store
    """)
    store_stats = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "new_products": new_products,
        "price_changes": price_changes,
        "categories": categories,
        "store_stats": store_stats,
    }


def build_prompt(data: dict) -> str:
    """将数据组装成给AI的提示词"""
    # 统计新品
    new_by_store = {}
    for p in data["new_products"]:
        s = p["store"]
        if s not in new_by_store:
            new_by_store[s] = {"count": 0, "categories": set(), "products": []}
        new_by_store[s]["count"] += 1
        new_by_store[s]["categories"].add(p["category"])
        new_by_store[s]["products"].append(f"{p['title']}(${p['price']})")

    # 统计价格变动
    price_by_store = {}
    for p in data["price_changes"]:
        s = p["store"]
        if s not in price_by_store:
            price_by_store[s] = []
        change_pct = abs(float(p["new_price"]) - float(p["old_price"])) / float(p["old_price"]) * 100
        direction = "涨" if float(p["new_price"]) > float(p["old_price"]) else "跌"
        price_by_store[s].append(f"{p['title']}({p['category']}): {direction}${p['old_price']}→${p['new_price']}({change_pct:.0f}%)")

    prompt = f"""你是跨境电商运营分析师。根据以下过去7天的竞品监控数据，生成一份中文周报摘要。

格式要求：
1. 用自然语言写，不要表格
2. 分为4个部分（如果某部分没有数据就写"本周无明显变化"）：
   - 价格变动最明显的品牌+品类+幅度
   - 上新最多的品牌+品类
   - 品类扩展趋势（哪个品牌在扩新品类）
   - 下周重点关注建议（推荐1-2个品牌及原因）
3. 语气专业、简洁，每句话都要有数据支撑
4. 必须包含eBay店铺的状态说明

=== 数据开始 ===

各店铺商品总数：
{chr(10).join(f"- {s['store']}: 共{s['total']}个(活跃{s['active']}个)" for s in data['store_stats'])}

本周新品：
{chr(10).join(f"- {s}: {v['count']}个新品({', '.join(v['categories'])})" for s, v in new_by_store.items()) if new_by_store else "无"}

本周价格变动：
{chr(10).join(f"- {s}: " + "; ".join(v[:3]) for s, v in price_by_store.items()) if price_by_store else "无显著变动"}

品类分布（按店铺）：
{chr(10).join(f"- {c['store']}: {c['category']}({c['cnt']}个)" for c in data['categories'][:30])}

=== 数据结束 ===

注意：
- 时间范围：过去7天
- 如果某品牌没有新品或价格变动，不要编造
- eBay店铺只有标题和价格，没有销量评分，请单独说明"""
    return prompt


def call_deepseek(prompt: str) -> str:
    """调用DeepSeek API生成周报"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的跨境电商竞品分析助手。输出简洁、有数据支撑的中文分析。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1500,
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            logger.error(f"DeepSeek API 错误: {resp.status_code} {resp.text[:200]}")
            return "周报生成失败（AI接口异常）"
    except Exception as e:
        logger.error(f"DeepSeek API 异常: {e}")
        return "周报生成失败（网络异常）"


def push_to_feishu(report: str):
    """推送到飞书"""
    text = f"【竞品周报摘要】\n\n{report}"
    try:
        resp = requests.post(FEISHU_WEBHOOK, json={
            "msg_type": "text",
            "content": {"text": text},
        }, timeout=15)
        if resp.status_code == 200:
            logger.info("✅ 周报推送成功")
        else:
            logger.warning(f"⚠️ 周报推送失败: {resp.text}")
    except Exception as e:
        logger.error(f"❌ 周报推送异常: {e}")


def generate_weekly_report():
    """入口：生成并推送周报"""
    logger.info("📊 正在生成周报...")

    # 读数据
    data = get_weekly_data()
    logger.info(f"  - 本周新品: {len(data['new_products'])} 个")
    logger.info(f"  - 价格变动: {len(data['price_changes'])} 个")
    logger.info(f"  - 品类分布: {len(data['categories'])} 条")

    # 调AI
    prompt = build_prompt(data)
    report = call_deepseek(prompt)

    # 推飞书
    push_to_feishu(report)
    logger.info("✅ 周报流程完成")
    return report
