"""安装Playwright + Chromium"""
import subprocess, sys

print("=" * 50)
print("  安装 Playwright")
print("=" * 50)

# 第1步：pip安装
print("\n[步骤1] pip install playwright...")
r = subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], capture_output=True, text=True)
if r.returncode == 0:
    print("  ✅ playwright 安装成功")
else:
    print(f"  ❌ 安装失败: {r.stderr[:200]}")
    sys.exit(1)

# 第2步：安装Chromium
print("\n[步骤2] playwright install chromium...")
print("  ⏳ 正在下载Chromium（约200MB），请等待...")
r = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True, text=True)
if r.returncode == 0:
    print("  ✅ Chromium 安装成功！")
else:
    print(f"  ❌ 安装失败: {r.stderr[:300]}")
    print("  可以尝试手动安装: playwright install chromium")

print("\n" + "=" * 50)
print("  安装完成！现在测试 Playwright 能否访问 eBay")
print("=" * 50)
