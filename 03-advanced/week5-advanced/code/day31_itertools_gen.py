"""
第 31 天：itertools 与生成器实战
===================================
itertools 是 Python 内置的迭代器工具库，提供了丰富的生成器函数。

对于前端工程师：
- itertools.cycle 类似无限循环数组，但惰性求值
- itertools.islice 类似 Array.prototype.slice()，不过作用于迭代器
- itertools.takewhile 类似 Array.prototype.filter()，但遇到 False 就停止
"""

import itertools
import time


# ---------------------------------------------------------------
# 1. itertools.cycle —— 无限循环播放列表
# ---------------------------------------------------------------
def demo_cycle_and_islice():
    """
    cycle 无限循环一个可迭代对象。
    islice 从迭代器中切片取出前 n 个元素。

    实战场景：音乐播放器循环播放歌单。
    """
    print("--- 循环播放歌单 (cycle + islice) ---")

    playlist = [
        "🎵 晴天 - 周杰伦",
        "🎵 起风了 - 买辣椒也用券",
        "🎵 孤勇者 - 陈奕迅",
    ]

    # cycle 创建无限循环迭代器
    # 对应 JS: function* cycle(arr) { while(true) yield* arr; }
    infinite_player = itertools.cycle(playlist)

    # islice 限制只取出前 7 首（模拟"切歌"7 次）
    # itertools.islice(iterable, start, stop[, step])
    print("播放列表（循环 3 轮后切歌到第 7 首）:")
    for idx, song in enumerate(itertools.islice(infinite_player, 7), 1):
        print(f"  {idx}. {song}")
        time.sleep(0.1)  # 模拟播放间隔


# ---------------------------------------------------------------
# 2. itertools.takewhile —— 条件成立时取值
# ---------------------------------------------------------------
def demo_takewhile():
    """
    takewhile(predicate, iterable)
    从可迭代对象中取出元素，直到条件第一次为 False 时停止。

    类似 Array.prototype.filter() + break —— 但更高效。
    """
    print("\n--- takewhile: 取数直到条件不成立 ---")

    # 场景 1：从数组中取出小于 100 的斐波那契数
    def fibonacci():
        """无限生成斐波那契数列。"""
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b

    fib_under_100 = list(itertools.takewhile(lambda x: x < 100, fibonacci()))
    print(f"小于 100 的斐波那契数: {fib_under_100}")

    # 场景 2：从传感器读取温度数据，只在温度低于阈值时记录
    sensor_data = [25, 26, 27, 28, 30, 35, 29, 28, 27]
    # 只关心温度 < 30 时的数据（一旦 >= 30 就停止关注）
    normal_data = list(itertools.takewhile(lambda t: t < 30, sensor_data))
    print(f"传感器正常数据 (temp < 30): {normal_data}")
    print(f"  注意：35 之后的 29, 28 没有出现，因为遇到 35 时就停止了")


# ---------------------------------------------------------------
# 3. 更多 itertools 实用函数
# ---------------------------------------------------------------
def demo_more_itertools():
    """展示其他常用 itertools 函数。"""
    print("\n--- 更多 itertools 函数 ---")

    # chain —— 将多个可迭代对象串联
    list1 = [1, 2, 3]
    list2 = [4, 5, 6]
    chained = list(itertools.chain(list1, list2))
    print(f"chain({list1}, {list2})            = {chained}")

    # zip_longest —— 类似 zip，但以最长的为准，缺失值填充
    names = ["张三", "李四", "王五", "赵六"]
    scores = [85, 92, 78]
    zipped = list(itertools.zip_longest(names, scores, fillvalue="缺考"))
    print(f"zip_longest(names, scores)       = {zipped}")

    # product —— 笛卡尔积（嵌套循环的替代）
    colors = ["红", "蓝"]
    sizes = ["S", "M", "L"]
    products = list(itertools.product(colors, sizes))
    print(f"product({colors}, {sizes}) = {products}")

    # permutations —— 排列
    items = ["A", "B", "C"]
    perms = list(itertools.permutations(items, 2))
    print(f"permutations({items}, 2)        = {perms}")

    # combinations —— 组合
    combs = list(itertools.combinations(items, 2))
    print(f"combinations({items}, 2)        = {combs}")


# ---------------------------------------------------------------
# 4. 实战：分页读取大量数据
# ---------------------------------------------------------------
def paginate(iterable, page_size: int):
    """
    将可迭代对象分页，每次 yield 一页数据。
    使用 iter() 和 islice 实现。

    前端类比：
    类似前端分页组件，但数据源是后端 API（迭代器）。
    """
    iterator = iter(iterable)
    while True:
        page = list(itertools.islice(iterator, page_size))
        if not page:
            break
        yield page


def demo_pagination():
    """演示分页功能。"""
    print("\n--- 数据分页 (islice 实现) ---")

    # 模拟大量数据
    all_data = range(1, 26)  # 1 到 25
    page_size = 7

    print(f"总共 {len(list(range(1, 26)))} 条数据，每页 {page_size} 条:")
    for page_num, page_data in enumerate(paginate(all_data, page_size), 1):
        print(f"  第 {page_num} 页: {page_data}")


# ---------------------------------------------------------------
# 5. 自定义生成器 vs itertools 对比
# ---------------------------------------------------------------
def demo_custom_vs_itertools():
    """对比手动编写生成器和使用 itertools 的差异。"""
    print("\n--- 自定义 vs itertools ---")

    data = [1, 2, 3, 4, 5]

    # 手动实现 cycle（取两次）
    def manual_cycle(items, times):
        for _ in range(times):
            for item in items:
                yield item

    manual = list(manual_cycle(data, 2))
    # 使用 itertools
    from_itertools = list(itertools.islice(itertools.cycle(data), len(data) * 2))

    print(f"手动 cycle * 2:    {manual}")
    print(f"itertools cycle:   {from_itertools}")
    print(f"结果相同: {manual == from_itertools}")


if __name__ == "__main__":
    print("=" * 55)
    print("第 31 天：itertools 与生成器实战")
    print("=" * 55)

    demo_cycle_and_islice()
    demo_takewhile()
    demo_pagination()
    demo_more_itertools()
    demo_custom_vs_itertools()
