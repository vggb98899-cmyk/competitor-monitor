"""测试通过 SOCKS5 代理访问 - 多方案"""
from curl_cffi import requests

proxies = {
    'http': 'socks5://127.0.0.1:10808',
    'https': 'socks5://127.0.0.1:10808',
}

# 先测一个简单网站确认代理通不通
print("[测试1] 通过SOCKS5访问 ipinfo.io...")
try:
    r = requests.get('http://ipinfo.io/json', impersonate='chrome120', proxies=proxies, timeout=15)
    print(f"  ✅ 成功！出口IP: {r.json().get('ip')}")
except Exception as e:
    print(f"  ❌ {type(e).__name__}")

# 换一个浏览器指纹访问Etsy
print("\n[测试2] 换safari指纹访问Etsy...")
try:
    r = requests.get(
        'https://www.etsy.com/shop/KAMOutdoors',
        impersonate='safari15_5',
        proxies=proxies,
        timeout=20
    )
    print(f"  状态码: {r.status_code}  大小: {len(r.text)//1024}KB")
    if r.status_code == 200:
        print("  ✅ 成功！")
    else:
        print(f"  ⚠️ 被拦截，试试其他方式")
except Exception as e:
    print(f"  ❌ {type(e).__name__}")

# 用更完整的浏览器头
print("\n[测试3] 加完整请求头 + chrome120...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
    }
    r = requests.get(
        'https://www.etsy.com/shop/KAMOutdoors',
        impersonate='chrome120',
        headers=headers,
        proxies=proxies,
        timeout=20
    )
    print(f"  状态码: {r.status_code}  大小: {len(r.text)//1024}KB")
    if r.status_code == 200:
        print("  ✅ 成功！")
except Exception as e:
    print(f"  ❌ {type(e).__name__}")

# 访问eBay试试
print("\n[测试4] 通过SOCKS5访问eBay...")
try:
    r = requests.get(
        'https://www.ebay.com/str/bollmanoutdoorwarehouse',
        impersonate='chrome120',
        proxies=proxies,
        timeout=20
    )
    print(f"  状态码: {r.status_code}  大小: {len(r.text)//1024}KB")
    if r.status_code == 200:
        print("  ✅ eBay可访问！")
except Exception as e:
    print(f"  ❌ {type(e).__name__}")
