"""通知模块：通过飞书Webhook推送消息"""
import socket
import requests
from datetime import datetime
from config import FEISHU_WEBHOOK, FILE_SERVER_PORT, BASE_DIR
from utils import logger


def get_local_ip() -> str:
    try:
        # 获取本机局域网IP（不连接外部服务器）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("192.168.1.1", 80))  # 连本地网关，不走VPN
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def send_dingtalk_notify(product_count: int, keyword_count: int) -> bool:
    """发送飞书通知"""
    ip = get_local_ip()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    download_url = f"http://{ip}:{FILE_SERVER_PORT}/竞品分析日报.xlsx"

    text = (
        f"【竞品分析日报】采集完成 | {now_str}\n"
        f"商品 {product_count} 条 | 店铺 {keyword_count} 家\n"
        f"下载: {download_url}"
    )

    # 重试3次，避开网络抖动
    for i in range(3):
        try:
            resp = requests.post(FEISHU_WEBHOOK, json={
                "msg_type": "text",
                "content": {"text": text},
            }, timeout=15, proxies={"http": None, "https": None})
            result = resp.json()
            if resp.status_code == 200:
                logger.info(f"✅ 日报推送成功")
                return True
            else:
                logger.warning(f"⚠️ 日报推送失败(第{i+1}次): {result}")
        except Exception as e:
            logger.warning(f"⚠️ 日报推送异常(第{i+1}次): {e}")
        
        if i < 2:
            import time
            time.sleep(2)
    
    logger.error("❌ 日报推送失败（重试3次均失败）")
    return False
