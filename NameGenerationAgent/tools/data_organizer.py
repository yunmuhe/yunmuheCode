"""
数据整理和转换工具
将所有txt和xlsx文件转换为csv格式，并按类别分类存储
"""
import os
import shutil
import pandas as pd
from pathlib import Path

class DataOrganizer:
    """数据整理器"""
    
    def __init__(self, corpus_path: str = None):
        """
        初始化整理器
        
        Args:
            corpus_path: 语料库根目录
        """
        if corpus_path is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            corpus_path = os.path.join(os.path.dirname(project_root), 'Chinese-Names-Corpus-master')
        
        self.corpus_path = corpus_path
        
        # 输出根目录
        self.output_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'organized'
        )
        
        # 创建分类目录
        self.categories = {
            'chinese_names': os.path.join(self.output_root, '中文人名'),
            'ancient_names': os.path.join(self.output_root, '古代人名'),
            'surnames': os.path.join(self.output_root, '姓氏库'),
            'japanese_names': os.path.join(self.output_root, '日文人名'),
            'english_names': os.path.join(self.output_root, '英文人名'),
            'chengyu': os.path.join(self.output_root, '成语词典'),
            'relationships': os.path.join(self.output_root, '称呼关系'),
            'poetic_names': os.path.join(self.output_root, '诗词名字'),
            'themed_names': os.path.join(self.output_root, '主题名字'),
            'other': os.path.join(self.output_root, '其他数据'),
        }
        
        # 创建所有目录
        for category_path in self.categories.values():
            os.makedirs(category_path, exist_ok=True)
    
    def organize_all(self):
        """整理所有数据"""
        print("=" * 70)
        print("数据整理和转换工具")
        print("=" * 70)
        print("\n将执行以下操作:")
        print("  1. 转换所有txt文件为csv格式")
        print("  2. 转换所有xlsx文件为csv格式")
        print("  3. 按类别分类存储")
        print("  4. 生成数据目录清单")
        print("\n分类目录:")
        for name, path in self.categories.items():
            print(f"  - {os.path.basename(path)}")
        
        print("\n" + "-" * 70)
        
        # 1. 转换txt文件
        print("\n[1/4] 转换txt文件...")
        self.convert_txt_files()
        
        # 2. 转换xlsx文件
        print("\n[2/4] 转换xlsx文件...")
        self.convert_xlsx_files()
        
        # 3. 分类整理
        print("\n[3/4] 分类整理文件...")
        self.classify_files()
        
        # 4. 生成目录清单
        print("\n[4/4] 生成数据目录...")
        self.generate_catalog()
        
        print("\n" + "=" * 70)
        print("✅ 数据整理完成！")
        print(f"📁 输出目录: {self.output_root}")
        print("=" * 70)
    
    def convert_txt_files(self):
        """转换所有txt文件为csv格式"""
        txt_files = []
        
        # 查找所有txt文件
        for root, dirs, files in os.walk(self.corpus_path):
            for file in files:
                if file.endswith('.txt') and not file.startswith('.'):
                    txt_files.append(os.path.join(root, file))
        
        print(f"   找到 {len(txt_files)} 个txt文件")
        
        converted_count = 0
        for txt_file in txt_files:
            try:
                self._convert_txt_to_csv(txt_file)
                converted_count += 1
            except Exception as e:
                print(f"   ❌ 转换失败: {os.path.basename(txt_file)} - {str(e)}")
        
        print(f"   ✅ 成功转换 {converted_count}/{len(txt_files)} 个文件")
    
    def _convert_txt_to_csv(self, txt_file: str):
        """
        转换单个txt文件为csv
        
        Args:
            txt_file: txt文件路径
        """
        base_name = os.path.splitext(os.path.basename(txt_file))[0]
        
        # 读取txt文件
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # 判断是否包含逗号分隔的数据
        if lines and ',' in lines[0]:
            # 已经是CSV格式，检查是否有标题行
            if lines[0].lower().startswith('dict') or '姓名' in lines[0] or 'name' in lines[0].lower():
                # 有标题行
                header = lines[0].split(',')
                data = [line.split(',') for line in lines[1:]]
            else:
                # 没有标题行，添加默认标题
                header = ['column_' + str(i+1) for i in range(len(lines[0].split(',')))]
                data = [line.split(',') for line in lines]
            
            df = pd.DataFrame(data, columns=header)
        else:
            # 单列数据
            # 根据文件名判断列名
            if '人名' in base_name or 'Names' in base_name or 'name' in base_name.lower():
                column_name = '姓名'
            elif '成语' in base_name or 'ChengYu' in base_name:
                column_name = '成语'
            else:
                column_name = '内容'
            
            df = pd.DataFrame(lines, columns=[column_name])
        
        # 确定输出路径（临时存储）
        temp_dir = os.path.join(self.output_root, '_temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        output_file = os.path.join(temp_dir, f"{base_name}.csv")
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"   ✅ {base_name}: {len(df)} 行")
    
    def convert_xlsx_files(self):
        """转换所有xlsx文件为csv格式"""
        xlsx_files = []
        
        # 查找所有xlsx文件
        for root, dirs, files in os.walk(self.corpus_path):
            for file in files:
                if file.endswith('.xlsx') and not file.startswith('~'):
                    xlsx_files.append(os.path.join(root, file))
        
        print(f"   找到 {len(xlsx_files)} 个xlsx文件")
        
        converted_count = 0
        for xlsx_file in xlsx_files:
            try:
                self._convert_xlsx_to_csv(xlsx_file)
                converted_count += 1
            except Exception as e:
                print(f"   ❌ 转换失败: {os.path.basename(xlsx_file)} - {str(e)}")
        
        print(f"   ✅ 成功转换 {converted_count}/{len(xlsx_files)} 个文件")
    
    def _convert_xlsx_to_csv(self, xlsx_file: str):
        """转换xlsx文件为csv"""
        base_name = os.path.splitext(os.path.basename(xlsx_file))[0]
        
        # 读取所有sheet
        excel_data = pd.read_excel(xlsx_file, sheet_name=None, engine='openpyxl')
        
        temp_dir = os.path.join(self.output_root, '_temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 如果有多个sheet
        if len(excel_data) > 1:
            for sheet_name, df in excel_data.items():
                output_file = os.path.join(temp_dir, f"{base_name}_{sheet_name}.csv")
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
        else:
            sheet_name = list(excel_data.keys())[0]
            df = excel_data[sheet_name]
            output_file = os.path.join(temp_dir, f"{base_name}.csv")
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    def classify_files(self):
        """分类整理文件"""
        temp_dir = os.path.join(self.output_root, '_temp')
        
        if not os.path.exists(temp_dir):
            print("   ⚠️  没有找到临时文件")
            return
        
        csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
        print(f"   整理 {len(csv_files)} 个csv文件")
        
        classified = {key: [] for key in self.categories.keys()}
        
        for csv_file in csv_files:
            category = self._determine_category(csv_file)
            source_path = os.path.join(temp_dir, csv_file)
            dest_path = os.path.join(self.categories[category], csv_file)
            
            # 复制文件到分类目录
            shutil.copy2(source_path, dest_path)
            classified[category].append(csv_file)
        
        # 显示分类结果
        for category, files in classified.items():
            if files:
                category_name = os.path.basename(self.categories[category])
                print(f"   📁 {category_name}: {len(files)} 个文件")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print("   ✅ 分类完成")
    
    def _determine_category(self, filename: str) -> str:
        """
        根据文件名确定分类
        
        Args:
            filename: 文件名
            
        Returns:
            分类键
        """
        filename_lower = filename.lower()
        
        # 中文人名
        if 'chinese_names_corpus_gender' in filename_lower or '中文人名' in filename:
            if 'gender' in filename_lower or '性别' in filename:
                return 'chinese_names'
        
        if 'chinese_names_corpus' in filename_lower and 'gender' not in filename_lower:
            return 'chinese_names'
        
        # 古代人名
        if 'ancient' in filename_lower or '古代' in filename:
            return 'ancient_names'
        
        # 姓氏
        if 'family_name' in filename_lower or 'surname' in filename_lower or '姓氏' in filename or '姓' in filename:
            return 'surnames'
        
        # 日文人名
        if 'japanese' in filename_lower or '日文' in filename or '日本' in filename:
            return 'japanese_names'
        
        # 英文人名
        if 'english' in filename_lower or '英文' in filename or '英语' in filename:
            return 'english_names'
        
        # 成语
        if 'chengyu' in filename_lower or '成语' in filename:
            return 'chengyu'
        
        # 称呼关系
        if 'relationship' in filename_lower or '称呼' in filename or '关系' in filename:
            return 'relationships'
        
        # 诗词名字
        if '诗词' in filename or '成语取名' in filename:
            return 'poetic_names'
        
        # 主题名字
        if '萌名' in filename or '春夏秋冬' in filename or 'qq网名' in filename_lower or '主题' in filename:
            return 'themed_names'
        
        # 其他
        return 'other'
    
    def generate_catalog(self):
        """生成数据目录清单"""
        catalog = []
        catalog.append("=" * 70)
        catalog.append("数据目录清单")
        catalog.append("=" * 70)
        catalog.append("")
        
        total_files = 0
        total_rows = 0
        
        for category_key, category_path in self.categories.items():
            category_name = os.path.basename(category_path)
            csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
            
            if not csv_files:
                continue
            
            catalog.append(f"\n【{category_name}】")
            catalog.append("-" * 70)
            
            category_rows = 0
            for csv_file in sorted(csv_files):
                file_path = os.path.join(category_path, csv_file)
                try:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    rows = len(df)
                    cols = len(df.columns)
                    category_rows += rows
                    catalog.append(f"  ✅ {csv_file}")
                    catalog.append(f"     行数: {rows:,} | 列数: {cols} | 列名: {', '.join(df.columns[:5])}")
                except Exception as e:
                    catalog.append(f"  ❌ {csv_file} - 读取失败")
            
            catalog.append(f"\n  小计: {len(csv_files)} 个文件, {category_rows:,} 行数据")
            total_files += len(csv_files)
            total_rows += category_rows
        
        catalog.append("")
        catalog.append("=" * 70)
        catalog.append(f"总计: {total_files} 个文件, {total_rows:,} 行数据")
        catalog.append("=" * 70)
        
        # 保存目录清单
        catalog_file = os.path.join(self.output_root, 'DATA_CATALOG.txt')
        with open(catalog_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(catalog))
        
        # 打印到控制台
        print('\n'.join(catalog[-10:]))  # 只打印最后10行
        print(f"\n   📄 完整目录已保存: DATA_CATALOG.txt")
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        stats = {}
        
        for category_key, category_path in self.categories.items():
            category_name = os.path.basename(category_path)
            csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
            
            if csv_files:
                total_rows = 0
                for csv_file in csv_files:
                    file_path = os.path.join(category_path, csv_file)
                    try:
                        df = pd.read_csv(file_path, encoding='utf-8-sig')
                        total_rows += len(df)
                    except:
                        pass
                
                stats[category_name] = {
                    'files': len(csv_files),
                    'rows': total_rows
                }
        
        return stats


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                 数据整理和转换工具                                 ║
║          Data Organization and Conversion Tool                    ║
╚══════════════════════════════════════════════════════════════════╝

功能说明:
  • 转换所有txt文件为csv格式
  • 转换所有xlsx文件为csv格式
  • 按类别分类存储数据
  • 生成数据目录清单

分类目录:
  📁 中文人名 - 现代中文人名数据
  📁 古代人名 - 古代人名数据
  📁 姓氏库 - 中文姓氏数据
  📁 日文人名 - 日文姓名数据
  📁 英文人名 - 英文姓名数据
  📁 成语词典 - 成语数据
  📁 称呼关系 - 称呼关系数据
  📁 诗词名字 - 诗词成语风格名字
  📁 主题名字 - 季节、网名等主题名字
  📁 其他数据 - 未分类数据

══════════════════════════════════════════════════════════════════
    """)
    
    # 检查依赖
    try:
        import pandas
        import openpyxl
    except ImportError:
        print("❌ 缺少必要的库！")
        print("\n请安装依赖:")
        print("  pip install pandas openpyxl")
        return
    
    organizer = DataOrganizer()
    
    response = input("是否开始整理？(y/n): ").strip().lower()
    
    if response == 'y':
        print("\n开始整理...\n")
        organizer.organize_all()
        
        # 显示统计
        stats = organizer.get_statistics()
        print("\n" + "=" * 70)
        print("📊 数据统计:")
        for category, data in stats.items():
            print(f"  {category}: {data['files']} 个文件, {data['rows']:,} 行数据")
        
        print("\n✨ 所有数据已整理完成！")
        print(f"📁 数据目录: {organizer.output_root}")
        print("\n使用方法:")
        print("  1. 查看完整目录: cat data/organized/DATA_CATALOG.txt")
        print("  2. 浏览分类数据: ls data/organized/*/")
        print("  3. 加载数据: pandas.read_csv('data/organized/中文人名/xxx.csv')")
        print("\n" + "=" * 70)
    else:
        print("\n已取消整理。")


if __name__ == '__main__':
    main()

