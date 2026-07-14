"""试多种eBay URL格式"""
import re
from curl_cffi import requests

proxies = {
    'http': 'socks5://127.0.0.1:10808',
    'https': 'socks5://127.0.0.1:10808',
}

urls = [
    ("店铺页(标准)", "https://www.ebay.com/str/bollmanoutdoorwarehouse"),
    ("店铺页(m.html)", "https://www.ebay.com/str/bollmanoutdoorwarehouse/m.html"),
    ("搜索(ssn)", "https://www.ebay.com/sch/i.html?_ssn=bollmanoutdoorwarehouse&_ipg=60"),
    ("搜索(store)", "https://www.ebay.com/sch/i.html?_dkr=1&store=bollmanoutdoorwarehouse&_ipg=60"),
    ("用户页", "https://www.ebay.com/usr/bollmanoutdoorwarehouse"),
]

for name, url in urls:
    try:
        r = requests.get(url, impersonate='chrome120', proxies=proxies, timeout=20)
        # 检查是不是商品列表页
        has_items = 's-item' in r.text or 's-item__title' in r.text or 'gallery-item' in r.text
        items_count = len(set(re.findall(r'/itm/(\d+)', r.text)))
        import re
        print(f"{name:15s} | 状态={r.status_code} | 大小={len(r.text)//1024}KB | 含商品卡片={has_items} | 商品ID数={items_count}")
    except Exception as e:
        print(f"{name:15s} | ❌ {type(e).__name__}")
