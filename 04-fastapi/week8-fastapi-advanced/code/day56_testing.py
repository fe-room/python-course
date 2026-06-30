"""
Day 56: FastAPI TestClient 测试入门
====================================

演示如何使用 FastAPI 的 TestClient 对 API 端点进行测试。

TestClient 类似于 Jest 中的 supertest / superagent：
    - Jest:  const request = require('supertest')(app);
    - pytest: client = TestClient(app)

运行方式（在终端中执行）：
    pip install fastapi httpx pytest
    # 启动服务: uvicorn day56_testing:app --reload
    # 运行测试: pytest day56_testing.py -v
"""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import List, Optional

# ==============================================================
# 1. 定义数据模型
# ==============================================================


class Todo(BaseModel):
    id: int
    title: str
    done: bool = False


class TodoCreate(BaseModel):
    title: str
    done: bool = False


# ==============================================================
# 2. 创建 FastAPI 应用 + 内存存储
# ==============================================================

app = FastAPI(title="Todo API (Test Demo)")

# 内存存储 — 仅用于演示，重启后数据丢失
todos_db: List[Todo] = []
next_id: int = 1


# ==============================================================
# 3. CRUD 路由
# ==============================================================


@app.get("/todos", response_model=List[Todo])
def list_todos():
    """获取所有待办事项"""
    return todos_db


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    """根据 ID 获取单个待办事项"""
    for todo in todos_db:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    """创建新的待办事项"""
    global next_id
    new_todo = Todo(id=next_id, title=todo.title, done=todo.done)
    todos_db.append(new_todo)
    next_id += 1
    return new_todo


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: TodoCreate):
    """更新待办事项"""
    for i, existing in enumerate(todos_db):
        if existing.id == todo_id:
            updated = Todo(id=todo_id, title=todo.title, done=todo.done)
            todos_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """删除待办事项"""
    for i, todo in enumerate(todos_db):
        if todo.id == todo_id:
            todos_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Todo not found")


# ==============================================================
# 4. 使用 TestClient 编写测试（直接运行此文件即可执行）
# ==============================================================
# pytest 会执行所有 test_* 开头的函数。
# TestClient 会自动管理请求上下文，无需启动服务器。

client = TestClient(app)


def reset_db():
    """每个测试前重置数据库的辅助函数"""
    global todos_db, next_id
    todos_db.clear()
    next_id = 1


def test_list_todos_empty():
    """Test GET /todos returns an empty list initially."""
    reset_db()
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo():
    """Test POST /todos creates a todo and returns it with 201."""
    reset_db()
    response = client.post("/todos", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["done"] is False
    assert data["id"] == 1


def test_list_todos_after_creation():
    """Test GET /todos returns todos after creation."""
    reset_db()
    # 创建两个待办事项
    client.post("/todos", json={"title": "Task A"})
    client.post("/todos", json={"title": "Task B", "done": True})

    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task A"
    assert data[1]["title"] == "Task B"
    assert data[1]["done"] is True


def test_get_todo_by_id():
    """Test GET /todos/{id} returns a specific todo."""
    reset_db()
    created = client.post("/todos", json={"title": "Find me"}).json()

    response = client.get(f"/todos/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


def test_get_todo_not_found():
    """Test GET /todos/{id} returns 404 for non-existent id."""
    reset_db()
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


def test_update_todo():
    """Test PUT /todos/{id} updates an existing todo."""
    reset_db()
    created = client.post("/todos", json={"title": "Old title"}).json()

    response = client.put(
        f"/todos/{created['id']}",
        json={"title": "New title", "done": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["done"] is True


def test_delete_todo():
    """Test DELETE /todos/{id} removes a todo."""
    reset_db()
    created = client.post("/todos", json={"title": "Delete me"}).json()

    response = client.delete(f"/todos/{created['id']}")
    assert response.status_code == 204

    # 确认已被删除
    get_response = client.get(f"/todos/{created['id']}")
    assert get_response.status_code == 404


def test_update_todo_not_found():
    """Test PUT /todos/{id} returns 404 for non-existent id."""
    reset_db()
    response = client.put(
        "/todos/999",
        json={"title": "Nope", "done": False},
    )
    assert response.status_code == 404


def test_delete_todo_not_found():
    """Test DELETE /todos/{id} returns 404 for non-existent id."""
    reset_db()
    response = client.delete("/todos/999")
    assert response.status_code == 404


# 如果直接运行此文件，执行测试
if __name__ == "__main__":
    import sys
    import subprocess
    subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"])