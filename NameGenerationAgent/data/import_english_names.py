"""
单独导入英文人名到现有数据库
"""
import sqlite3
import csv
import sys
import io
from pathlib import Path

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def import_english_names(conn, csv_path):
    """导入英文人名"""
    cursor = conn.cursor()
    imported = 0

    print(f"正在导入: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

        print(f"  文件总行数: {len(lines)}")

        # 显示前3行用于调试
        print(f"  前3行预览:")
        for i, line in enumerate(lines[:3]):
            print(f"    第{i+1}行: {repr(line[:50])}")

        # 跳过表头（检查第一行是否为表头）
        start_line = 0
        if lines:
            first_line = lines[0].strip()
            if '姓名' in first_line or 'English' in first_line or first_line == '姓名':
                start_line = 1
                print(f"  检测到表头，从第2行开始处理")

        batch = []
        skipped = 0
        for idx, line in enumerate(lines[start_line:], start=start_line+1):
            line = line.strip()

            # 跳过空行
            if not line:
                continue

            # 检查是否包含分隔符
            if '|' not in line:
                skipped += 1
                if skipped <= 5:  # 只显示前5个跳过的行
                    print(f"  警告: 第{idx}行没有'|'分隔符: {repr(line[:50])}")
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

    conn.commit()
    print(f"\n✓ 导入英文人名完成: {imported} 条")
    if skipped > 0:
        print(f"  跳过 {skipped} 行（无分隔符或格式错误）")
    return imported


def main():
    db_path = Path(__file__).parent / 'names_corpus.db'

    if not db_path.exists():
        print(f"错误: 数据库文件不存在: {db_path}")
        print("请先运行 convert_csv_to_sqlite.py 创建数据库")
        return

    print(f"连接数据库: {db_path}\n")
    conn = sqlite3.connect(db_path)

    try:
        # 清空现有英文人名数据
        cursor = conn.cursor()
        cursor.execute('DELETE FROM english_names')
        conn.commit()
        print("已清空现有英文人名数据\n")

        # 导入所有英文人名CSV文件
        english_dir = Path(__file__).parent / 'organized' / '英文人名'

        if not english_dir.exists():
            print(f"错误: 目录不存在: {english_dir}")
            return

        csv_files = list(english_dir.glob('*.csv'))

        if not csv_files:
            print(f"错误: 未找到CSV文件在: {english_dir}")
            return

        total = 0
        for csv_file in csv_files:
            print(f"\n处理文件: {csv_file.name}")
            count = import_english_names(conn, str(csv_file))
            total += count

        # 显示统计
        print("\n" + "="*60)
        cursor.execute('SELECT COUNT(*) FROM english_names')
        final_count = cursor.fetchone()[0]
        print(f"最终英文人名数量: {final_count:,} 条")

        # 显示示例
        print("\n示例数据:")
        cursor.execute('SELECT chinese_name, english_name, gender FROM english_names LIMIT 5')
        for cn, en, gender in cursor.fetchall():
            print(f"  {cn} | {en} | {gender}")

        print("="*60)
        print("\n✓ 英文人名导入完成!")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
