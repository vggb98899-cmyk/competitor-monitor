"""测试eBay API - 旧版Finding API用App ID"""
import requests
from urllib.parse import quote

APP_ID = "-vggb9889-SBX-96248bbc0-49fcc3f1"

# 沙盒Finding API端点
url = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"

params = {
    "OPERATION-NAME": "findItemsByKeywords",
    "SERVICE-VERSION": "1.0.0",
    "SECURITY-APPNAME": APP_ID,
    "RESPONSE-DATA-FORMAT": "JSON",
    "keywords": "outdoor gear camping",
    "paginationInput.entriesPerPage": 5,
    "GLOBAL-ID": "EBAY-US",
}

print("[测试] 旧版Finding API + App ID...")
try:
    r = requests.get(url, params=params, timeout=15)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        resp = data.get("findItemsByKeywordsResponse", [{}])[0]
        ack = resp.get("ack", [""])[0]
        print(f"  响应状态: {ack}")
        items = resp.get("searchResult", [{}])[0].get("item", [])
        print(f"  ✅ 找到 {len(items)} 个商品")
        for item in items[:3]:
            title = item.get("title", [""])[0]
            price = item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__value__", "")
            url_item = item.get("viewItemURL", [""])[0]
            print(f"     {title[:50]} | ${price}")
        print(f"\n  ⚠️ 注意：这是沙盒数据，不是真实商品")
    else:
        print(f"  返回: {r.text[:300]}")
except Exception as e:
    print(f"  ❌ {type(e).__name__}: {str(e)[:100]}")
