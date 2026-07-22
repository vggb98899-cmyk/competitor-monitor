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
        with open(PRICE_HISTORY_FILE, "r", encoding="utf-8") as f:
            ph = json.load(f)

        # 处理两种格式
        first_key = next(iter(ph), "")
        if first_key and first_key[0].isdigit():  # 旧格式：{日期: {标题: 价格}}
            flat_ph = {"默认": ph}
        else:  # 新格式：{店铺: {日期: {标题: 价格}}}
            flat_ph = ph

        for store, days in flat_ph.items():
            dates = sorted(d for d in days if d[0].isdigit())
            if len(dates) >= 2:
                old_date = dates[-2]
                new_date = dates[-1]
                old_prices = days[old_date]
                new_prices = days[new_date]
                if isinstance(new_prices, dict):
                    changes = []
                    for title, new_price in new_prices.items():
                        if title in old_prices and old_prices[title] != new_price:
                            try:
                                changes.append(f"{title[:30]}: ${str(old_prices[title])}→${str(new_price)}")
                            except:
                                pass
                    if changes:
                        price_data[store] = changes[:5]

    # 计算各店铺的品类占比
    cat_by_store = {}
    for c in categories:
        s = c["store"]
        if s not in cat_by_store:
            cat_by_store[s] = {"total": 0, "cats": []}
        cat_by_store[s]["total"] += c["cnt"]
        cat_by_store[s]["cats"].append((c["category"], c["cnt"]))

    cat_summary = []
    for s, info in cat_by_store.items():
        parts = []
        for cat, cnt in info["cats"][:6]:
            pct = cnt / info["total"] * 100
            parts.append(f"{cat}({pct:.0f}%)")
        # 标记未分类问题
        uncat_pct = sum(cnt for cat, cnt in info["cats"] if cat == "未分类") / info["total"] * 100 if any(cat == "未分类" for cat, _ in info["cats"]) else 0
        flag = " ⚠️未分类占比高，属采集缺陷" if uncat_pct > 20 else ""
        cat_summary.append(f"- {s}: " + ", ".join(parts) + flag)

    # 组装提示词
    prompt = f"""你是跨境电商运营分析师。根据过去7天的竞品监控数据，生成一份高质量中文周报。

【输出要求】
- 自然语言，不要表格
- 每句话必须有具体数字支撑
- 分4段，每段必须给明确结论：

第1段「价格变动」：
  - 列出变动幅度最大的品牌+品类+具体百分比（如"XX品牌帐篷均价下降8%"）
  - 如果无变动直接写"本周各品牌价格体系稳定，无超5%的调价动作"

第2段「上新分析」：
  - 按品牌分开说，新品最多的品牌排前面
  - 每个品牌要写：新增X个SKU，其中Y%集中在XX品类
  - 判断：这是正常补货还是战略性扩品

第3段「品类趋势」：
  - 指出品类占比有明显变化的品牌
  - 对于"未分类"占比高的品牌，判断是采集缺陷还是真实业务信号
  - 采集缺陷的判断标准：未分类>20%且该品牌大部分商品是已知品类→属采集问题

第4段「下周关注」：
  - 只推荐1-2个品牌，说清楚为什么
  - 必须附带操作建议

eBay部分：只在出现价格异常时报详情，无异常则只写一句"eBay店铺正常，无异常"

=== 过去7天数据 ===

各店铺商品总数：
{chr(10).join(f"- {s['store']}: {s['total']}个" for s in store_stats)}

本周新品（共{len(new_products)}个）：
{chr(10).join(f"- {p['store']}: {p['title'][:40]}({p['category']})" for p in new_products[:25]) if new_products else "无"}

品类分布（占比）：
{chr(10).join(cat_summary)}

价格变动记录：
{chr(10).join(f"- {s}: " + "; ".join(v[:3]) for s, v in price_data.items()) if price_data else "本周无显著价格变动"}

eBay店铺：户外装备店52个商品正常采集，仅有标价数据。
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
            proxies={"http": None, "https": None},  # 不走VPN
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
            }, timeout=15, proxies={"http": None, "https": None})
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
