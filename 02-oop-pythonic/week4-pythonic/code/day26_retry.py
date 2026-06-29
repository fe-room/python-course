"""
day26_retry.py — 带参数的 @retry 装饰器
==========================================
模拟一个"不稳定的网络请求"，用重试机制提高成功率。
"""

import functools
import random
import time


# ── 1. @retry 装饰器（带参数） ────────────────────────────

def retry(max_attempts=3, delay=0.5):
    """
    带参数的重试装饰器。
    max_attempts: 最大重试次数
    delay:        每次重试前的等待时间（秒）

    用法：
        @retry(max_attempts=3, delay=0.5)
        def flaky_func():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"  第 {attempt}/{max_attempts} 次尝试...")
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"  第 {attempt} 次失败: {e}")
                    if attempt < max_attempts:
                        print(f"  等待 {delay} 秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"  已达最大重试次数 {max_attempts}，放弃。")
            raise last_exception          # 全部失败后抛出最后一个异常
        return wrapper
    return decorator                       # 注意返回的是 decorator 函数


# ── 2. 模拟不稳定的网络请求 ──────────────────────────────

@retry(max_attempts=5, delay=0.3)
def flaky_network_request(url):
    """
    模拟一个只有 40% 成功率的网络请求。
    随机失败，带不同的错误信息。
    """
    if random.random() < 0.6:            # 60% 概率失败
        errors = [
            "连接超时",
            "服务器 500 错误",
            "DNS 解析失败",
            "连接被重置",
        ]
        raise ConnectionError(random.choice(errors))
    return f"成功获取 {url} 的数据"


# ── 3. 另一个示例：模拟读取文件（可配置成功率） ──────────

@retry(max_attempts=3, delay=0.2)
def flaky_read_file(filename, success_rate=0.5):
    """模拟读取文件，success_rate 控制成功率"""
    if random.random() > success_rate:
        raise IOError(f"读取 {filename} 失败：文件被占用")
    return f"文件 {filename} 的内容：Hello, World!"


# ── 演示入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("演示：@retry 装饰器处理不稳定的网络请求")
    print("=" * 60)

    # 固定随机种子，让每次运行结果可复现（方便调试）
    # 去掉这行就能看到每次不同的随机结果
    # random.seed(42)

    urls = [
        "https://api.example.com/users",
        "https://api.example.com/posts",
    ]

    for url in urls:
        print(f"\n>>> 正在请求: {url}")
        try:
            result = flaky_network_request(url)
            print(f"  结果: {result}")
        except ConnectionError as e:
            print(f"  最终失败: {e}")

    print("\n" + "=" * 60)
    print("额外演示：模拟读取文件（成功率 40%）")
    print("=" * 60)

    try:
        content = flaky_read_file("data.txt", success_rate=0.4)
        print(f"  结果: {content}")
    except IOError as e:
        print(f"  最终失败: {e}")
