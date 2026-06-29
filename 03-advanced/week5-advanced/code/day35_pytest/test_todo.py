"""
第 35 天：pytest 测试入门
===========================
使用 pytest 编写单元测试。

运行方式（在终端中执行）：
    pip install pytest && pytest test_todo.py -v

对于前端工程师：
- pytest 类似 Jest / Vitest
- assert 语句类似 Jest 的 expect().toBe()
- pytest 会自动发现 test_ 开头的函数
"""

# ---------------------------------------------------------------
# 待测试的函数：返回 1 到 n 之间所有偶数的平方
# ---------------------------------------------------------------
def even_squares(n: int) -> list:
    """
    返回 1 到 n 之间所有偶数的平方。

    >>> even_squares(10)
    [4, 16, 36, 64, 100]
    >>> even_squares(1)
    []
    """
    if n <= 1:
        return []
    return [x * x for x in range(2, n + 1, 2)]


# ---------------------------------------------------------------
# 测试用例
# ---------------------------------------------------------------

def test_even_squares_returns_correct_values():
    """测试基础功能：返回正确的偶数的平方。"""
    result = even_squares(10)
    # assert 相当于 Jest 中的 expect(result).toEqual([4, 16, 36, 64, 100])
    assert result == [4, 16, 36, 64, 100]


def test_even_squares_empty_when_n_less_than_2():
    """测试边界情况：n < 2 时返回空列表。"""
    assert even_squares(1) == []
    assert even_squares(0) == []
    assert even_squares(-5) == []


def test_even_squares_n_is_2():
    """测试边界情况：n 正好等于 2。"""
    # 2 是偶数，2^2 = 4
    assert even_squares(2) == [4]


def test_even_squares_n_is_3():
    """测试边界情况：n 是奇数且大于 2。"""
    # 只有 2 是偶数 2^2 = 4
    assert even_squares(3) == [4]


def test_even_squares_large_n():
    """测试大数值。"""
    result = even_squares(100)
    # 1-100 有 50 个偶数
    assert len(result) == 50
    # 最后一个偶数是 100，100^2 = 10000
    assert result[-1] == 10000
    # 第一个偶数是 2，2^2 = 4
    assert result[0] == 4


def test_even_squares_contains_only_even_squares():
    """测试所有结果都是偶数的平方（能被 4 整除）。"""
    result = even_squares(50)
    for num in result:
        # 偶数的平方必然能被 4 整除
        assert num % 4 == 0, f"{num} 不是偶数的平方"


# 如果你对 pytest 失败消息感兴趣，取消注释下面的测试：
# def test_failure_message():
#     """演示失败时的错误信息。"""
#     assert even_squares(10) == [4, 16, 36, 64, 101]  # 预期错误
