"""
conftest.py — pytest 共享夹具（Shared Fixtures）
=================================================

conftest.py 中的 fixture 会自动被同目录及子目录下的所有测试文件共享，
无需手动 import。这类似于 Jest 中的 setupFiles / jest.setup.js。

运行方式：
    cd day35_pytest && pytest -v

对于前端工程师：
    conftest.py 类似于 Jest 的 jest.setup.js 或 __mocks__ 目录，
    但 conftest.py 的作用域是基于文件系统目录的。当 pytest 运行
    某个测试文件时，它会自动加载该文件所在目录及所有父目录中的
    conftest.py。
"""

import pytest
from typing import List, Dict


@pytest.fixture
def sample_todos() -> List[Dict[str, object]]:
    """
    返回一组示例 Todo 数据，供多个测试文件复用。

    这个 fixture 的作用类似于 Jest 中的 beforeEach 里准备数据的逻辑，
    或者是工厂函数 (factory function)。

    对比 Jest:
        // Jest 中需要手动在每个测试文件里写：
        // beforeEach(() => { todos = [...] })

        在 pytest 中只需要在 conftest.py 里定义一次 fixture，
        所有测试文件都能通过参数名自动注入使用。

    使用方式：
        在测试函数参数中声明 sample_todos：
            def test_something(sample_todos):
                # sample_todos 就是 fixture 返回的数据
                pass

    Returns:
        List[Dict]: 包含三个待办事项的列表
    """
    return [
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Finish homework", "done": True},
        {"id": 3, "title": "Walk the dog", "done": False},
    ]


@pytest.fixture
def empty_todos() -> List[Dict[str, object]]:
    """
    返回空列表 fixture，用于测试边界情况。

    对比 Jest:
        // Jest 中可能需要两个不同的 beforeEach：
        // let todos = []

        在 pytest 中可以定义多个 fixture，按需选择。
    """
    return []