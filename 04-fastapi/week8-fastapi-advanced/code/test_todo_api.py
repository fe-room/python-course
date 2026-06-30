"""
test_todo_api.py — Todo API 的 CRUD 集成测试
==============================================

测试 day56_testing.py 中定义的 FastAPI Todo API 的所有 CRUD 端点。

运行方式：
    cd week8-fastapi-advanced/code && pytest test_todo_api.py -v

对于前端工程师：
    这个文件展示了独立的测试文件如何导入 API 应用并使用 TestClient 测试。
    不同于 day56_testing.py 中内联的测试，这里演示了"测试文件与代码分离"的
    推荐实践。

对比 Jest:
    // Jest 中通常在 __tests__/ 目录下组织测试文件
    // import app from '../app';
    // const request = require('supertest')(app);
"""

import pytest
from fastapi.testclient import TestClient

# 从 day56_testing.py 导入 FastAPI 应用实例
# TestClient 类似 Jest 的 supertest(request(app))
from day56_testing import app, todos_db, next_id

# --------------------------------------------------------------
# 全局 TestClient 实例 — 所有测试复用同一个 client
# --------------------------------------------------------------
# TestClient 是对 FastAPI 应用的封装，像 supertest 一样无需启动真实服务器。
client = TestClient(app)


# --------------------------------------------------------------
# pytest fixture: 每个测试前重置数据库
# --------------------------------------------------------------
# fixture 就像 Jest 的 beforeEach，但通过依赖注入方式使用。
@pytest.fixture(autouse=True)
def reset_db():
    """每个测试前清空数据库，确保测试隔离（避免测试间互相影响）。"""
    todos_db.clear()
    # 重置 ID 计数器
    # 注意：在 Python 中修改全局整数需要用 global 关键字，
    # 但这里我们直接通过 day56_testing 模块的变量来重置。
    # globals() 方式在 fixture 中不可靠，我们直接通过导入的模块变量操作。
    import day56_testing
    day56_testing.next_id = 1
    yield  # 测试执行到此


# --------------------------------------------------------------
# 辅助函数: 创建一个待办事项并返回其 JSON 数据
# --------------------------------------------------------------
def create_todo(title: str = "Default task", done: bool = False) -> dict:
    """创建一个 Todo 并返回响应 JSON。"""
    response = client.post("/todos", json={"title": title, "done": done})
    assert response.status_code == 201
    return response.json()


# ==============================================================
# 测试用例 — CRUD 全覆盖
# ==============================================================


# --- CREATE ---

