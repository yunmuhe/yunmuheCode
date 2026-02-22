"""
缓存效果对比性能测试脚本
用于论文中对比启用缓存与禁用缓存场景下的性能差异

使用方法：
1. 禁用缓存测试：
   locust -f tests/locustfile_cache_comparison.py CacheDisabledUser --host=http://127.0.0.1:5000 --headless -u 10 -r 2 -t 60s

2. 启用缓存测试（使用相同描述以命中缓存）：
   locust -f tests/locustfile_cache_comparison.py CacheEnabledUser --host=http://127.0.0.1:5000 --headless -u 10 -r 2 -t 60s
"""

import random
import time
from locust import HttpUser, task, between, events

# ==================== 固定测试数据（用于缓存命中） ====================

# 固定的角色描述（用于缓存命中测试）
FIXED_DESCRIPTIONS = [
    "一位勇敢的战士",
    "温柔善良的少女",
    "睿智的老者",
    "聪明伶俐的孩童",
    "冷酷的刺客",
]

# 随机角色描述（用于缓存未命中测试）
RANDOM_DESCRIPTIONS = [
    "身经百战意志坚定的勇士",
    "心地纯洁乐于助人的姑娘",
    "饱经沧桑见多识广的智者",
    "活泼可爱天真烂漫的小孩",
    "身手敏捷来无影去无踪的杀手",
    "知书达理气质高贵的贵族",
    "仗义疏财行侠仗义的侠客",
    "精通魔法洞察未来的法师",
    "守护正义从不退缩的骑士",
    "与自然为伴善解人意的精灵",
]

CULTURAL_STYLES = ["chinese_modern", "chinese_traditional", "fantasy"]
GENDERS = ["male", "female", "neutral"]
AGES = ["child", "teen", "adult", "elder"]


# ==================== 测试统计 ====================

class CacheTestStats:
    """缓存测试统计"""

    def __init__(self):
        self.cache_hit_count = 0
        self.cache_miss_count = 0
        self.response_times = []
        self.success_count = 0
        self.failure_count = 0

    def record(self, response_time: float, from_cache: bool, success: bool):
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
            if from_cache:
                self.cache_hit_count += 1
            else:
                self.cache_miss_count += 1
        else:
            self.failure_count += 1

    def get_summary(self):
        if not self.response_times:
            return {}

        sorted_times = sorted(self.response_times)
        total = len(sorted_times)

        return {
            "total_requests": self.success_count + self.failure_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "cache_hit_count": self.cache_hit_count,
            "cache_miss_count": self.cache_miss_count,
            "cache_hit_rate": f"{self.cache_hit_count / self.success_count * 100:.1f}%" if self.success_count > 0 else "0%",
            "avg_response_time": round(sum(sorted_times) / total, 2),
            "min_response_time": round(sorted_times[0], 2),
            "max_response_time": round(sorted_times[-1], 2),
            "p50_response_time": round(sorted_times[int(total * 0.5)], 2),
            "p90_response_time": round(sorted_times[int(total * 0.9)], 2),
            "p99_response_time": round(sorted_times[int(total * 0.99)] if total > 100 else sorted_times[-1], 2),
        }


# 全局统计实例
cache_stats = CacheTestStats()


# ==================== 禁用缓存测试用户 ====================

class CacheDisabledUser(HttpUser):
    """
    禁用缓存的测试用户
    每次请求都使用不同的描述+时间戳，确保不命中缓存
    """
    wait_time = between(1, 2)

    def on_start(self):
        """用户启动时检查服务健康状态"""
        response = self.client.get("/health")
        if response.status_code == 200:
            print(f"[禁用缓存测试] 服务健康检查通过")

    @task
    def generate_without_cache(self):
        """禁用缓存的姓名生成请求"""
        # 使用随机描述+时间戳确保不命中缓存
        description = f"{random.choice(RANDOM_DESCRIPTIONS)}_{int(time.time() * 1000)}"

        payload = {
            "description": description,
            "count": 5,
            "cultural_style": random.choice(CULTURAL_STYLES),
            "gender": random.choice(GENDERS),
            "age": random.choice(AGES),
            "use_cache": False  # 显式禁用缓存
        }

        start_time = time.time()

        with self.client.post(
            "/generate",
            json=payload,
            catch_response=True,
            name="/generate [无缓存]",
            timeout=120
        ) as response:
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        cache_stats.record(elapsed_time, from_cache=False, success=True)
                        response.success()
                    else:
                        cache_stats.record(elapsed_time, from_cache=False, success=False)
                        response.failure(data.get("error", "未知错误"))
                except Exception as e:
                    cache_stats.record(elapsed_time, from_cache=False, success=False)
                    response.failure(f"解析响应失败: {str(e)}")
            else:
                cache_stats.record(elapsed_time, from_cache=False, success=False)
                response.failure(f"HTTP {response.status_code}")


# ==================== 启用缓存测试用户 ====================

