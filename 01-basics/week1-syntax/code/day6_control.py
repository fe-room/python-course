#!/usr/bin/env python3
"""Day 6: 控制流"""

# ---------- if/elif/else ----------
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "D"
print(f"score={score}, grade={grade}")

# ---------- 三元表达式 ----------
age = 20
status = "成年" if age >= 18 else "未成年"
print(status)  # 成年

# ---------- for + range ----------
print("range(5):", end=" ")
for i in range(5):
    print(i, end=" ")
print()

# ---------- 练习：99 乘法表 ----------
print("\n99 乘法表:")
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}x{i}={i*j}", end="\t")
    print()

# ---------- 练习：FizzBuzz ----------
print("\nFizzBuzz:")
for i in range(1, 21):  # 只打印到 20 节省空间
    if i % 15 == 0:
        print("FizzBuzz", end=" ")
    elif i % 3 == 0:
        print("Fizz", end=" ")
    elif i % 5 == 0:
        print("Buzz", end=" ")
    else:
        print(i, end=" ")
print()