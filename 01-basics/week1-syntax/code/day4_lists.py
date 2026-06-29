#!/usr/bin/env python3
"""Day 4: 列表操作"""

# ---------- 基本操作 ----------
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
fruits.insert(0, "avocado")
print("after append/insert:", fruits)

fruits.remove("banana")
popped = fruits.pop()
print("after remove/pop:", fruits, "| popped:", popped)

# ---------- 切片 ----------
nums = [0, 1, 2, 3, 4, 5]
print("nums[1:4]:", nums[1:4])    # [1, 2, 3]
print("nums[::-1]:", nums[::-1])  # [5, 4, 3, 2, 1, 0]

# ---------- 列表推导式 ----------
squares = [x * 2 for x in range(5)]
evens = [x for x in range(10) if x % 2 == 0]
print("squares:", squares)   # [0, 2, 4, 6, 8]
print("evens:", evens)       # [0, 2, 4, 6, 8]

# ---------- 遍历 ----------
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# ---------- 练习 ----------
def even_squares(numbers):
    """返回列表中偶数的平方"""
    return [n * n for n in numbers if n % 2 == 0]

print("even_squares([1,2,3,4,5,6]):", even_squares([1, 2, 3, 4, 5, 6]))
# 预期: [4, 16, 36]