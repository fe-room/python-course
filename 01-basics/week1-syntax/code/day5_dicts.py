#!/usr/bin/env python3
"""Day 5: 字典操作"""

# ---------- 基本操作 ----------
user = {"name": "Alice", "age": 25}
user["email"] = "alice@example.com"
print(user.get("name"))          # Alice
print(user.get("phone", "N/A"))  # N/A（带默认值）

# ---------- 遍历 ----------
for key, val in user.items():
    print(f"{key}: {val}")

# ---------- 字典推导式 ----------
squared = {x: x**2 for x in range(5)}
print("dict comp:", squared)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# ---------- 练习：单词频率统计 ----------
text = "hello world hello python hello world"
freq = {}
for word in text.split():
    freq[word] = freq.get(word, 0) + 1

top3 = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]
print("top 3 words:", top3)  # [('hello', 3), ('world', 2), ('python', 1)]