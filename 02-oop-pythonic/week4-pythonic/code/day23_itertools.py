"""
day23_itertools.py — itertools 模块常用函数
==============================================
itertools 提供了高效的迭代器工具，组合、过滤、无限循环都能搞定。
"""

import itertools

# ── 1. chain：串联多个可迭代对象 ──────────────────────────

def demo_chain():
    """chain 把多个迭代器首尾相接"""
    list1 = [1, 2, 3]
    list2 = [4, 5, 6]
    list3 = [7, 8, 9]
    result = list(itertools.chain(list1, list2, list3))
    print(f"chain({list1}, {list2}, {list3}) -> {result}")
    return result


# ── 2. product：笛卡尔积 ──────────────────────────────────

def demo_product():
    """product 生成所有组合（类似嵌套 for 循环）"""
    suits = ["红桃", "黑桃", "梅花", "方块"]
    ranks = ["A", "2", "3", "4", "5"]
    cards = list(itertools.product(suits, ranks))
    print(f"product({suits}, {ranks}) -> 共 {len(cards)} 张牌")
    print(f"前 5 张: {cards[:5]}")
    return cards


# ── 3. cycle：无限循环 ────────────────────────────────────

def demo_cycle():
    """cycle 无限重复一个可迭代对象（记得 break！）"""
    colors = ["红", "绿", "蓝"]
    result = []
    for i, color in enumerate(itertools.cycle(colors)):
        if i >= 7:          # 取前 7 个就停下
            break
        result.append(color)
    print(f"cycle({colors}) 取前 7 个 -> {result}")
    return result


# ── 4. islice：切片迭代器 ─────────────────────────────────

def demo_islice():
    """islice 对迭代器做切片，惰性求值"""
    # 生成 1~20 的平方
    squares = (x ** 2 for x in range(1, 21))
    sliced = list(itertools.islice(squares, 5, 10))   # 取索引 5~9
    print(f"islice(平方生成器, 5, 10) -> {sliced}")
    return sliced


# ── 5. groupby：相邻分组 ──────────────────────────────────

def demo_groupby():
    """groupby 把相邻的相同元素归为一组（注意要先排序）"""
    data = [("A", 1), ("A", 2), ("B", 3), ("B", 4), ("A", 5)]
    # groupby 只对相邻元素生效，所以要先按 key 排序
    sorted_data = sorted(data, key=lambda x: x[0])
    result = {}
    for key, group in itertools.groupby(sorted_data, key=lambda x: x[0]):
        result[key] = [item[1] for item in group]
    print(f"原始数据: {data}")
    print(f"排序后按 key 分组: {result}")
    return result


# ── 6. 练习：找出所有 (a, b, c) 组合，使 a + b + c = 100 ──

def find_triplets_sum_to_100():
    """
    找出 1~100 中所有三个数的组合，使其和为 100。
    使用 product 暴力枚举，再过滤。
    """
    numbers = range(1, 101)
    result = []
    for combo in itertools.product(numbers, repeat=3):
        if sum(combo) == 100:
            result.append(combo)
    return result


# ── 演示入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("1. chain — 串联迭代器")
    print("=" * 50)
    demo_chain()

    print("\n" + "=" * 50)
    print("2. product — 笛卡尔积（扑克牌）")
    print("=" * 50)
    demo_product()

    print("\n" + "=" * 50)
    print("3. cycle — 无限循环")
    print("=" * 50)
    demo_cycle()

    print("\n" + "=" * 50)
    print("4. islice — 迭代器切片")
    print("=" * 50)
    demo_islice()

    print("\n" + "=" * 50)
    print("5. groupby — 相邻分组")
    print("=" * 50)
    demo_groupby()

    print("\n" + "=" * 50)
    print("6. 练习：找到所有 (a, b, c) 组合，使 a + b + c = 100")
    print("=" * 50)
    triplets = find_triplets_sum_to_100()
    print(f"总共找到 {len(triplets)} 组")
    print(f"前 10 组: {triplets[:10]}")
    print(f"后 10 组: {triplets[-10:]}")
