"""
day22_collections.py — defaultdict, Counter, deque 用法
======================================================
Python 标准库 collections 模块提供了好用的数据结构，
能让代码更简洁、更 Pythonic。
"""

from collections import defaultdict, Counter, deque

# ── 1. Counter：词频统计 ──────────────────────────────────

def word_frequency_handwritten(words):
    """手写版本：自己维护 dict 计数"""
    freq = {}
    for w in words:
        if w in freq:
            freq[w] += 1
        else:
            freq[w] = 1
    return freq

def word_frequency_counter(words):
    """Counter 版本：一行搞定"""
    return Counter(words)


# ── 2. defaultdict：自动分组 ──────────────────────────────

def group_by_first_letter_handwritten(items):
    """手写版本：每次都要检查 key 是否存在"""
    result = {}
    for item in items:
        key = item[0].upper()          # 取首字母大写作为分组 key
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result

def group_by_first_letter_defaultdict(items):
    """defaultdict 版本：自动创建空 list，省去 if 判断"""
    result = defaultdict(list)
    for item in items:
        result[item[0].upper()].append(item)
    return dict(result)                # 转回普通 dict 方便查看


# ── 3. deque：双端队列 ────────────────────────────────────

def deque_demo():
    """演示 deque 在两端增删的高效性"""
    dq = deque(maxlen=5)               # 固定长度，超长自动丢弃旧元素
    for i in range(1, 8):
        dq.append(i)
        print(f"append({i}) -> {list(dq)}")
    return dq


# ── 演示入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("1. Counter 词频统计")
    print("=" * 50)
    words = ["apple", "banana", "apple", "orange", "banana", "apple", "kiwi"]
    hw = word_frequency_handwritten(words)
    ct = word_frequency_counter(words)
    print(f"手写版: {hw}")
    print(f"Counter: {ct}")
    print(f"最常见的 2 个: {ct.most_common(2)}")

    print("\n" + "=" * 50)
    print("2. defaultdict 分组")
    print("=" * 50)
    fruits = ["apple", "banana", "avocado", "blueberry", "cherry", "apricot"]
    print(f"手写版:     {group_by_first_letter_handwritten(fruits)}")
    print(f"defaultdict: {group_by_first_letter_defaultdict(fruits)}")

    print("\n" + "=" * 50)
    print("3. deque 演示")
    print("=" * 50)
    dq = deque_demo()
    print(f"\n最终 deque: {list(dq)}")
    dq.appendleft("new")
    print(f"appendleft -> {list(dq)}")
    dq.pop()
    print(f"pop        -> {list(dq)}")
    dq.popleft()
    print(f"popleft    -> {list(dq)}")
