"""
工具模块：存放Excel、日志等通用功能
"""
import logging
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill

# ─── 日志设置 ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def save_to_excel(products: list[dict], file_path: Path) -> str:
    """
    将商品列表保存为 Excel 文件

    Args:
        products: 商品字典列表，每项含 title / price / sales 字段
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
    headers = ["商品标题", "价格(USD)", "月销量"]
    header_font = Font(bold=True, size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(bold=True, size=11, color="FFFFFF")

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font_white
        cell.fill = header_fill

    # ─── 数据行 ───
    for row, product in enumerate(products, 2):
        ws.cell(row=row, column=1, value=product.get("title", ""))
        ws.cell(row=row, column=2, value=product.get("price", ""))
        ws.cell(row=row, column=3, value=product.get("sales", ""))

    # ─── 调整列宽 ───
    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 12

    # 保存
    wb.save(file_path)
    logger.info(f"Excel 已保存 → {file_path}")
    return str(file_path)
