"""
文件服务器：开机自启，提供 Excel 下载服务
强制下载模式，点击链接直接保存文件，不预览
"""
import os
import io
import socket
from pathlib import Path
from urllib.parse import quote
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8765
BASE_DIR = Path(__file__).parent
SERVE_DIR = BASE_DIR / "output"


class DownloadHandler(SimpleHTTPRequestHandler):
    """自定义处理器：强制下载"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

    def guess_type(self, path):
        return "application/octet-stream"

    def send_head(self):
        """重写：添加 Content-Disposition 头，强制下载"""
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()

        # 获取文件名
        filename = os.path.basename(path)

        # 读取文件
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except OSError:
            return super().send_head()

        # 发送响应头
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{quote(filename)}"')
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        # 返回文件数据（用BytesIO包装，父类需要文件对象）
        return io.BytesIO(data)


def get_local_ip() -> str:
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
    print(f"  文件服务器已启动（强制下载模式）")
    print(f"  {'='*50}")
    print(f"  Excel 文件地址:")
    print(f"     http://{ip}:{PORT}/竞品分析日报.xlsx")
    print(f"  {'='*50}")
    print(f"  保持此窗口不关闭\n")

    server = HTTPServer(("0.0.0.0", PORT), DownloadHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  已关闭")
        server.server_close()


if __name__ == "__main__":
    main()
