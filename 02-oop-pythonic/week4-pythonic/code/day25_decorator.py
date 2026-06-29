"""
day25_decorator.py — 装饰器（Decorator）入门
==============================================
装饰器是"给函数增加额外功能"的语法糖。
用 @wraps 可以保留原函数的元信息（名字、文档等）。
"""

import functools
import time


# ── 1. 简单的 @log_call 装饰器 ───────────────────────────

def log_call(func):
    """
    打印函数调用日志的装饰器。
    用 @wraps 保留原函数的 __name__ 和 __doc__。
    """
    @functools.wraps(func)                     # 保留原函数元信息
    def wrapper(*args, **kwargs):
        print(f"[LOG] 调用 {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} 返回: {result}")
        return result
    return wrapper


@log_call
def add(a, b):
    """把两个数相加"""
    return a + b


@log_call
def greet(name, greeting="你好"):
    """向某人打招呼"""
    return f"{greeting}，{name}！"


# ── 2. 演示 @wraps 的作用 ───────────────────────────────

def log_call_without_wraps(func):
    """不加 @wraps 的版本，对比用"""
    def wrapper(*args, **kwargs):
        print(f"[LOG] 调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@log_call_without_wraps
def say_hello_without():
    """没有 @wraps 的函数"""
    print("Hello!")


@log_call
def say_hello_with():
    """使用 @wraps 的函数"""
    print("Hello!")


# ── 3. 实用例子：计时装饰器 ─────────────────────────────

def timer(func):
    """测量函数执行时间的装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMER] {func.__name__} 耗时: {elapsed:.4f} 秒")
        return result
    return wrapper


@timer
def slow_sum(n):
    """计算 1 到 n 的和（故意用循环制造延迟）"""
    total = 0
    for i in range(n):
        total += i
    return total


# ── 演示入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("1. @log_call 装饰器演示")
    print("=" * 50)
    print(add(3, 5))
    print(greet("小明", greeting="哈喽"))

    print("\n" + "=" * 50)
    print("2. @wraps 的作用对比")
    print("=" * 50)
    print(f"有 @wraps  → 函数名: {say_hello_with.__name__}  |  文档: {say_hello_with.__doc__}")
    print(f"无 @wraps → 函数名: {say_hello_without.__name__}  |  文档: {say_hello_without.__doc__}")
    print("（注意：无 @wraps 的版本函数名变成了 wrapper，文档也丢了！）")

    print("\n" + "=" * 50)
    print("3. 计时装饰器演示")
    print("=" * 50)
    result = slow_sum(1_000_000)
    print(f"计算结果: {result}")
