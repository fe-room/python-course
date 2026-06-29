#!/usr/bin/env python3
"""CLI Todo List — 第 1 阶段周项目

用法:
    python todo.py add "学习 Python"
    python todo.py list
    python todo.py done 1
    python todo.py del 1
"""

import json, sys
from pathlib import Path

DATA_FILE = Path(__file__).parent / "todos.json"


def load():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        return json.load(f)


def save(todos):
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def cmd_add(title):
    todos = load()
    todo = {
        "id": len(todos) + 1,
        "title": title,
        "done": False,
    }
    todos.append(todo)
    save(todos)
    print(f"已添加: {title}")


def cmd_list():
    todos = load()
    if not todos:
        print("暂无待办事项")
        return
    for t in todos:
        status = "✓" if t["done"] else " "
        print(f"[{status}] {t['id']}. {t['title']}")


def cmd_done(todo_id):
    todos = load()
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = True
            save(todos)
            print(f"已完成: {t['title']}")
            return
    print("未找到该待办")


def cmd_delete(todo_id):
    todos = load()
    todos = [t for t in todos if t["id"] != todo_id]
    save(todos)
    print(f"已删除 #{todo_id}")


def cmd_search(keyword):
    todos = load()
    kw = keyword.lower()
    found = [t for t in todos if kw in t["title"].lower()]
    if not found:
        print("无匹配结果")
        return
    for t in found:
        status = "✓" if t["done"] else " "
        print(f"[{status}] {t['id']}. {t['title']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("用法: todo.py <add|list|done|del|search> [参数]")
        sys.exit(1)

    cmd, *rest = args
    if cmd == "add":
        cmd_add(" ".join(rest))
    elif cmd == "list":
        cmd_list()
    elif cmd == "done" and rest:
        cmd_done(int(rest[0]))
    elif cmd == "del" and rest:
        cmd_delete(int(rest[0]))
    elif cmd == "search" and rest:
        cmd_search(" ".join(rest))
    else:
        print(f"未知命令或参数缺失: {cmd}")