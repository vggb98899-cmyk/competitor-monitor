"""查看MySQL数据统计"""
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1", port=3306, user="root",
    password="123456", database="competitor_db"
)
cursor = conn.cursor()

print("=" * 40)
print("  数据库数据统计")
print("=" * 40)

cursor.execute("""
    SELECT store, COUNT(*),
           SUM(CASE WHEN is_active THEN 1 ELSE 0 END)
    FROM products GROUP BY store ORDER BY store
""")
print("\n📦 各店铺商品数:")
for row in cursor.fetchall():
    total = int(row[1])
    active = int(row[2])
    print(f"  {row[0]:<20s} | 共 {total:4d} 个 | 活跃 {active:4d} 个")

cursor.execute("SELECT COUNT(*) FROM snapshots")
print(f"\n📊 快照记录总数: {int(cursor.fetchone()[0])} 条")

cursor.execute("""
    SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2)
    FROM information_schema.tables
    WHERE table_schema = 'competitor_db'
""")
print(f"💾 数据库大小: {cursor.fetchone()[0]} MB")

cursor.close()
conn.close()
print("\n✅ 数据正常！")
