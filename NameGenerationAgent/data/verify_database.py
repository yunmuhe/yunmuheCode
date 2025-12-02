"""
验证SQLite数据库
"""
import sqlite3
import sys
import io
from pathlib import Path

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

db_path = Path(__file__).parent / 'names_corpus.db'

if not db_path.exists():
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("SQLite数据库验证报告")
print("="*60)
print(f"\n数据库路径: {db_path}")
print(f"数据库大小: {db_path.stat().st_size / (1024*1024):.2f} MB\n")

# 查询各表的记录数
tables = [
    ('chinese_names', '中文人名'),
    ('ancient_names', '古代人名'),
    ('family_names', '姓氏'),
    ('idioms', '成语'),
    ('themed_names', '主题名字'),
    ('japanese_names', '日文人名'),
    ('english_names', '英文人名'),
    ('relationships', '称呼关系')
]

total = 0
print("各表统计:")
print("-"*60)
for table, name in tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        total += count
        print(f"{name:15s} : {count:>12,} 条")
    except Exception as e:
        print(f"{name:15s} : 错误 - {e}")

print("-"*60)
print(f"{'总计':15s} : {total:>12,} 条")

# 测试查询
print("\n"+"="*60)
print("测试查询:")
print("="*60)

# 1. 随机查询5个中文人名
print("\n1. 随机中文人名样例:")
cursor.execute('SELECT name, gender FROM chinese_names ORDER BY RANDOM() LIMIT 5')
for name, gender in cursor.fetchall():
    print(f"   {name} ({gender})")

# 2. 查询使用频率最高的5个中文姓氏
print("\n2. 使用频率最高的中文姓氏:")
cursor.execute('SELECT name, frequency FROM family_names WHERE origin="Chinese" ORDER BY frequency DESC LIMIT 5')
for name, freq in cursor.fetchall():
    print(f"   {name} (频率: {freq:,.0f})")

# 3. 随机查询3个成语
print("\n3. 随机成语样例:")
cursor.execute('SELECT idiom FROM idioms ORDER BY RANDOM() LIMIT 3')
for (idiom,) in cursor.fetchall():
    print(f"   {idiom}")

print("\n" + "="*60)
print("✓ 数据库验证完成!")
print("="*60)

conn.close()
