"""
环境测试脚本：验证 MySQL + 代理 是否可用
在你电脑上运行：
  python D:\Reasonix\my_first_project\test_env.py
"""
import sys
sys.path.insert(0, r"D:\Reasonix\my_first_project")

print("=" * 50)
print("  环境检测工具")
print("=" * 50)

# ─── 测试1：MySQL ───
print("\n[测试1] MySQL 数据库连接...")
try:
    import mysql.connector
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="123456",
    )
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"  ✅ MySQL连接成功！版本: {version[0]}")
    cursor.close()
    conn.close()
except ImportError:
    print("  ⚠️  python缺少 mysql-connector 库，正在安装...")
    import subprocess
    subprocess.run(["pip", "install", "mysql-connector-python"])
    print("  安装完成，请重新运行此脚本")
except Exception as e:
    print(f"  ❌ 连接失败: {e}")

# ─── 测试2：代理 ───
print("\n[测试2] 9http 住宅代理...")
try:
    import requests
    proxies = {
        'http': 'http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@global.9http.com:9091',
        'https': 'http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@global.9http.com:9091'
    }
    r = requests.get('http://ipinfo.io/json', proxies=proxies, timeout=15)
    data = r.json()
    print(f"  ✅ 代理可用！出口IP: {data.get('ip')}")
    print(f"     位置: {data.get('country')} - {data.get('city')}")
except Exception as e:
    print(f"  ❌ 代理不可用: {type(e).__name__}")
    print(f"     可能原因：代理格式不对或已过期")

# ─── 测试3：Etsy访问 ───
print("\n[测试3] 通过代理访问Etsy...")
try:
    from curl_cffi import requests as curl_req
    proxies = {
        'http': 'http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@global.9http.com:9091',
        'https': 'http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@global.9http.com:9091'
    }
    r = curl_req.get(
        'https://www.etsy.com/shop/KAMOutdoors',
        impersonate='chrome120',
        proxies=proxies,
        timeout=20
    )
    size_kb = len(r.text) // 1024
    has_listings = 'listing-link' in r.text or 'listing-card' in r.text
    print(f"  ✅ Etsy可访问！状态码: {r.status_code}  页面大小: {size_kb}KB")
    print(f"     商品列表在HTML里: {'是 ✅' if has_listings else '否 ⚠️（可能是JS加载）'}")
except Exception as e:
    print(f"  ❌ 访问失败: {type(e).__name__}: {str(e)[:100]}")

print("\n" + "=" * 50)
print("  检测完成，把上面的结果发给我")
print("=" * 50)
