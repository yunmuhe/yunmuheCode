"""
一键整理所有数据
转换txt和xlsx为csv，并按类别分类存储
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_dependencies():
    """检查依赖"""
    try:
        import pandas
        import openpyxl
        return True
    except ImportError:
        print("=" * 70)
        print("❌ 缺少必要的库！")
        print("=" * 70)
        print("\n请安装依赖:")
        print("  pip install pandas openpyxl")
        print("\n或:")
        print("  pip install -r requirements.txt")
        print("\n" + "=" * 70)
        return False

if __name__ == '__main__':
    if not check_dependencies():
        sys.exit(1)
    
    from tools.data_organizer import main
    main()

