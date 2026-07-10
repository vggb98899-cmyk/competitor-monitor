"""
文件服务器：开机自启，提供 Excel 下载服务
启动后访问 http://你电脑IP:8765/ 即可下载文件
"""
import socket
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 服务端口
PORT = 8765

# 提供下载的目录（output 文件夹）
BASE_DIR = Path(__file__).parent
SERVE_DIR = BASE_DIR / "output"


class DownloadHandler(SimpleHTTPRequestHandler):
    """自定义处理器：强制下载，不预览"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

    def guess_type(self, path):
        """让所有文件都触发下载"""
        return "application/octet-stream"


def get_local_ip() -> str:
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    ip = get_local_ip()
    print(f"\n{'='*50}")
    print(f"  Manduka 文件服务器已启动")
    print(f"  {'='*50}")
    print(f"  局域网地址:")
    print(f"     http://{ip}:{PORT}/")
    print(f"  本机地址:")
    print(f"     http://127.0.0.1:{PORT}/")
    print(f"  Excel 文件地址:")
    print(f"     http://{ip}:{PORT}/manduka_products.xlsx")
    print(f"  {'='*50}")
    print(f"  保持此窗口不关闭，其他电脑才能下载\n")

    server = HTTPServer(("0.0.0.0", PORT), DownloadHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  服务已关闭")
        server.server_close()


if __name__ == "__main__":
    main()
