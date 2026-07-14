"""测试不用代理能不能直接访问Etsy"""
from curl_cffi import requests

print("[测试] 不用代理，直接访问 Etsy...")
try:
    r = requests.get(
        'https://www.etsy.com/shop/KAMOutdoors',
        impersonate='chrome120',
        timeout=20
    )
    print(f"  状态码: {r.status_code}")
    print(f"  页面大小: {len(r.text)//1024}KB")
    if 'KAMOutdoors' in r.text:
        print("  ✅ 页面内容正常，包含店铺名")
    else:
        print("  ⚠️ 页面可能被拦截")
except Exception as e:
    print(f"  ❌ {type(e).__name__}: {str(e)[:80]}")
