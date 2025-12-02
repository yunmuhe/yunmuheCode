"""
CSV to SQLite Converter
将data/organized/目录下的所有CSV文件转换为SQLite数据库
"""
import sqlite3
import csv
import os
from pathlib import Path
import sys
import io

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_database_schema(conn):
    """创建数据库表结构"""
    cursor = conn.cursor()

    # 1. 中文人名表（带性别）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chinese_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            UNIQUE(name, gender)
        )
    ''')

    # 2. 古代人名表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ancient_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # 3. 姓氏表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            frequency REAL,
            origin TEXT
        )
    ''')

    # 4. 成语词典表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS idioms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idiom TEXT NOT NULL UNIQUE,
            category TEXT
        )
    ''')

    # 5. 主题名字表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS themed_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            theme TEXT NOT NULL,
            gender TEXT,
            UNIQUE(name, theme)
        )
    ''')

    # 6. 日文人名表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS japanese_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT
        )
    ''')

    # 7. 英文人名表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS english_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english_name TEXT,
            chinese_name TEXT,
            gender TEXT,
            UNIQUE(english_name, chinese_name)
        )
    ''')

    # 8. 称呼关系表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL UNIQUE,
            type TEXT
        )
    ''')

    # 创建索引以提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chinese_names_name ON chinese_names(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chinese_names_gender ON chinese_names(gender)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ancient_names_name ON ancient_names(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_family_names_name ON family_names(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_idioms_idiom ON idioms(idiom)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_themed_names_theme ON themed_names(theme)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_japanese_names_name ON japanese_names(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_english_names_chinese ON english_names(chinese_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_term ON relationships(term)')

    conn.commit()
    print("✓ 数据库表结构创建完成")


def import_chinese_names(conn, csv_path):
    """导入中文人名（带性别）"""
    cursor = conn.cursor()
    imported = 0

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        batch = []

        for row in reader:
            name = row.get('column_1') or row.get('dict', '').strip()
            gender = row.get('column_2') or row.get('sex', '').strip()

            if name and name != 'dict':
                batch.append((name, gender))

                if len(batch) >= 1000:
                    cursor.executemany(
                        'INSERT OR IGNORE INTO chinese_names (name, gender) VALUES (?, ?)',
                        batch
                    )
                    imported += len(batch)
                    batch = []
                    print(f"  已导入 {imported} 条中文人名...", end='\r')

        if batch:
            cursor.executemany(
                'INSERT OR IGNORE INTO chinese_names (name, gender) VALUES (?, ?)',
                batch
            )
            imported += len(batch)

    conn.commit()
    print(f"✓ 导入中文人名: {imported} 条                    ")


def import_ancient_names(conn, csv_path):
    """导入古代人名"""
    cursor = conn.cursor()
    imported = 0

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过表头

        batch = []
        for row in reader:
            if row and row[0].strip():
                batch.append((row[0].strip(),))

                if len(batch) >= 1000:
                    cursor.executemany(
                        'INSERT OR IGNORE INTO ancient_names (name) VALUES (?)',
                        batch
                    )
                    imported += len(batch)
                    batch = []
                    print(f"  已导入 {imported} 条古代人名...", end='\r')

        if batch:
            cursor.executemany(
                'INSERT OR IGNORE INTO ancient_names (name) VALUES (?)',
                batch
            )
            imported += len(batch)

    conn.commit()
    print(f"✓ 导入古代人名: {imported} 条                    ")


def import_family_names(conn, csv_path):
    """导入姓氏库"""
    cursor = conn.cursor()
    imported = 0

    origin = "Chinese"
    if "Japanese" in csv_path or "日本" in csv_path:
        origin = "Japanese"

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        batch = []
        for row in reader:
            # 尝试多种列名
            name = (row.get('NameB') or row.get('name') or row.get('姓氏') or
                   list(row.values())[0] if row else '').strip()

            # 尝试获取频率
            freq_str = (row.get('TF') or row.get('frequency') or row.get('频率') or
                       list(row.values())[1] if len(row.values()) > 1 else '').strip()

            try:
                frequency = float(freq_str) if freq_str and freq_str.replace('.', '').isdigit() else None
            except:
                frequency = None

            if name and name not in ('NameB', 'name', '姓氏'):
                batch.append((name, frequency, origin))

                if len(batch) >= 1000:
                    cursor.executemany(
                        'INSERT OR IGNORE INTO family_names (name, frequency, origin) VALUES (?, ?, ?)',
                        batch
                    )
                    imported += len(batch)
                    batch = []

        if batch:
            cursor.executemany(
                'INSERT OR IGNORE INTO family_names (name, frequency, origin) VALUES (?, ?, ?)',
                batch
            )
            imported += len(batch)

    conn.commit()
    print(f"✓ 导入{origin}姓氏: {imported} 条")


def import_idioms(conn, csv_path):
    """导入成语词典"""
    cursor = conn.cursor()
    imported = 0

    # 从文件名推断类别
    category = "通用"
    if "男孩" in csv_path:
        category = "男孩"
    elif "女孩" in csv_path:
        category = "女孩"

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过表头

        batch = []
        for row in reader:
            if row and row[0].strip():
                idiom = row[0].strip()
                if idiom and idiom != '成语':
                    batch.append((idiom, category))

                    if len(batch) >= 1000:
                        cursor.executemany(
                            'INSERT OR IGNORE INTO idioms (idiom, category) VALUES (?, ?)',
                            batch
                        )
                        imported += len(batch)
                        batch = []

        if batch:
            cursor.executemany(
                'INSERT OR IGNORE INTO idioms (idiom, category) VALUES (?, ?)',
                batch
            )
            imported += len(batch)

    conn.commit()
    print(f"✓ 导入成语词典({category}): {imported} 条")


def import_themed_names(conn, csv_path):
    """导入主题名字"""
    cursor = conn.cursor()
    imported = 0

    # 从文件名推断主题和性别
    filename = os.path.basename(csv_path)
    theme = "通用"
    gender = "随机"

    if "QQ网名" in filename:
        theme = "QQ网名"
    elif "春夏秋冬" in filename:
        theme = "春夏秋冬"
    elif "萌名通用" in filename:
        theme = "萌名通用"

    if "男孩" in filename:
        gender = "男"
    elif "女孩" in filename:
        gender = "女"
    elif "随机" in filename:
        gender = "随机"

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过表头

        batch = []
        for row in reader:
            if row and row[0].strip():
                name = row[0].strip()
                batch.append((name, theme, gender))

                if len(batch) >= 1000:
                    cursor.executemany(
                        'INSERT OR IGNORE INTO themed_names (name, theme, gender) VALUES (?, ?, ?)',
                        batch
                    )
                    imported += len(batch)
                    batch = []

        if batch:
            cursor.executemany(
                'INSERT OR IGNORE INTO themed_names (name, theme, gender) VALUES (?, ?, ?)',
                batch
            )
            imported += len(batch)

    conn.commit()
    print(f"✓ 导入主题名字({theme}-{gender}): {imported} 条")


def import_japanese_names(conn, csv_path):
    """导入日文人名"""
    cursor = conn.cursor()
    imported = 0

    name_type = "姓氏" if "姓氏" in csv_path else "全名"

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过表头

        batch = []
        for row in reader:
            if row and row[0].strip():
                name = row[0].strip()
                batch.append((name, name_type))

                if len(batch) >= 1000:
                    cursor.executemany(
                        'INSERT OR IGNORE INTO japanese_names (name, type) VALUES (?, ?)',
                        batch
                    )
                    imported += len(batch)
                    batch = []

        if batch:
            cursor.executemany(
                'INSERT OR IGNORE INTO japanese_names (name, type) VALUES (?, ?)',
                batch
            )
            imported += len(batch)

    conn.commit()
    print(f"✓ 导入日文人名({name_type}): {imported} 条")


def import_english_names(conn, csv_path):
    """导入英文人名"""
    cursor = conn.cursor()
    imported = 0

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        # 读取第一行判断格式
        first_line = f.readline().strip()
        f.seek(0)  # 重置文件指针

        # 如果包含'|'分隔符，使用特殊处理
        if '|' in first_line:
            reader = csv.reader(f, delimiter='\n')
            next(reader, None)  # 跳过表头

            batch = []
            for row in reader:
                if not row or not row[0].strip():
                    continue

                line = row[0].strip()
                if '|' not in line:
                    continue

                parts = line.split('|')
                if len(parts) >= 2:
                    chinese = parts[0].strip()
                    english = parts[1].strip()
                    gender = parts[2].strip() if len(parts) > 2 else ''

                    if chinese or english:
                        batch.append((english, chinese, gender))

                        if len(batch) >= 1000:
                            cursor.executemany(
                                'INSERT OR IGNORE INTO english_names (english_name, chinese_name, gender) VALUES (?, ?, ?)',
                                batch
                            )
                            imported += len(batch)
                            batch = []
                            print(f"  已导入 {imported} 条英文人名...", end='\r')

            if batch:
                cursor.executemany(
                    'INSERT OR IGNORE INTO english_names (english_name, chinese_name, gender) VALUES (?, ?, ?)',
                    batch
                )
                imported += len(batch)
        else:
            # 使用DictReader处理标准CSV格式
            reader = csv.DictReader(f)

            batch = []
            for row in reader:
                english = (row.get('English') or row.get('english') or row.get('英文名') or '').strip()
                chinese = (row.get('Chinese') or row.get('chinese') or row.get('中文名') or '').strip()
                gender = (row.get('Sex') or row.get('gender') or row.get('性别') or '').strip()

                if english or chinese:
                    batch.append((english, chinese, gender))

                    if len(batch) >= 1000:
                        cursor.executemany(
                            'INSERT OR IGNORE INTO english_names (english_name, chinese_name, gender) VALUES (?, ?, ?)',
                            batch
                        )
                        imported += len(batch)
                        batch = []
                        print(f"  已导入 {imported} 条英文人名...", end='\r')

            if batch:
                cursor.executemany(
                    'INSERT OR IGNORE INTO english_names (english_name, chinese_name, gender) VALUES (?, ?, ?)',
                    batch
                )
                imported += len(batch)

    conn.commit()
    print(f"✓ 导入英文人名: {imported} 条                    ")


def import_relationships(conn, csv_path):
    """导入称呼关系"""
    cursor = conn.cursor()
    imported = 0

    rel_type = "称呼" if "称呼" in csv_path else "词根"

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过表头

        batch = []
        for row in reader:
            if row and row[0].strip():
                term = row[0].strip()
                batch.append((term, rel_type))

                if len(batch) >= 1000:
                    cursor.executemany(
                        'INSERT OR IGNORE INTO relationships (term, type) VALUES (?, ?)',
                        batch
                    )
                    imported += len(batch)
                    batch = []

        if batch:
            cursor.executemany(
                'INSERT OR IGNORE INTO relationships (term, type) VALUES (?, ?)',
                batch
            )
            imported += len(batch)

    conn.commit()
    print(f"✓ 导入称呼关系({rel_type}): {imported} 条")


def main():
    """主函数"""
    # 数据库路径
    db_path = Path(__file__).parent / 'names_corpus.db'
    organized_path = Path(__file__).parent / 'organized'

    # 删除旧数据库
    if db_path.exists():
        print(f"删除旧数据库: {db_path}")
        os.remove(db_path)

    print(f"\n开始转换CSV到SQLite数据库: {db_path}\n")

    # 连接数据库
    conn = sqlite3.connect(db_path)

    try:
        # 创建表结构
        create_database_schema(conn)
        print()

        # 导入各类数据
        print("开始导入数据...\n")

        # 1. 中文人名
        chinese_names_files = [
            organized_path / '中文人名' / 'Chinese_Names_Corpus_Gender（120W）.csv',
            organized_path / '中文人名' / 'Chinese_Names_Corpus（120W）.csv'
        ]
        for f in chinese_names_files:
            if f.exists():
                import_chinese_names(conn, str(f))

        # 2. 古代人名
        ancient_file = organized_path / '古代人名' / 'Ancient_Names_Corpus（25W）.csv'
        if ancient_file.exists():
            import_ancient_names(conn, str(ancient_file))

        # 3. 姓氏库
        family_names_dir = organized_path / '姓氏库'
        if family_names_dir.exists():
            for f in family_names_dir.glob('*.csv'):
                import_family_names(conn, str(f))

        # 4. 成语词典
        idioms_dir = organized_path / '成语词典'
        if idioms_dir.exists():
            for f in idioms_dir.glob('*.csv'):
                if '关于' not in f.name:  # 跳过关于文件
                    import_idioms(conn, str(f))

        # 5. 主题名字
        themed_dir = organized_path / '主题名字'
        if themed_dir.exists():
            for f in themed_dir.glob('*.csv'):
                if '关于' not in f.name:  # 跳过关于文件
                    import_themed_names(conn, str(f))

        # 6. 日文人名
        japanese_dir = organized_path / '日文人名'
        if japanese_dir.exists():
            for f in japanese_dir.glob('*.csv'):
                import_japanese_names(conn, str(f))

        # 7. 英文人名
        english_dir = organized_path / '英文人名'
        if english_dir.exists():
            for f in english_dir.glob('*.csv'):
                import_english_names(conn, str(f))

        # 8. 称呼关系
        relationship_dir = organized_path / '称呼关系'
        if relationship_dir.exists():
            for f in relationship_dir.glob('*.csv'):
                import_relationships(conn, str(f))

        # 显示统计信息
        print("\n" + "="*50)
        print("数据库统计信息:")
        print("="*50)

        cursor = conn.cursor()
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

        total_records = 0
        for table, name in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            total_records += count
            print(f"{name:12s}: {count:>10,} 条")

        print("="*50)
        print(f"{'总计':12s}: {total_records:>10,} 条")
        print("="*50)

        # 获取数据库大小
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print(f"\n数据库文件大小: {db_size:.2f} MB")
        print(f"数据库路径: {db_path}")

        print("\n✓ CSV转SQLite转换完成！")

    except Exception as e:
        print(f"\n✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
