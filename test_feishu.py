"""测试飞书Webhook连通性"""
import requests

url = "https://open.feishu.cn/open-apis/bot/v2/hook/49a763a2-f5e0-4a27-93db-461eec32fed2"
text = "【竞品】测试消息 - 如果看到这条说明通了"

print("测试飞书Webhook...")
try:
    resp = requests.post(url, json={"msg_type": "text", "content": {"text": text}}, timeout=15)
    print(f"状态码: {resp.status_code}")
    print(f"返回: {resp.text}")
    if resp.status_code == 200:
        print("✅ 飞书Webhook正常！")
    else:
        print("❌ 飞书返回错误")
except Exception as e:
    print(f"❌ {type(e).__name__}: {e}")
