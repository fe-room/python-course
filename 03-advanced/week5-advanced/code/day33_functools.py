"""
第 33 天：functools —— 函数式编程工具
========================================
functools 提供了高阶函数和可调用对象的操作工具。

对于前端工程师：
- @lru_cache 类似 React 的 useMemo / memo —— 缓存计算结果
- partial 类似 JS 的 Function.prototype.bind() —— 部分参数预填充
"""

import functools
import time


# ---------------------------------------------------------------
# 1. @lru_cache —— 最近最少使用缓存（记忆化）
# ---------------------------------------------------------------
def fibonacci_slow(n: int) -> int:
    """
    朴素递归实现斐波那契数列。
    没有缓存，重复计算导致指数级复杂度 O(2^n)。

    JS 对比：
        function fib(n) {
            if (n <= 1) return n;
            return fib(n - 1) + fib(n - 2);
        }
    """
    if n <= 1:
        return n
    return fibonacci_slow(n - 1) + fibonacci_slow(n - 2)


@functools.lru_cache(maxsize=128)
def fibonacci_cached(n: int) -> int:
    """
    使用 @lru_cache 装饰器的版本。
    缓存中间结果，将复杂度降到 O(n)。

    lru_cache(maxsize=128) 参数：
    - maxsize: 最多缓存多少个结果，None 表示无限制
    - typed: 是否区分不同参数类型（如 3 和 3.0）
    """
    if n <= 1:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


def demo_fibonacci_caching():
    """对比有无缓存时的性能差异。"""
    print("--- 斐波那契数列：缓存 vs 无缓存 ---")

    n = 35

    # 测试无缓存
    start = time.perf_counter()
    result_slow = fibonacci_slow(n)
    time_slow = time.perf_counter() - start

    # 测试有缓存
    start = time.perf_counter()
    result_cached = fibonacci_cached(n)
    time_cached = time.perf_counter() - start

    print(f"fibonacci({n}) = {result_slow}")
    print(f"  无缓存耗时: {time_slow:.4f} 秒")
    print(f"  有缓存耗时: {time_cached:.4f} 秒")
    print(f"  加速比: {time_slow / time_cached:.1f}x")

    # 查看缓存信息
    print(f"\n缓存统计:")
    print(f"  命中 (hits):       {fibonacci_cached.cache_info().hits}")
    print(f"  未命中 (misses):   {fibonacci_cached.cache_info().misses}")
    print(f"  当前大小 (currsize): {fibonacci_cached.cache_info().currsize}")
    print(f"  最大容量 (maxsize): {fibonacci_cached.cache_info().maxsize}")


# ---------------------------------------------------------------
# 2. functools.partial —— 部分参数预填充
# ---------------------------------------------------------------
def power(base: float, exponent: float) -> float:
    """
    计算 base 的 exponent 次幂。
    两个参数都需要调用者提供。

    JS 对比：
        function power(base, exponent) {
            return Math.pow(base, exponent);
        }
    """
    return base ** exponent


def demo_partial():
    """
    使用 partial 预填充 exponent 参数，创建专用函数。

    JS 对比：
        const square = power.bind(null, 2);  // 错误：bind 绑定的是第一个参数

    注意区别：
    - JS 的 bind 从左到右绑定参数（且会丢失 this 上下文）
    - Python 的 partial 可以按名称指定要绑定的参数

    Python 中正确的类比：
        // JS 没有直接的 partial，需要手动实现
        function partial(fn, ...boundArgs) {
            return function(...args) {
                return fn(...boundArgs, ...args);
            };
        }
        const square = partial(power, 4);  // 固定 base=4
    """
    print("\n--- partial 部分应用 ---")

    # 创建平方函数：固定 exponent=2
    square = functools.partial(power, exponent=2)
    # 创建立方函数：固定 exponent=3
    cube = functools.partial(power, exponent=3)

    # 现在只需要传入 base 即可
    numbers = [1, 2, 3, 4, 5]
    print(f"数字: {numbers}")
    print(f"平方: {[square(x) for x in numbers]}")
    print(f"立方: {[cube(x) for x in numbers]}")

    # 也可以按位置绑定第一个参数
    power_of_two = functools.partial(power, 2)  # 固定 base=2
    print(f"2 的幂: {[power_of_two(e) for e in range(1, 7)]}")


# ---------------------------------------------------------------
# 3. 更多 functools 实用工具
# ---------------------------------------------------------------
def demo_more_functools():
    """展示其他 functools 工具。"""
    print("\n--- 更多 functools 工具 ---")

    # @functools.wraps —— 保留被装饰函数的元信息
    def my_decorator(func):
        @functools.wraps(func)  # 不加这个，函数名和文档会丢失
        def wrapper(*args, **kwargs):
            """这是 wrapper 的文档。"""
            print(f"调用 {func.__name__}")
            return func(*args, **kwargs)
        return wrapper

    @my_decorator
    def say_hello(name: str):
        """说你好。"""
        return f"你好, {name}!"

    print(f"函数名: {say_hello.__name__}")          # 有 wraps: "say_hello"
    print(f"文档:   {say_hello.__doc__}")            # 有 wraps: "说你好。"
    print(f"结果:   {say_hello('张三')}")

    # functools.reduce —— 归约（类似 JS 的 Array.prototype.reduce）
    numbers = [1, 2, 3, 4, 5]
    total = functools.reduce(lambda a, b: a + b, numbers)
    product = functools.reduce(lambda a, b: a * b, numbers)
    print(f"\nreduce 求和:    {numbers} -> {total}")
    print(f"reduce 求积:    {numbers} -> {product}")


# ---------------------------------------------------------------
# 4. 实战：用 lru_cache 缓存 API 调用
# ---------------------------------------------------------------
def demo_cache_decorator_pattern():
    """
    模拟缓存 API 调用的结果。
    常用于减少重复的网络请求或数据库查询。
    """
    print("\n--- 模拟缓存 API 调用 ---")

    call_count = 0

    @functools.lru_cache(maxsize=32)
    def fetch_user(user_id: int) -> dict:
        """
        模拟从数据库获取用户信息。
        实际项目中，这里会是网络请求或数据库查询。
        """
        nonlocal call_count
        call_count += 1
        # 假设这是数据库查询
        users = {
            1: {"name": "张三", "role": "admin"},
            2: {"name": "李四", "role": "user"},
            3: {"name": "王五", "role": "user"},
        }
        print(f"    [实际查询] user_id={user_id}")
        time.sleep(0.05)  # 模拟查询延迟
        return users.get(user_id, {"name": "未知", "role": "guest"})

    # 第一次调用 —— 实际查询
    print("第一次调用（缓存未命中）:")
    result1 = fetch_user(1)
    print(f"  结果: {result1}")

    # 第二次调用相同参数 —— 命中缓存
    print("\n第二次调用（应该命中缓存）:")
    result2 = fetch_user(1)
    print(f"  结果: {result2}")

    # 查询不同用户 —— 未命中
    print("\n查询不同用户（缓存未命中）:")
    result3 = fetch_user(2)
    print(f"  结果: {result3}")

    print(f"\n总共实际查询次数: {call_count}（3 次调用只查询了 2 次）")


if __name__ == "__main__":
    print("=" * 55)
    print("第 33 天：functools —— 函数式编程工具")
    print("=" * 55)

    demo_fibonacci_caching()
    demo_partial()
    demo_more_functools()
    demo_cache_decorator_pattern()
