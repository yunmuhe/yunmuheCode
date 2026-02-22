"""
Locust性能测试脚本
用于测试智能姓名生成系统在高并发下的性能表现

使用方法：
1. 安装Locust: pip install locust
2. 启动后端服务: python main.py
3. 运行测试:
   - Web界面模式: locust -f tests/locustfile.py --host=http://127.0.0.1:5000
   - 命令行模式: locust -f tests/locustfile.py --host=http://127.0.0.1:5000 --headless -u 10 -r 2 -t 60s
"""

import random
import time
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner

# ==================== 测试数据配置 ====================

# 角色描述模板
DESCRIPTIONS = [
    "一位勇敢的战士，身经百战，意志坚定",
    "温柔善良的少女，心地纯洁，乐于助人",
    "睿智的老者，饱经沧桑，见多识广",
    "聪明伶俐的孩童，活泼可爱，天真烂漫",
    "冷酷的刺客，身手敏捷，来无影去无踪",
    "优雅的贵族小姐，知书达理，气质高贵",
    "豪爽的江湖侠客，仗义疏财，行侠仗义",
    "神秘的法师，精通魔法，洞察未来",
    "忠诚的骑士，守护正义，从不退缩",
    "美丽的精灵公主，与自然为伴，善解人意",
    "沉稳的将军，运筹帷幄，决胜千里",
    "活泼的少年，热血沸腾，追逐梦想",
    "沉默寡言的剑客，剑法高超，快如闪电",
    "博学的书生，才华横溢，出口成章",
    "坚毅的女将军，英姿飒爽，巾帼不让须眉",
]

# 文化风格选项
CULTURAL_STYLES = [
    "chinese_modern",
    "chinese_traditional",
    "fantasy",
    "western",
    "japanese"
]

# 性别选项
GENDERS = ["male", "female", "neutral"]

# 年龄选项
AGES = ["child", "teen", "adult", "elder"]


# ==================== 测试统计 ====================

class TestStats:
    """测试统计信息收集"""

    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.api_usage = {}
        self.response_times = []

    def record_success(self, api_name: str, response_time: float):
        self.success_count += 1
        self.api_usage[api_name] = self.api_usage.get(api_name, 0) + 1
        self.response_times.append(response_time)

    def record_failure(self):
        self.failure_count += 1

    def get_summary(self):
        avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        return {
            "total_requests": self.success_count + self.failure_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_count / (self.success_count + self.failure_count) * 100 if (self.success_count + self.failure_count) > 0 else 0,
            "avg_response_time": round(avg_time, 2),
            "api_usage": self.api_usage
        }

# 全局统计实例
test_stats = TestStats()


# ==================== 用户行为定义 ====================

class NameGeneratorUser(HttpUser):
    """
    模拟用户行为的类

    wait_time: 用户请求之间的等待时间（1-3秒随机）
    """
    wait_time = between(1, 3)

    def on_start(self):
        """用户启动时执行"""
        # 先进行健康检查，确保服务可用
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"[用户启动] 服务健康检查通过")
            else:
                response.failure(f"健康检查失败: {response.status_code}")

    @task(10)
    def generate_names_random(self):
        """
        任务：随机参数生成姓名（权重10，最常执行）
        """
        payload = {
            "description": random.choice(DESCRIPTIONS),
            "count": random.randint(3, 8),
            "cultural_style": random.choice(CULTURAL_STYLES),
            "gender": random.choice(GENDERS),
            "age": random.choice(AGES),
            "use_cache": True
        }

        self._send_generate_request(payload, "随机参数生成")

    @task(5)
    def generate_names_chinese_modern(self):
        """
        任务：中国现代风格生成（权重5）
        """
        payload = {
            "description": random.choice(DESCRIPTIONS),
            "count": 5,
            "cultural_style": "chinese_modern",
            "gender": random.choice(GENDERS),
            "age": "adult",
            "use_cache": True
        }

        self._send_generate_request(payload, "中国现代风格")

    @task(3)
    def generate_names_chinese_traditional(self):
        """
        任务：中国传统风格生成（权重3）
        """
        payload = {
            "description": random.choice(DESCRIPTIONS),
            "count": 5,
            "cultural_style": "chinese_traditional",
            "gender": random.choice(GENDERS),
            "age": random.choice(AGES),
            "use_cache": True
        }

        self._send_generate_request(payload, "中国传统风格")

    @task(2)
    def generate_names_fantasy(self):
        """
        任务：奇幻风格生成（权重2）
        """
        payload = {
            "description": random.choice(DESCRIPTIONS),
            "count": random.randint(5, 10),
            "cultural_style": "fantasy",
            "gender": random.choice(GENDERS),
            "age": random.choice(AGES),
            "use_cache": True
        }

        self._send_generate_request(payload, "奇幻风格")

    @task(2)
    def generate_names_no_cache(self):
        """
        任务：禁用缓存的请求（权重2，测试无缓存性能）
        """
        payload = {
            "description": f"{random.choice(DESCRIPTIONS)}_{time.time()}",  # 添加时间戳确保不命中缓存
            "count": 3,
            "cultural_style": random.choice(CULTURAL_STYLES),
            "gender": random.choice(GENDERS),
            "age": random.choice(AGES),
            "use_cache": False
        }

        self._send_generate_request(payload, "无缓存请求")

    @task(1)
    def generate_names_large_count(self):
        """
        任务：大量姓名生成（权重1，测试极限）
        """
        payload = {
            "description": random.choice(DESCRIPTIONS),
            "count": 20,  # 最大数量
            "cultural_style": random.choice(CULTURAL_STYLES),
            "gender": random.choice(GENDERS),
            "age": random.choice(AGES),
            "use_cache": True
        }

        self._send_generate_request(payload, "大量生成")

    @task(3)
    def get_options(self):
        """
        任务：获取可用选项（权重3，轻量请求）
        """
        with self.client.get("/options", catch_response=True, name="/options") as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("获取选项失败")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def get_stats(self):
        """
        任务：获取系统统计（权重2，轻量请求）
        """
        with self.client.get("/stats", catch_response=True, name="/stats") as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("获取统计失败")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def health_check(self):
        """
        任务：健康检查（权重2，轻量请求）
        """
        with self.client.get("/health", catch_response=True, name="/health") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    def _send_generate_request(self, payload: dict, task_name: str):
        """
        发送生成请求的通用方法

        Args:
            payload: 请求数据
            task_name: 任务名称（用于日志）
        """
        start_time = time.time()

        with self.client.post(
            "/generate",
            json=payload,
            catch_response=True,
            name="/generate",
            timeout=120  # 设置较长超时，因为AI生成可能较慢
        ) as response:

            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        names_count = len(data.get("names", []))
                        api_name = data.get("api_name", "unknown")

                        # 记录统计
                        test_stats.record_success(api_name, elapsed_time)

                        response.success()

                        # 调试输出（可选）
                        # print(f"[{task_name}] 成功生成 {names_count} 个姓名，API: {api_name}，耗时: {elapsed_time:.2f}s")
                    else:
                        error_msg = data.get("error", "未知错误")
                        test_stats.record_failure()
                        response.failure(f"业务失败: {error_msg}")
                except Exception as e:
                    test_stats.record_failure()
                    response.failure(f"解析响应失败: {str(e)}")
            else:
                test_stats.record_failure()
                response.failure(f"HTTP {response.status_code}")