class TestCreateTodo:
    """测试创建待办事项的各种场景"""

    def test_create_basic_todo(self):
        """创建最基本的待办事项（只传 title）"""
        response = client.post("/todos", json={"title": "Buy groceries"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["done"] is False  # 默认值
        assert data["id"] == 1       # 自增 ID

    def test_create_todo_with_done_true(self):
        """创建已完成状态的待办事项"""
        response = client.post("/todos", json={"title": "Completed task", "done": True})
        assert response.status_code == 201
        assert response.json()["done"] is True

    def test_create_multiple_todos_auto_increment_id(self):
        """验证 ID 自增"""
        todo1 = create_todo("First")
        todo2 = create_todo("Second")
        todo3 = create_todo("Third")

        assert todo1["id"] == 1
        assert todo2["id"] == 2
        assert todo3["id"] == 3


# --- READ ---

class TestReadTodo:
    """测试查询待办事项的各种场景"""

    def test_list_todos_empty(self):
        """初始状态下待办事项列表为空"""
        response = client.get("/todos")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_todos_after_creation(self):
        """创建后列表包含正确的数据"""
        create_todo("Task 1")
        create_todo("Task 2")

        response = client.get("/todos")
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Task 1"
        assert data[1]["title"] == "Task 2"

    def test_get_todo_by_id(self):
        """根据 ID 获取单个待办事项"""
        created = create_todo("Specific task")
        response = client.get(f"/todos/{created['id']}")
        assert response.status_code == 200
        assert response.json()["title"] == "Specific task"

    def test_get_todo_not_found_returns_404(self):
        """请求不存在的 ID 返回 404"""
        response = client.get("/todos/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"

    def test_get_todo_with_invalid_id_type(self):
        """传入非数字 ID 返回 422（请求体验证失败）"""
        # FastAPI 会根据类型注解自动验证路径参数
        response = client.get("/todos/abc")
        assert response.status_code == 422


# --- UPDATE ---

class TestUpdateTodo:
    """测试更新待办事项的各种场景"""

    def test_update_title(self):
        """更新待办事项的标题"""
        created = create_todo("Old title")
        response = client.put(
            f"/todos/{created['id']}",
            json={"title": "New title", "done": False},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "New title"

    def test_update_done_status(self):
        """更新待办事项的完成状态"""
        created = create_todo("Task", done=False)
        response = client.put(
            f"/todos/{created['id']}",
            json={"title": "Task", "done": True},
        )
        assert response.status_code == 200
        assert response.json()["done"] is True

    def test_update_full_todo(self):
        """同时更新标题和状态"""
        created = create_todo("Original", done=False)
        response = client.put(
            f"/todos/{created['id']}",
            json={"title": "Updated", "done": True},
        )
        data = response.json()
        assert data["title"] == "Updated"
        assert data["done"] is True

    def test_update_non_existent_todo(self):
        """更新不存在的待办事项返回 404"""
        response = client.put(
            "/todos/999",
            json={"title": "Nope", "done": False},
        )
        assert response.status_code == 404


# --- DELETE ---

class TestDeleteTodo:
    """测试删除待办事项的各种场景"""

    def test_delete_existing_todo(self):
        """删除存在的待办事项返回 204"""
        created = create_todo("To be deleted")
        # DELETE 请求应该返回 204 No Content
        response = client.delete(f"/todos/{created['id']}")
        assert response.status_code == 204

    def test_deleted_todo_is_actually_removed(self):
        """确认删除后无法再获取该待办事项"""
        created = create_todo("Gone soon")
        todo_id = created["id"]

        # 删除前可以获取到
        assert client.get(f"/todos/{todo_id}").status_code == 200

        # 执行删除
        client.delete(f"/todos/{todo_id}")

        # 删除后返回 404
        assert client.get(f"/todos/{todo_id}").status_code == 404

    def test_delete_non_existent_todo(self):
        """删除不存在的待办事项返回 404"""
        response = client.delete("/todos/999")
        assert response.status_code == 404


# --- 高级测试场景 ---

class TestAdvancedScenarios:
    """业务场景相关的综合测试"""

    def test_complete_workflow(self):
        """
        模拟一个完整的工作流：创建 -> 验证 -> 更新 -> 验证 -> 删除 -> 验证。
        这类似于 Jest 中的集成测试 (integration test)。
        """
        # 1. 创建
        todo = create_todo("Learn FastAPI testing")
        todo_id = todo["id"]
        assert todo["done"] is False

        # 2. 标记为已完成
        response = client.put(
            f"/todos/{todo_id}",
            json={"title": "Learn FastAPI testing", "done": True},
        )
        assert response.json()["done"] is True

        # 3. 确认列表中状态已更新
        response = client.get(f"/todos/{todo_id}")
        assert response.json()["done"] is True

        # 4. 删除
        client.delete(f"/todos/{todo_id}")
        assert client.get(f"/todos/{todo_id}").status_code == 404

        # 5. 最终列表应为空
        assert client.get("/todos").json() == []

    def test_multiple_todos_isolation(self):
        """
        多个待办事项互不干扰 — 每个都有独立的 ID 和数据。
        """
        t1 = create_todo("Alpha")
        t2 = create_todo("Beta")
        t3 = create_todo("Gamma")

        # 删除 Beta
        client.delete(f"/todos/{t2['id']}")

        # Alpha 和 Gamma 仍然存在
        assert client.get(f"/todos/{t1['id']}").status_code == 200
        assert client.get(f"/todos/{t3['id']}").status_code == 200

        # Beta 已消失
        assert client.get(f"/todos/{t2['id']}").status_code == 404

        # 列表中只有 2 项
        all_todos = client.get("/todos").json()
        assert len(all_todos) == 2