"""
strings.py — 字符串工具模块
===========================
提供常用的字符串操作函数。
"""

def reverse(s: str) -> str:
    """返回字符串 s 的反转。"""
    return s[::-1]


def count_words(s: str) -> int:
    """返回字符串 s 中的单词数量（按空格分割）。"""
    return len(s.split())


def upper_case(s: str) -> str:
    """返回字符串 s 的全大写版本。"""
    return s.upper()


# 直接运行本文件时做简单测试
if __name__ == "__main__":
    text = "hello python world"
    print("strings 模块自测:")
    print(f"  reverse('{text}')     = '{reverse(text)}'")
    print(f"  count_words('{text}') = {count_words(text)}")
    print(f"  upper_case('{text}')  = '{upper_case(text)}'")