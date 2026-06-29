#!/usr/bin/env python3
"""Todo API + SQLAlchemy — 第 5 阶段周项目

运行: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, get_db, Base
from .models import Todo as TodoModel
from .schemas import TodoCreate, TodoUpdate, TodoResponse

Base.metadata.create_all(engine)

app = FastAPI(title="Todo API (DB)", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/todos", response_model=list[TodoResponse])
def list_todos(skip: int = 0, limit: int = 20, done: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(TodoModel)
    if done is not None:
        query = query.filter(TodoModel.done == done)
    return query.offset(skip).limit(limit).all()


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(data: TodoCreate, db: Session = Depends(get_db)):
    todo = TodoModel(title=data.title, category=data.category)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(TodoModel, todo_id)
    if not todo:
        raise HTTPException(404)
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, data: TodoUpdate, db: Session = Depends(get_db)):
    todo = db.get(TodoModel, todo_id)
    if not todo:
        raise HTTPException(404)
    if data.title is not None:
        todo.title = data.title
    if data.done is not None:
        todo.done = data.done
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(TodoModel, todo_id)
    if not todo:
        raise HTTPException(404)
    db.delete(todo)
    db.commit()
