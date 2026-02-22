"""
动态模型发现功能测试脚本
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_get_all_models():
    """测试获取所有平台的模型列表"""
    print("\n=== 测试1: 获取所有平台的模型列表 ===")
    try:
        response = requests.get(f"{BASE_URL}/models")
        data = response.json()

        if data['success']:
            print(f"✅ 成功获取模型列表")
            print(f"   可用平台: {', '.join(data['platforms'])}")
            print(f"   模型总数: {data['total_count']}")

            for platform, models in data['models'].items():
                print(f"\n   {platform.upper()}:")
                for model in models[:3]:  # 只显示前3个
                    default_mark = " [默认]" if model.get('is_default') else ""
                    print(f"     - {model['name']}{default_mark}")
                if len(models) > 3:
                    print(f"     ... 还有 {len(models) - 3} 个模型")
            return True
        else:
            print(f"❌ 失败: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_get_platform_models(platform):
    """测试获取特定平台的模型列表"""
    print(f"\n=== 测试2: 获取 {platform} 平台的模型列表 ===")
    try:
        response = requests.get(f"{BASE_URL}/models?api={platform}")
        data = response.json()

        if data['success']:
            print(f"✅ 成功获取 {platform} 的 {data['count']} 个模型")
            for model in data['models']:
                default_mark = " [默认]" if model.get('is_default') else ""
                print(f"   - {model['id']}: {model['name']}{default_mark}")
                print(f"     {model['description']}")
            return True
        else:
            print(f"❌ 失败: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_generate_with_model(platform, model_id):
    """测试使用指定模型生成姓名"""
    print(f"\n=== 测试3: 使用 {platform}/{model_id} 生成姓名 ===")
    try:
        payload = {
            "description": "聪明可爱的女孩",
            "count": 3,
            "preferred_api": platform,
            "model": model_id
        }

        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()

        if data['success']:
            print(f"✅ 成功生成 {len(data['names'])} 个姓名")
            print(f"   使用API: {data.get('api_name', 'unknown')}")
            print(f"   使用模型: {data.get('model', 'unknown')}")
            print("\n   生成的姓名:")
            for name in data['names']:
                print(f"     - {name['name']}: {name['meaning']}")
            return True
        else:
            print(f"❌ 失败: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def test_cache_refresh():
    """测试缓存刷新功能"""
    print("\n=== 测试4: 测试缓存刷新 ===")
    try:
        # 第一次请求（可能从缓存）
        print("   第一次请求...")
        response1 = requests.get(f"{BASE_URL}/models?api=aliyun")

        # 强制刷新缓存
        print("   强制刷新缓存...")
        response2 = requests.get(f"{BASE_URL}/models?api=aliyun&refresh=true")

        if response1.json()['success'] and response2.json()['success']:
            print("✅ 缓存刷新功能正常")
            return True
        else:
            print("❌ 缓存刷新失败")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("动态模型发现功能测试")
    print("=" * 60)

    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器未运行，请先启动服务器")
            print("   运行: cd NameGenerationAgent && python main.py")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 无法连接到服务器: {str(e)}")
        print("   请确保服务器正在运行: http://127.0.0.1:5000")
        sys.exit(1)

    results = []

    # 测试1: 获取所有模型
    results.append(("获取所有模型", test_get_all_models()))

    # 测试2: 获取特定平台模型
    results.append(("获取阿里云模型", test_get_platform_models("aliyun")))

    # 测试3: 使用指定模型生成（如果有可用的API）
    # 注意：这个测试需要配置有效的API密钥
    # results.append(("使用指定模型生成", test_generate_with_model("aliyun", "qwen-turbo")))

    # 测试4: 缓存刷新
    results.append(("缓存刷新", test_cache_refresh()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
