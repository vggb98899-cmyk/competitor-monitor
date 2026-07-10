"""
定时任务注册脚本：以管理员身份运行，一次配置永久生效

注册两个任务：
  1. MandukaFileServer  → 开机自启文件服务器
  2. MandukaDailyReport → 每天早上8点采集数据 + 钉钉推送
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
PYTHON = sys.executable  # Python 解释器路径


def run_as_admin():
    """检查是否有管理员权限"""
    try:
        return subprocess.run(
            ["net", "session"],
            capture_output=True,
            text=True,
        ).returncode == 0
    except:
        return False


def create_task(name: str, description: str, command: str, args: str, trigger: str, start_time: str = "") -> bool:
    """创建 Windows 定时任务"""
    cmd = [
        "schtasks", "/create",
        "/tn", name,
        "/tr", f'"{command}" "{args}"',
        "/sc", trigger,
        "/f",  # 已存在则覆盖
    ]
    if start_time:
        cmd += ["/st", start_time]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ 创建成功: {name}")
        return True
    else:
        print(f"  ❌ 创建失败: {name}")
        print(f"     错误: {result.stderr.strip()}")
        return False


def main():
    print("=" * 55)
    print("  Manduka 定时任务安装脚本")
    print("=" * 55)

    # 检查管理员权限
    if not run_as_admin():
        print("\n  ⚠️  需要管理员权限！")
        print("  请右键 → 以管理员身份运行此脚本")
        print("\n  或者：")
        print("  1. 右键 setup_schedule.py")
        print("  2. 选择「用Python打开」")
        input("\n  按回车键退出...")
        return

    daily_run_py = BASE_DIR / "daily_run.py"
    file_server_py = BASE_DIR / "file_server.py"

    print(f"\n  项目目录: {BASE_DIR}")
    print(f"  Python路径: {PYTHON}")
    print(f"  每日脚本: {daily_run_py}")
    print(f"  文件服务: {file_server_py}\n")

    # 任务1：文件服务器开机自启（用户登录时启动）
    print("  [任务1] 注册文件服务器开机自启...")
    create_task(
        name="MandukaFileServer",
        description="Manduka 商品数据文件服务器，开机后台自动启动",
        command=PYTHON,
        args=str(file_server_py),
        trigger="ONLOGON",  # 用户登录时启动
    )

    print()

    # 任务2：每天早上8点采集数据
    print("  [任务2] 注册每日8:00采集任务...")
    create_task(
        name="MandukaDailyReport",
        description="每天早8点采集 Manduka 商品数据并推送到钉钉",
        command=PYTHON,
        args=str(daily_run_py),
        trigger="DAILY",
        start_time="08:00",
    )

    print(f"\n  {'='*55}")
    print("  配置完成！以下是两个任务的效果：")
    print(f"  {'='*55}")
    print(f"  🔄 MandukaFileServer")
    print(f"     触发：每次你登录Windows时自动启动")
    print(f"     作用：在后台开启文件下载服务")
    print(f"  🔄 MandukaDailyReport")
    print(f"     触发：每天 08:00")
    print(f"     作用：自动采集数据 → 推送到钉钉群")
    print(f"  {'='*55}")
    print(f"  ⚠️  注意事项：")
    print(f"  1. 你的电脑必须在 08:00 前开机并联网")
    print(f"  2. 文件服务器必须先启动（开机自启已配置）")
    print(f"  3. 不需要时可用「任务计划程序」禁用或删除")
    print(f"  {'='*55}\n")

    input("按回车键退出...")


if __name__ == "__main__":
    main()
