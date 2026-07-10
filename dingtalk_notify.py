"""
钉钉通知模块：通过Webhook推送Excel下载链接到群
"""
import socket
import json
import requests
from datetime import datetime
from config import DINGTALK_WEBHOOK, FILE_SERVER_PORT, BASE_DIR
from utils import logger


def get_local_ip() -> str:
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_file_size_mb(path) -> str:
    """获取文件大小（MB），保留两位小数"""
    try:
        size = path.stat().st_size / (1024 * 1024)
        return f"{size:.2f}MB"
    except:
        return "未知"


def send_dingtalk_notify(product_count: int, keyword_count: int) -> bool:
    """
    发送钉钉通知，包含Excel下载链接

    Args:
        product_count: 采集到的商品数量
        keyword_count: 关键词数量

    Returns:
        是否发送成功
    """
    ip = get_local_ip()
    file_name = "manduka_products.xlsx"
    download_url = f"http://{ip}:{FILE_SERVER_PORT}/{file_name}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 检查文件是否存在
    excel_path = BASE_DIR / "output" / file_name
    file_info = ""
    if excel_path.exists():
        file_size = get_file_size_mb(excel_path)
        file_info = f"\n📦 文件大小：{file_size}"

    # 构建消息（必须包含"推送"关键字）
    message = {
        "msgtype": "actionCard",
        "actionCard": {
            "title": "Manduka 商品数据日报 —— 推送",
            "text": (
                f"### Manduka 商品数据日报 —— 推送\n\n"
                f"⏰ **采集时间：** {now_str}\n"
                f"✅ **采集状态：** 完成\n"
                f"📊 **商品数量：** {product_count} 条\n"
                f"🔑 **搜索关键词：** {keyword_count} 个\n"
                f"{file_info}\n\n"
                f"📥 点击下方按钮下载 Excel 报表"
            ),
            "btnOrientation": "0",
            "singleTitle": "📥 下载报表",
            "singleURL": download_url,
        },
    }

    try:
        resp = requests.post(
            DINGTALK_WEBHOOK,
            json=message,
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
        result = resp.json()
        if result.get("errcode") == 0:
            logger.info(f"✅ 钉钉通知发送成功")
            return True
        else:
            logger.error(f"❌ 钉钉通知发送失败: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ 钉钉通知发送异常: {e}")
        return False
