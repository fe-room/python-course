#!/usr/bin/env python3
"""Todo API — 第 4 阶段周项目

运行: uvicorn app.main:app --reload
文档: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ----- 数据模型 -----

class Todo(BaseModel):
    id: int
    title: str
    done: bool = False
    category: str = "general"

class TodoCreate(BaseModel):
    title: str
    category: str = "general"

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# ----- 内存存储 -----

todos: list[Todo] = []
next_id = 1

# ----- FastAPI -----

app = FastAPI(title="Todo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- 路由 -----

@app.get("/todos")
def list_todos(skip: int = 0, limit: int = 20, done: Optional[bool] = None):
    """获取 Todo 列表，支持分页和状态过滤"""
    result = [t for t in todos if done is None or t.done == done]
    return {"total": len(result), "items": result[skip: skip + limit]}


@app.post("/todos", status_code=201)
def create_todo(data: TodoCreate):
    """创建新 Todo"""
    global next_id
    todo = Todo(id=next_id, title=data.title, category=data.category)
    todos.append(todo)
    next_id += 1
    return todo


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    """获取单个 Todo"""
    for t in todos:
        if t.id == todo_id:
            return t
    raise HTTPException(404, "Todo 不存在")


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, data: TodoUpdate):
    """更新 Todo"""
    for t in todos:
        if t.id == todo_id:
            if data.title is not None:
                t.title = data.title
            if data.done is not None:
                t.done = data.done
            return t
    raise HTTPException(404, "Todo 不存在")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """删除 Todo"""
    global todos
    before = len(todos)
    todos = [t for t in todos if t.id != todo_id]
    if len(todos) == before:
        raise HTTPException(404, "Todo 不存在")


@app.get("/stats")
def stats():
    """统计信息"""
    total = len(todos)
    done = sum(1 for t in todos if t.done)
    return {"total": total, "done": done, "pending": total - done}
