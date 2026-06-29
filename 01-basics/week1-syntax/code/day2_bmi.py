#!/usr/bin/env python3
"""Day 2: 变量与类型 — BMI 计算器"""

# 输入
height = float(input("身高(m)："))
weight = float(input("体重(kg)："))

# 计算
bmi = weight / (height ** 2)

# 判断
if bmi < 18.5:
    level = "偏瘦"
elif bmi < 24:
    level = "正常"
elif bmi < 28:
    level = "偏胖"
else:
    level = "肥胖"

# 输出（保留 1 位小数）
print(f"BMI = {bmi:.1f}，{level}")

# 类型练习
print(f"type(height) = {type(height)}")  # <class 'float'>
print(f"type(True) = {type(True)}")       # <class 'bool'>
print(f"type(None) = {type(None)}")       # <class 'NoneType'>