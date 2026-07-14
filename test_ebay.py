"""测试eBay能不能访问"""
from curl_cffi import requests

print("[测试] 访问 eBay 店铺页...")
try:
    r = requests.get(
        'https://www.ebay.com/str/bollmanoutdoorwarehouse',
        impersonate='chrome120',
        timeout=20
    )
    print(f"  状态码: {r.status_code}")
    print(f"  页面大小: {len(r.text)//1024}KB")
    if r.status_code == 200:
        print("  ✅ eBay可访问！")
    else:
        print(f"  ⚠️ 状态码异常: {r.status_code}")
except Exception as e:
    print(f"  ❌ {type(e).__name__}: {str(e)[:80]}")
