"""测试MySQL连接"""
import mysql.connector

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="123456",
    )
    print("✅ MySQL连接成功！")
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"   MySQL版本: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")
    print("\n请确认：")
    print("  1. MySQL服务是否已启动？")
    print("  2. 密码是否是 123456？")
    print("  3. 端口是否是 3306？")
