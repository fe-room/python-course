"""
day12_comprehensions.py — 高级推导式
====================================
知识点：
  1. 列表推导式（含嵌套循环）
  2. 字典推导式
  3. 集合推导式
  4. 推导式中的三元表达式（条件表达式）
  5. 实战：一行代码过滤奇数并求平方
"""

from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. 列表推导式复习 + 进阶
# ---------------------------------------------------------------------------
print("=" * 50)
print("1. 列表推导式 (List Comprehension)")
print("=" * 50)

# 基础：生成 0 ~ 9 的平方
squares = [x ** 2 for x in range(10)]
print(f"0~9 的平方: {squares}")

# 带条件：只保留偶数
evens = [x for x in range(20) if x % 2 == 0]
print(f"0~19 的偶数: {evens}")

# --- 嵌套循环 in 推导式 ---
# 生成坐标对 (x, y)
coords = [(x, y) for x in range(3) for y in range(3)]
print(f"\n坐标对 (3x3): {coords}")

# 相当于：
# result = []
# for x in range(3):
#     for y in range(3):
#         result.append((x, y))

# 嵌套循环 + 条件：只保留 x != y 的坐标
unique_coords = [(x, y) for x in range(3) for y in range(3) if x != y]
print(f"坐标对 (x != y): {unique_coords}")

# 展平二维列表
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
print(f"\n展平矩阵: {matrix} -> {flat}")

# 嵌套循环理解口诀：
# for 子句的顺序 = 普通 for 循环的嵌套顺序（从左到右）
# [expr for a in A for b in B if cond]
# 等价于：
# for a in A:
#     for b in B:
#         if cond: result.append(expr)

# ---------------------------------------------------------------------------
# 2. 字典推导式
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("2. 字典推导式 (Dict Comprehension)")
print("=" * 50)

# 基础：数字 → 平方
square_dict = {x: x ** 2 for x in range(5)}
print(f"数字 → 平方: {square_dict}")

# 条件过滤
even_squares = {x: x ** 2 for x in range(10) if x % 2 == 0}
print(f"偶数的平方: {even_squares}")

# 实用场景：交换键值
original = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in original.items()}
print(f"\n交换键值: {original} -> {swapped}")

# 实用场景：列表 → 词频字典
words = ["apple", "banana", "apple", "orange", "banana", "apple"]
word_count = {w: words.count(w) for w in set(words)}
print(f"\n词频统计: {word_count}")

# ---------------------------------------------------------------------------
# 3. 集合推导式
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("3. 集合推导式 (Set Comprehension)")
print("=" * 50)

# 基础：去重 + 转换
nums = [1, 2, 2, 3, 3, 3, 4, 5, 5]
unique_squares = {x ** 2 for x in nums}
print(f"去重平方: {nums} -> {unique_squares}")

# 提取字符串中的唯一字母
sentence = "hello world"
unique_letters = {c for c in sentence if c.isalpha()}
print(f"唯一字母: {sorted(unique_letters)}")

# ---------------------------------------------------------------------------
# 4. 推导式中的三元表达式
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("4. 推导式 + 三元表达式")
print("=" * 50)

# Python 的三元表达式： x if cond else y
# 结合推导式可以实现"双分支"效果

# 把 0~9 中的偶数标为 "even"，奇数标为 "odd"
labels = ["even" if x % 2 == 0 else "odd" for x in range(10)]
print(f"偶数/奇数标签: {labels}")

# 实用：将分数转为等级
scores = [85, 92, 58, 73, 45, 100]
grades = ["优秀" if s >= 90 else "良好" if s >= 75 else "及格" if s >= 60 else "不及格" for s in scores]
print(f"\n分数: {scores}")
print(f"等级: {grades}")

# 注意：嵌套三元表达式可读性较差，实际开发中建议用函数

# ---------------------------------------------------------------------------
# 5. 练习题：一行代码过滤奇数并求平方
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("练习题：一行代码过滤奇数并求平方")
print("=" * 50)
"""
请用一行列表推导式实现 filter_odd_square(numbers)：
  - 输入：numbers，一个整数列表
  - 输出：新列表，只保留奇数，每个奇数取平方
  - 要求：只用一行 return 语句
示例：
  filter_odd_square([1, 2, 3, 4, 5]) -> [1, 9, 25]
"""

# ---------- 你的代码从这里开始 ----------

def filter_odd_square(numbers):
    """一行代码：过滤出奇数并返回它们的平方"""
    return [x ** 2 for x in numbers if x % 2 != 0]


# 进阶版：也处理负数，保证平方后结果正确
def filter_odd_square_advanced(numbers):
    """进阶版：支持负数（负数也是奇数/偶数）"""
    return [x ** 2 for x in numbers if x % 2 != 0]


# ---------- 测试 ----------

def test_filter_odd_square():
    # 测试 1
    result = filter_odd_square([1, 2, 3, 4, 5])
    expected = [1, 9, 25]
    assert result == expected, f"期望 {expected}, 得到 {result}"
    print(f"测试 1: filter_odd_square([1,2,3,4,5]) = {result}")

    # 测试 2
    result = filter_odd_square([10, 11, 12, 13])
    expected = [121, 169]
    assert result == expected, f"期望 {expected}, 得到 {result}"
    print(f"测试 2: filter_odd_square([10,11,12,13]) = {result}")

    # 测试 3
    result = filter_odd_square([2, 4, 6])
    assert result == [], f"期望 [], 得到 {result}"
    print(f"测试 3: filter_odd_square([2,4,6]) = {result}")

    # 测试 4: 进阶版
    result = filter_odd_square_advanced([-3, -2, -1, 0, 1, 2, 3])
    expected = [9, 1, 1, 9]
    assert result == expected, f"期望 {expected}, 得到 {result}"
    print(f"测试 4 (负数): filter_odd_square_advanced([-3,-2,-1,0,1,2,3]) = {result}")

    print("所有测试通过！")

if __name__ == "__main__":
    test_filter_odd_square()
    print("\n推导式演示完成。")