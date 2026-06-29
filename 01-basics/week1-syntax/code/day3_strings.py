#!/usr/bin/env python3
"""Day 3: 字符串操作"""

from datetime import datetime

# ---------- 切片 ----------
s = "Python"
print(s[0])      # P
print(s[-1])     # n
print(s[0:3])    # Pyt（左闭右开）
print(s[:3])     # Pyt
print(s[3:])     # hon
print(s[::2])    # Pto
print(s[::-1])   # nohtyP

# ---------- 常用方法 ----------
print("hello world".split())              # ['hello', 'world']
print(" ".join(["a", "b", "c"]))          # a b c
print("  abc  ".strip())                   # abc
print("hello".replace("l", "x"))          # hexxo
print("hello".startswith("he"))            # True
print("hello".endswith("lo"))              # True

# ---------- f-string ----------
name, age = "Bob", 30
print(f"{name} is {age} years old")
print(f"{age:04d}")          # 0030
print(f"{3.14159:.2f}")      # 3.14

# ---------- 练习：日志格式化 ----------
def format_log(level, message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{now}] [{level.upper()}] {message}"

print(format_log("info", "服务启动"))
print(format_log("error", "数据库连接失败"))