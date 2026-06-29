#!/usr/bin/env python3
"""Day 7: 函数"""

# ---------- 基本 ----------
def greet(name):
    return f"Hello, {name}"

# ---------- 默认参数 ----------
def power(base, exp=2):
    return base ** exp

print(power(3))    # 9
print(power(3, 3)) # 27

# ---------- *args ----------
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3, 4))  # 10

# ---------- **kwargs ----------
def create_user(**kwargs):
    return kwargs

print(create_user(name="Alice", age=25))  # {'name': 'Alice', 'age': 25}

# ---------- 类型注解 ----------
def add(a: int, b: int) -> int:
    return a + b

# ---------- 练习：可变参数计算器 ----------
def calc(operator, *numbers):
    if operator == "add":
        return sum(numbers)
    elif operator == "mul":
        result = 1
        for n in numbers:
            result *= n
        return result
    elif operator == "max":
        return max(numbers)
    elif operator == "min":
        return min(numbers)
    else:
        return "未知操作符"

print(calc("add", 1, 2, 3, 4))   # 10
print(calc("mul", 2, 3, 4))      # 24
print(calc("max", 5, 2, 8, 1))   # 8