"""
第 29 天：生成器（Generator）
=============================
对比列表推导式与生成器的内存占用，理解 yield 关键字。

对于前端工程师：
- 生成器类似 JavaScript 中的 Generator function（function*）
- yield 类似 JS 中的 yield 关键字
- 区别：Python 生成器是 表达式（yield 产生值），JS 生成器返回 {value, done} 对象
"""

import sys


# ---------------------------------------------------------------
# 1. 基本生成器函数：从 1 数到 n
# ---------------------------------------------------------------
def count_up_to(n: int):
    """
    生成从 1 到 n 的整数。
    类似 JS: function* countUpTo(n) { for (let i = 1; i <= n; i++) yield i; }
    """
    i = 1
    while i <= n:
        yield i  # 产出当前值，暂停执行
        i += 1   # 下一次调用 __next__() 时从这里继续


# ---------------------------------------------------------------
# 2. 内存对比：列表 vs 生成器
# ---------------------------------------------------------------
def memory_comparison():
    """演示列表推导式与生成器表达式在内存占用上的巨大差异。"""
    n = 100_000

    # 列表推导式 —— 一次性生成所有元素存到内存
    list_squares = [x * x for x in range(n)]
    list_size = sys.getsizeof(list_squares)

    # 生成器表达式 —— 惰性求值，每次只生成一个元素
    gen_squares = (x * x for x in range(n))
    gen_size = sys.getsizeof(gen_squares)

    print(f"n = {n:,}")
    print(f"{'列表推导式':>12}  size = {list_size:>10} 字节  (含 {len(list_squares):,} 个元素)")
    print(f"{'生成器表达式':>12}  size = {gen_size:>10} 字节  (只存了生成器状态)")
    print(f"生成器比列表节省了 {list_size - gen_size:,} 字节（{(1 - gen_size / list_size) * 100:.1f}%）")

    # 验证结果一致
    print(f"\n前 5 个平方数（列表）:   {list_squares[:5]}")
    print(f"前 5 个平方数（生成器）: {list(next(gen_squares) for _ in range(5))}")


# ---------------------------------------------------------------
# 3. 模拟读取大文件（逐行读取，不把整个文件加载到内存）
# ---------------------------------------------------------------
def read_large_file_line_by_line(file_path: str):
    """
    逐行读取文件，每次只保留一行在内存中。
    适用于 GB 级别的日志文件。

    Python 特有的文件迭代器本身就是生成器：
    for line in open(file):  # open() 返回的文件对象是可迭代的
        ...
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # f 本身就是一个生成器式的迭代器
            for line_number, line in enumerate(f, 1):
                # yield 当前行，调用者处理完后再 yield 下一行
                yield line_number, line.strip()
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return  # 生成器结束


def demo_read_large_file():
    """演示大文件按行读取（使用一个临时小文件做示例）。"""
    import tempfile
    import os

    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".log", delete=False) as tmp:
        tmp.write("2025-01-01 INFO  服务启动\n")
        tmp.write("2025-01-01 DEBUG 加载配置中...\n")
        tmp.write("2025-01-01 INFO  数据库连接成功\n")
        tmp.write("2025-01-01 ERROR 连接超时，重试第 1 次\n")
        tmp.write("2025-01-01 ERROR 连接超时，重试第 2 次\n")
        tmp.write("2025-01-01 INFO  连接恢复\n")
        tmp_path = tmp.name

    print(f"读取临时文件: {tmp_path}")
    # 使用生成器逐行读取 —— 如果文件有 10GB，这里的内存占用依然很小
    for line_num, line_content in read_large_file_line_by_line(tmp_path):
        # 只处理 ERROR 级别的日志
        if "ERROR" in line_content:
            print(f"  [异常] 第 {line_num} 行: {line_content}")

    os.unlink(tmp_path)  # 清理临时文件


# ---------------------------------------------------------------
# 4. 生成器的其他特性
# ---------------------------------------------------------------
def generator_features():
    """展示生成器的额外能力。"""

    def fibonacci_gen(limit: int):
        """生成斐波那契数列，不超过 limit。"""
        a, b = 0, 1
        while a <= limit:
            yield a
            a, b = b, a + b

    print("\n--- 生成器特性 ---")

    # 特性 1：生成器只能遍历一次（一次性的）
    fib = fibonacci_gen(100)
    print(f"斐波那契数列（<= 100）: {list(fib)}")
    print(f"再次遍历 fib: {list(fib)}（空，因为生成器已耗尽）")

    # 特性 2：生成器可以用于 for 循环
    print("逐个打印:", end=" ")
    for num in fibonacci_gen(20):
        print(num, end=" ")
    print()

    # 特性 3：可以用 next() 手动驱动
    gen = count_up_to(3)
    print(f"next(gen) = {next(gen)}")  # 1
    print(f"next(gen) = {next(gen)}")  # 2
    print(f"next(gen) = {next(gen)}")  # 3
    try:
        next(gen)  # 生成器耗尽，抛出 StopIteration
    except StopIteration:
        print("生成器已耗尽（StopIteration）")


if __name__ == "__main__":
    print("=" * 55)
    print("第 29 天：生成器（Generator）")
    print("=" * 55)

    print("\n>>> 1. 基本生成器 count_up_to <<<")
    for num in count_up_to(10):
        print(num, end=" ")
    print()

    print("\n\n>>> 2. 内存对比：列表 vs 生成器 <<<")
    memory_comparison()

    print("\n\n>>> 3. 模拟大文件逐行读取 <<<")
    demo_read_large_file()

    print("\n\n>>> 4. 生成器特性 <<<")
    generator_features()
