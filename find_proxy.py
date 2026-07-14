"""自动检测本机VPN代理端口"""
import socket

# 常见的Clash/V2Ray本地代理端口
COMMON_PORTS = [
    # Clash 默认端口
    (7890, "HTTP"),
    (7891, "SOCKS"),
    (7892, "HTTP"),
    # V2Ray 默认端口
    (10809, "HTTP"),
    (10808, "SOCKS"),
    (1081, "HTTP"),
    # SSR/Shadowsocks 默认端口
    (1080, "SOCKS"),
    # 其他常见端口
    (8080, "HTTP"),
    (3128, "HTTP"),
    (9090, "HTTP"),
]

print("=" * 50)
print("  正在检测本机VPN代理端口...")
print("=" * 50)

found = []
for port, ptype in COMMON_PORTS:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex(('127.0.0.1', port))
    s.close()
    if result == 0:
        print(f"  ✅ 端口 {port} ({ptype}) → 可用！")
        found.append((port, ptype))

if not found:
    print("\n  ❌ 没有找到常见代理端口")
    print("  请检查你的VPN软件设置，找到'本地代理端口'")
    print("  通常在VPN的设置页面可以看到")
else:
    print(f"\n  ✅ 找到 {len(found)} 个可用端口")
    print("\n  使用方式（在代码中配置）：")
    print(f"  方式1: 设置系统环境变量")
    for port, ptype in found:
        if ptype == "HTTP":
            print(f"     set HTTP_PROXY=http://127.0.0.1:{port}")
            print(f"     set HTTPS_PROXY=http://127.0.0.1:{port}")
    print(f"  方式2: 在Python代码中直接配置")
    for port, ptype in found:
        if ptype == "HTTP":
            print(f"     proxies={{'http':'http://127.0.0.1:{port}', 'https':'http://127.0.0.1:{port}'}}")

print("=" * 50)
