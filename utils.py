"""
工具模块：存放Excel、日志、价格历史等通用功能
"""
import json
import logging
from pathlib import Path
from datetime import date, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# ─── 日志设置 ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── 价格历史读写 ───

def load_price_history(filepath: Path) -> dict:
    """
    读取价格历史文件，返回 { "日期": { "商品标题": "价格", ... }, ... }
    如果文件不存在，返回空字典
    """
    if not filepath.exists():
        logger.info("价格历史文件不存在，首次运行")
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        history = json.load(f)
    logger.info(f"已读取价格历史，共 {len(history)} 天记录")
    return history


def save_price_history(filepath: Path, history: dict) -> None:
    """保存价格历史到文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    logger.info(f"价格历史已保存 → {filepath}")


def attach_price_changes(
    products: list[dict],
    history: dict,
    today_str: str,
    yesterday_str: str,
) -> list[dict]:
    """
    给每个商品加上"相比昨日涨跌额"字段

    Args:
        products: 商品列表（每项含 title / price）
        history: 历史数据 { "2026-07-08": { "商品标题": "价格", ... }, ... }
        today_str: 今天的日期字符串 "2026-07-09"
        yesterday_str: 昨天的日期字符串 "2026-07-08"

    Returns:
        新增了 change / change_label 字段的商品列表
    """
    yesterday_prices = history.get(yesterday_str, {})

    for product in products:
        title = product["title"]
        current_price = product["price"]

        # 如果没有历史价格
        if not yesterday_prices or title not in yesterday_prices:
            product["change"] = ""
            product["change_label"] = "—"
            continue

        # 计算涨跌
        try:
            old_price = float(yesterday_prices[title])
            new_price = float(current_price)
            diff = round(new_price - old_price, 2)

            if diff > 0:
                product["change_label"] = f"+${diff:.2f} ↑"
            elif diff < 0:
                product["change_label"] = f"-${abs(diff):.2f} ↓"
            else:
                product["change_label"] = "$0.00 ="
            product["change"] = diff
        except (ValueError, TypeError):
            product["change"] = ""
            product["change_label"] = "—"

    changed_count = sum(1 for p in products if p.get("change_label") not in ("—", ""))
    logger.info(f"价格对比完成，{changed_count} 个商品有历史可对比")
    return products


def update_history(
    history: dict,
    products: list[dict],
    today_str: str,
) -> dict:
    """
    将今天的商品价格写入历史记录

    Args:
        history: 现有历史数据
        products: 今天的商品列表
        today_str: 今天日期

    Returns:
        更新后的历史数据
    """
    today_record = {}
    for p in products:
        today_record[p["title"]] = p["price"]

    history[today_str] = today_record
    logger.info(f"已记录今天 ({today_str}) 共 {len(today_record)} 个商品价格")
    return history


# ─── Excel 输出 ───

def save_to_excel(products: list[dict], file_path: Path) -> str:
    """
    将商品列表保存为 Excel 文件

    Args:
        products: 商品字典列表，每项含 title / price / sales / category / change_label
        file_path: 输出文件路径

    Returns:
        保存成功的文件路径字符串
    """
    # 确保输出目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建工作簿
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "商品数据"

    # ─── 表头 ───
    headers = ["商品标题", "品类", "价格(USD)", "月销量", "相比昨日涨跌额"]
    header_font = Font(bold=True, size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(bold=True, size=11, color="FFFFFF")

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # ─── 数据行 ───
    for row, product in enumerate(products, 2):
        ws.cell(row=row, column=1, value=product.get("title", ""))
        ws.cell(row=row, column=2, value=product.get("category", ""))
        ws.cell(row=row, column=3, value=product.get("price", ""))
        ws.cell(row=row, column=4, value=product.get("sales", ""))
        ws.cell(row=row, column=5, value=product.get("change_label", ""))

    # ─── 调整列宽 ───
    ws.column_dimensions["A"].width = 52
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 20

    # 保存
    wb.save(file_path)
    logger.info(f"Excel 已保存 → {file_path}")
    return str(file_path)