class CacheEnabledUser(HttpUser):
    """
    启用缓存的测试用户
    使用固定的描述集合，在预热后大部分请求应命中缓存
    """
    wait_time = between(1, 2)

    def on_start(self):
        """用户启动时预热缓存"""
        response = self.client.get("/health")
        if response.status_code == 200:
            print(f"[启用缓存测试] 服务健康检查通过，开始预热缓存...")

        # 预热：对每个固定描述发送一次请求
        for desc in FIXED_DESCRIPTIONS[:3]:  # 只预热前3个
            payload = {
                "description": desc,
                "count": 5,
                "cultural_style": "chinese_modern",
                "gender": "neutral",
                "age": "adult",
                "use_cache": True
            }
            self.client.post("/generate", json=payload, timeout=120)

        print(f"[启用缓存测试] 缓存预热完成")

    @task
    def generate_with_cache(self):
        """启用缓存的姓名生成请求"""
        # 使用固定描述以命中缓存
        description = random.choice(FIXED_DESCRIPTIONS)

        payload = {
            "description": description,
            "count": 5,
            "cultural_style": "chinese_modern",  # 固定参数以提高缓存命中率
            "gender": "neutral",
            "age": "adult",
            "use_cache": True  # 启用缓存
        }

        start_time = time.time()

        with self.client.post(
            "/generate",
            json=payload,
            catch_response=True,
            name="/generate [有缓存]",
            timeout=120
        ) as response:
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        # 判断是否命中缓存（响应时间小于500ms认为是缓存命中）
                        from_cache = elapsed_time < 0.5
                        cache_stats.record(elapsed_time, from_cache=from_cache, success=True)
                        response.success()
                    else:
                        cache_stats.record(elapsed_time, from_cache=False, success=False)
                        response.failure(data.get("error", "未知错误"))
                except Exception as e:
                    cache_stats.record(elapsed_time, from_cache=False, success=False)
                    response.failure(f"解析响应失败: {str(e)}")
            else:
                cache_stats.record(elapsed_time, from_cache=False, success=False)
                response.failure(f"HTTP {response.status_code}")


# ==================== 混合测试用户（模拟真实场景） ====================

class MixedCacheUser(HttpUser):
    """
    混合缓存测试用户
    70%请求使用固定描述（可能命中缓存），30%使用随机描述
    """
    wait_time = between(1, 2)

    def on_start(self):
        response = self.client.get("/health")
        if response.status_code == 200:
            print(f"[混合测试] 服务健康检查通过")

    @task(7)
    def generate_likely_cached(self):
        """可能命中缓存的请求（权重7）"""
        payload = {
            "description": random.choice(FIXED_DESCRIPTIONS),
            "count": 5,
            "cultural_style": "chinese_modern",
            "gender": "neutral",
            "age": "adult",
            "use_cache": True
        }

        start_time = time.time()
        with self.client.post("/generate", json=payload, catch_response=True,
                             name="/generate [可能缓存]", timeout=120) as response:
            elapsed_time = time.time() - start_time
            if response.status_code == 200 and response.json().get("success"):
                from_cache = elapsed_time < 0.5
                cache_stats.record(elapsed_time, from_cache=from_cache, success=True)
                response.success()
            else:
                cache_stats.record(elapsed_time, from_cache=False, success=False)
                response.failure("请求失败")

    @task(3)
    def generate_not_cached(self):
        """不会命中缓存的请求（权重3）"""
        payload = {
            "description": f"{random.choice(RANDOM_DESCRIPTIONS)}_{time.time()}",
            "count": random.randint(3, 8),
            "cultural_style": random.choice(CULTURAL_STYLES),
            "gender": random.choice(GENDERS),
            "age": random.choice(AGES),
            "use_cache": True
        }

        start_time = time.time()
        with self.client.post("/generate", json=payload, catch_response=True,
                             name="/generate [未缓存]", timeout=120) as response:
            elapsed_time = time.time() - start_time
            if response.status_code == 200 and response.json().get("success"):
                cache_stats.record(elapsed_time, from_cache=False, success=True)
                response.success()
            else:
                cache_stats.record(elapsed_time, from_cache=False, success=False)
                response.failure("请求失败")


# ==================== 事件处理 ====================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始"""
    global cache_stats
    cache_stats = CacheTestStats()  # 重置统计
    print("=" * 70)
    print("智能姓名生成系统 - 缓存效果对比性能测试")
    print("=" * 70)
    print(f"目标主机: {environment.host}")
    print("=" * 70)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束"""
    print("\n" + "=" * 70)
    print("缓存效果对比测试结果")
    print("=" * 70)
    summary = cache_stats.get_summary()
    if summary:
        print(f"总请求数: {summary['total_requests']}")
        print(f"成功请求: {summary['success_count']}")
        print(f"失败请求: {summary['failure_count']}")
        print(f"缓存命中: {summary['cache_hit_count']}")
        print(f"缓存未命中: {summary['cache_miss_count']}")
        print(f"缓存命中率: {summary['cache_hit_rate']}")
        print("-" * 70)
        print(f"平均响应时间: {summary['avg_response_time']}s")
        print(f"最小响应时间: {summary['min_response_time']}s")
        print(f"最大响应时间: {summary['max_response_time']}s")
        print(f"P50响应时间: {summary['p50_response_time']}s")
        print(f"P90响应时间: {summary['p90_response_time']}s")
        print(f"P99响应时间: {summary['p99_response_time']}s")
    print("=" * 70)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              智能姓名生成系统 - 缓存效果对比测试工具                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  测试场景：                                                           ║
║                                                                      ║
║  1. 禁用缓存测试：                                                    ║
║     locust -f tests/locustfile_cache_comparison.py CacheDisabledUser \\
║            --host=http://127.0.0.1:5000 --headless -u 10 -r 2 -t 60s ║
║                                                                      ║
║  2. 启用缓存测试：                                                    ║
║     locust -f tests/locustfile_cache_comparison.py CacheEnabledUser  \\
║            --host=http://127.0.0.1:5000 --headless -u 10 -r 2 -t 60s ║
║                                                                      ║
║  3. 混合场景测试：                                                    ║
║     locust -f tests/locustfile_cache_comparison.py MixedCacheUser    \\
║            --host=http://127.0.0.1:5000 --headless -u 10 -r 2 -t 60s ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
