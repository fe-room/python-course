"""
test_advanced.py — pytest 进阶特性演示
========================================

展示 pytest 的核心进阶功能：
1. fixture（夹具）— 复用测试数据
2. parametrize（参数化）— 用不同参数运行同一测试

运行方式（在终端中执行）：
    cd day35_pytest && pytest test_advanced.py -v

对于前端工程师：
    - fixture 类似于 Jest 的 beforeEach / beforeAll + 工厂函数
    - parametrize 类似于 Jest 的 test.each([...])("...", ...)
"""

import pytest
from typing import List, Dict


# ==============================================================
# 1. fixture — 使用 conftest.py 中定义的共享夹具
# ==============================================================
# sample_todos 来自 conftest.py，pytest 会自动注入。
# 你不需要 import 它，只需要在函数参数中声明参数名即可。
#
# 对比 Jest:
#   const { sampleTodos } = require('./fixtures');
#   beforeEach(() => { todos = sampleTodos(); });
#
# 在 pytest 中，fixture 是依赖注入 (Dependency Injection) 的方式。
# 测试函数通过参数名 "请求" 它需要的 fixture，pytest 负责提供。


def test_sample_todos_has_three_items(sample_todos):
    """
    验证 sample_todos fixture 返回了 3 个待办事项。
    """
    assert len(sample_todos) == 3


def test_sample_todos_contains_walk_the_dog(sample_todos):
    """
    验证 sample_todos 中包含 "Walk the dog" 事项。

    对比 Jest:
        expect(todos).toContainEqual(
          expect.objectContaining({ title: 'Walk the dog' })
        )
    """
    titles = [todo["title"] for todo in sample_todos]
    assert "Walk the dog" in titles


def test_sample_todos_ids_are_unique(sample_todos):
    """
    验证所有待办事项的 id 都是唯一的。
    """
    ids = [todo["id"] for todo in sample_todos]
    assert len(ids) == len(set(ids)), "IDs must be unique"


def test_empty_todos_returns_empty_list(empty_todos):
    """
    使用另一个 fixture（empty_todos）测试空列表场景。

    一个测试函数可以使用多个 fixture，只需在参数中列出即可：
        def test_something(sample_todos, empty_todos):
    """
    assert empty_todos == []
    assert len(empty_todos) == 0


def test_fixture_scope(sample_todos):
    """
    注意：默认情况下 fixture 是 function 作用域的，
    即每个测试函数都会得到 fixture 返回的一个"新"副本。

    对比 Jest:
        默认每次 beforeEach 都会重新初始化数据，
        与 pytest fixture 的 function 作用域类似。
    """
    # 修改 fixture 数据不会影响其他测试
    sample_todos.append({"id": 4, "title": "Extra item", "done": False})
    assert len(sample_todos) == 4


# ==============================================================
# 2. parametrize — 用多组参数运行同一个测试逻辑
# ==============================================================
# @pytest.mark.parametrize 允许你用不同的输入和预期输出
# 运行同一个测试函数。每个组合都会作为一个独立的测试用例运行。
#
# 对比 Jest:
#   test.each([
#     [1, 2, 3],
#     [4, 5, 9],
#   ])('%i + %i = %i', (a, b, expected) => {
#     expect(a + b).toBe(expected);
#   });


# --------------------------------------------------------------
# 示例 1：测试加法
# --------------------------------------------------------------
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),        # 正数相加
    (0, 0, 0),        # 零加零
    (-1, 1, 0),       # 相反数相加
    (100, 200, 300),  # 大数相加
])
def test_add(a, b, expected):
    """
    参数化测试 — 验证加法结果。
    这 4 组参数会生成 4 个独立的测试用例：
        test_add[1-2-3]
        test_add[0-0-0]
        test_add[-1-1-0]
        test_add[100-200-300]
    """
    assert a + b == expected


# --------------------------------------------------------------
# 示例 2：测试待办事项的完成状态过滤
# --------------------------------------------------------------
@pytest.mark.parametrize("done_status,expected_count", [
    (True, 1),   # 只有 "Finish homework" 是已完成
    (False, 2),  # "Buy groceries" 和 "Walk the dog" 未完成
])
def test_filter_by_done_status(sample_todos, done_status, expected_count):
    """
    参数化测试 — 结合 fixture 使用 parametrize。

    sample_todos fixture 会为每个参数组合注入一次，
    因此 pytest 会运行 2 个测试用例，每个都使用 sample_todos 数据。

    对比 Jest:
        test.each([[true, 1], [false, 2]])(
          'done=%s should return %i items',
          (doneStatus, expectedCount) => {
            const result = todos.filter(t => t.done === doneStatus);
            expect(result).toHaveLength(expectedCount);
          }
        );
    """
    filtered = [t for t in sample_todos if t["done"] == done_status]
    assert len(filtered) == expected_count


# --------------------------------------------------------------
# 示例 3：测试字符串处理
# --------------------------------------------------------------
@pytest.mark.parametrize("text,expected_len", [
    ("hello", 5),
    ("", 0),
    ("a" * 100, 100),
    ("Hello, 世界", 9),  # 中文字符每个算一个长度
])
def test_string_length(text, expected_len):
    """
    参数化测试 — 验证字符串长度。
    """
    assert len(text) == expected_len


# --------------------------------------------------------------
# 示例 4：多个 parametrize 装饰器组合（笛卡尔积）
# --------------------------------------------------------------
@pytest.mark.parametrize("operation", ["upper", "lower"])
@pytest.mark.parametrize("text", ["Hello", "World"])
def test_string_case_combination(text, operation):
    """
    当有多个 @pytest.mark.parametrize 时，
    pytest 会生成所有组合（笛卡尔积）。

    这里会生成 2 * 2 = 4 个测试用例：
        test_string_case_combination[Hello-upper]
        test_string_case_combination[Hello-lower]
        test_string_case_combination[World-upper]
        test_string_case_combination[World-lower]

    对比 Jest:
        // Jest 中需要手动嵌套循环或使用 test.each 的组合
    """
    if operation == "upper":
        assert text.upper() == text.upper()
    else:
        assert text.lower() == text.lower()


# ==============================================================
# 3. 综合示例：测试 Todo 数据的实用函数
# ==============================================================


def get_pending_todos(todos: List[Dict]) -> List[Dict]:
    """返回所有未完成的待办事项。"""
    return [t for t in todos if not t["done"]]


def get_todo_by_id(todos: List[Dict], todo_id: int) -> Dict:
    """根据 ID 查找待办事项，未找到时返回 None。"""
    for t in todos:
        if t["id"] == todo_id:
            return t
    return None


@pytest.mark.parametrize("todo_id,expected_title", [
    (1, "Buy groceries"),
    (2, "Finish homework"),
    (3, "Walk the dog"),
])
def test_get_todo_by_id(sample_todos, todo_id, expected_title):
    """
    综合测试 — 使用 parametrize 测试通过 ID 查找待办事项。
    """
    result = get_todo_by_id(sample_todos, todo_id)
    assert result is not None
    assert result["title"] == expected_title


@pytest.mark.parametrize("todo_id", [999, -1, 0])
def test_get_todo_by_id_not_found(sample_todos, todo_id):
    """
    综合测试 — 测试查找不存在的 ID 时返回 None。
    """
    result = get_todo_by_id(sample_todos, todo_id)
    assert result is None


def test_get_pending_todos(sample_todos):
    """
    综合测试 — 验证 get_pending_todos 只返回未完成的事项。
    """
    pending = get_pending_todos(sample_todos)
    assert len(pending) == 2
    for todo in pending:
        assert todo["done"] is False