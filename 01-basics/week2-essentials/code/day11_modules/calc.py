"""
calc.py — 基础计算器模块
=======================
提供简单的四则运算函数。
"""

def add(a, b):
    """返回 a + b"""
    return a + b


def subtract(a, b):
    """返回 a - b"""
    return a - b


def multiply(a, b):
    """返回 a * b"""
    return a * b


def divide(a, b):
    """
    返回 a / b。
    注意：如果 b 为 0，Python 会抛出 ZeroDivisionError。
    """
    return a / b


# 直接运行本文件时做简单测试
if __name__ == "__main__":
    print("calc 模块自测:")
    print(f"  add(10, 5)      = {add(10, 5)}")
    print(f"  subtract(10, 5) = {subtract(10, 5)}")
    print(f"  multiply(10, 5) = {multiply(10, 5)}")
    print(f"  divide(10, 5)   = {divide(10, 5)}")