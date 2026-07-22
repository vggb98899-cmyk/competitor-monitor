"""通知模块：通过飞书Webhook推送消息"""
import socket
import requests
from datetime import datetime
from config import FEISHU_WEBHOOK, FILE_SERVER_PORT, BASE_DIR
from utils import logger


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"


def send_dingtalk_notify(product_count: int, keyword_count: int) -> bool:
    """发送飞书通知（函数名保持兼容）"""
    ip = get_local_ip()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    download_url = f"http://{ip}:{FILE_SERVER_PORT}/竞品分析日报.xlsx"

    text = (
        f"【竞品分析日报】采集完成 | {now_str}\n"
        f"商品 {product_count} 条 | 店铺 {keyword_count} 家\n"
        f"下载: {download_url}"
    )

    try:
        resp = requests.post(FEISHU_WEBHOOK, json={
            "msg_type": "text",
            "content": {"text": text},
        }, timeout=15)
        result = resp.json()
        if resp.status_code == 200:
            logger.info(f"✅ 日报推送成功")
            return True
        else:
            logger.error(f"❌ 日报推送失败: {result}")
            return False
    except Exception as e:
        logger.error(f"❌ 日报推送异常: {e}")
        return False