class QuickTestUser(HttpUser):
    """
    快速测试用户类（仅测试轻量接口）
    用于快速验证系统可用性
    """
    wait_time = between(0.5, 1)

    @task(5)
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def get_options(self):
        self.client.get("/options")

    @task(2)
    def get_stats(self):
        self.client.get("/stats")


class HeavyLoadUser(HttpUser):
    """
    重负载测试用户类
    专门测试生成接口的极限性能
    """
    wait_time = between(0.5, 1.5)

    @task
    def generate_continuous(self):
        """持续发送生成请求"""
        payload = {
            "description": random.choice(DESCRIPTIONS),
            "count": random.randint(5, 10),
            "cultural_style": random.choice(CULTURAL_STYLES),
            "gender": random.choice(GENDERS),
            "age": random.choice(AGES),
            "use_cache": random.choice([True, False])
        }

        with self.client.post(
            "/generate",
            json=payload,
            catch_response=True,
            timeout=120
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(data.get("error", "失败"))
            else:
                response.failure(f"HTTP {response.status_code}")


# ==================== 事件处理 ====================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时执行"""
    print("=" * 60)
    print("智能姓名生成系统 - Locust性能测试开始")
    print("=" * 60)
    print(f"目标主机: {environment.host}")
    print(f"用户数: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("=" * 60)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时执行"""
    print("\n" + "=" * 60)
    print("测试结束 - 自定义统计信息")
    print("=" * 60)
    summary = test_stats.get_summary()
    print(f"总请求数: {summary['total_requests']}")
    print(f"成功数: {summary['success_count']}")
    print(f"失败数: {summary['failure_count']}")
    print(f"成功率: {summary['success_rate']:.2f}%")
    print(f"平均响应时间: {summary['avg_response_time']}s")
    print(f"API使用分布: {summary['api_usage']}")
    print("=" * 60)

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """每个请求完成时执行（可用于详细日志）"""
    # 可以在这里添加更详细的日志记录
    pass


# ==================== 命令行入口 ====================

if __name__ == "__main__":
    import os
    import sys

    print("""
╔══════════════════════════════════════════════════════════════╗
║         智能姓名生成系统 - Locust性能测试工具                  ║
╠══════════════════════════════════════════════════════════════╣
║  使用方法:                                                    ║
║                                                              ║
║  1. Web界面模式（推荐）:                                       ║
║     locust -f tests/locustfile.py --host=http://127.0.0.1:5000║
║     然后访问 http://localhost:8089 配置并启动测试              ║
║                                                              ║
║  2. 命令行模式（无界面）:                                      ║
║     locust -f tests/locustfile.py --host=http://127.0.0.1:5000 \\
║            --headless -u 10 -r 2 -t 60s                       ║
║                                                              ║
║  参数说明:                                                    ║
║     -u: 并发用户数                                            ║
║     -r: 每秒启动用户数（爬坡速率）                             ║
║     -t: 测试持续时间                                          ║
║                                                              ║
║  3. 指定用户类:                                               ║
║     locust -f tests/locustfile.py --class-picker             ║
║     （可在Web界面选择不同的用户类）                            ║
║                                                              ║
║  4. 快速测试（仅轻量接口）:                                    ║
║     locust -f tests/locustfile.py QuickTestUser              ║
║                                                              ║
║  5. 重负载测试:                                               ║
║     locust -f tests/locustfile.py HeavyLoadUser              ║
╚══════════════════════════════════════════════════════════════╝
    """)
