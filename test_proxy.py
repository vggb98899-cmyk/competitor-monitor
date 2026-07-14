"""代理测试 - 多种方式"""
import subprocess, sys

print("=" * 50)
print("  代理测试（多方案）")
print("=" * 50)

# 方案A：Python requests + 标准格式
print("\n[方案A] requests + http://user:pass@host:port")
try:
    import requests
    proxies = {
        'http': 'http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@global.9http.com:9091',
        'https': 'http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@global.9http.com:9091',
    }
    r = requests.get('http://ipinfo.io/json', proxies=proxies, timeout=15)
    print(f"  ✅ IP: {r.json().get('ip')}")
except Exception as e:
    print(f"  ❌ {type(e).__name__}")

# 方案B：Python requests + 备用域名
print("\n[方案B] requests + as.9http.com 备用域名")
try:
    import requests
    proxies = {
        'http': 'http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@as.9http.com:9091',
        'https': 'http://soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@as.9http.com:9091',
    }
    r = requests.get('http://ipinfo.io/json', proxies=proxies, timeout=15)
    print(f"  ✅ IP: {r.json().get('ip')}")
except Exception as e:
    print(f"  ❌ {type(e).__name__}")

# 方案C：cmd curl 命令
print("\n[方案C] cmd 命令行 curl 测试...")
try:
    result = subprocess.run(
        ['curl', '-x', 'soxLrK8B-geo-US_Alabama_Bessemer:UZy7BDcwL3@global.9http.com:9091',
         '-s', 'http://ipinfo.io/json'],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode == 0 and 'ip' in result.stdout:
        import json
        data = json.loads(result.stdout)
        print(f"  ✅ IP: {data.get('ip')}")
    else:
        print(f"  ❌ 失败: {result.stderr[:100] or '无输出'}")
except FileNotFoundError:
    print("  ⚠️ 本机没有 curl 命令")
except Exception as e:
    print(f"  ❌ {type(e).__name__}")

print("\n" + "=" * 50)
print("  如果方案C成功，说明代理本身没问题")
print("  只是Python库的代理配置需要调整")
print("=" * 50)
