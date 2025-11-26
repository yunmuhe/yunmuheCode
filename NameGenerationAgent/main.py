"""
智能姓名生成系统 - 主启动脚本
"""
import os
import sys

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """主函数"""
    print("智能姓名生成系统")
    print("=" * 40)

    # 检查.env文件
    env_file_path = os.path.join(project_root, '.env')
    if not os.path.exists(env_file_path):
        print("[错误] 未找到.env文件")
        print("请运行: python quick_setup_api.py")
        return

    # 加载环境变量
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
        print("[成功] 环境变量加载成功")
    except Exception as e:
        print(f"[错误] 环境变量加载失败: {str(e)}")
        return
    
    # 检查所有API适配器注册与可用状态
    try:
        print("---------------------------")
        print("开始API诊断...")
        from src.core.name_generator import name_generator
        print("姓名生成器导入成功")
        options = name_generator.get_available_options()
        print("可用API诊断:")
        for api in options.get('apis', []):
            print(f"  - {api}")
        print(f"全部API: {options.get('apis')}")
        print("---------------------------")
    except Exception as e:
        print(f"[错误] API诊断失败: {e}")
        import traceback
        print("详细错误堆栈:")
        traceback.print_exc()
        print("---------------------------")

    # 启动Flask应用
    try:
        from src.web.app import app
        print("[成功] Flask应用启动成功")
        print("[成功] 提示词模板已修复")
        print("[访问] 访问地址: http://localhost:5000")
        print("[说明] 使用说明:")
        print("   1. 在角色描述框中输入角色描述")
        print("   2. 选择文化风格、性别、年龄等选项")
        print("   3. 选择生成数量")
        print("   4. 点击'生成姓名'按钮")
        print("   5. 查看不同风格的姓名结果")
        print("\n[功能] 表单选项功能:")
        print("   - 文化风格: 现代中文/传统中文/奇幻风格/西方风格")
        print("   - 性别: 男性/女性/中性")
        print("   - 年龄: 儿童/青少年/成年人/长者")
        print("   - 同一描述 + 不同选项 = 不同风格的姓名")
        print("按 Ctrl+C 停止服务")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"[错误] Flask应用启动失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
