"""
day24_contextmanager.py — 上下文管理器（Context Manager）
=============================================================
上下文管理器让你可以用 with 语句安全地管理资源。
这里用两种方式实现一个计时器 Timer：
  1. 基于 __enter__ / __exit__ 的类版本
  2. 基于 @contextmanager 装饰器的生成器版本
"""

import time
from contextlib import contextmanager


# ── 方式一：基于 __enter__ / __exit__ ─────────────────────

class TimerClass:
    """
    用 __enter__ / __exit__ 实现的计时器。
    with 进入时记录开始时间，退出时打印耗时。
    """

    def __init__(self, name="代码块"):
        self.name = name

    def __enter__(self):
        """进入 with 块时调用，返回的对象赋值给 as 后面的变量"""
        self.start = time.perf_counter()       # perf_counter 精度更高
        print(f"[{self.name}] 开始计时...")
        return self                            # 可以用 as t 拿到这个对象

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        离开 with 块时调用。
        参数 exc_type/exc_val/exc_tb 是异常信息（没有异常则为 None）。
        返回 True 表示"异常已处理"，不会往外抛。
        """
        elapsed = time.perf_counter() - self.start
        print(f"[{self.name}] 耗时: {elapsed:.4f} 秒")
        # 返回 False（默认）表示异常继续往外抛，True 则吞掉异常
        return False


# ── 方式二：基于 @contextmanager 装饰器 ───────────────────

@contextmanager
def timer_context(name="代码块"):
    """
    用 @contextmanager 装饰器，只需写一个生成器函数。
    yield 之前是 __enter__，之后是 __exit__。
    """
    print(f"[{name}] 开始计时...")
    start = time.perf_counter()
    try:
        yield                        # yield 的值会赋给 as 后面的变量
    finally:
        elapsed = time.perf_counter() - start
        print(f"[{name}] 耗时: {elapsed:.4f} 秒")
    # 如果生成器内部发生异常，异常会在 yield 处抛出，被 finally 捕获后继续传播


# ── 演示入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("方式一：基于 __enter__ / __exit__ 的类")
    print("=" * 50)

    with TimerClass("睡眠 0.5 秒") as t:
        time.sleep(0.5)
        print(f"  t 的类型: {type(t).__name__}")

    print("\n" + "=" * 50)
    print("方式二：基于 @contextmanager 装饰器")
    print("=" * 50)

    with timer_context("睡眠 0.3 秒"):
        time.sleep(0.3)

    print("\n" + "=" * 50)
    print("嵌套使用（自动缩进演示）")
    print("=" * 50)

    with TimerClass("外层"):
        time.sleep(0.2)
        with timer_context("内层"):
            time.sleep(0.3)
