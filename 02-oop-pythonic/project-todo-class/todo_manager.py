#!/usr/bin/env python3
"""Todo Manager — 第 2 阶段周项目

- class 组织代码
- dataclass + Enum
- JSON 持久化
- 分类 / 标签 / 搜索 / 排序
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from typing import Optional


class Status(Enum):
    PENDING = auto()
    DONE = auto()
    ARCHIVED = auto()


@dataclass
class Todo:
    title: str
    status: Status = Status.PENDING
    category: str = "general"
    tags: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    done_at: Optional[datetime] = None
    id: int = 0

    def complete(self):
        if self.status != Status.DONE:
            self.status = Status.DONE
            self.done_at = datetime.now()

    def match(self, keyword: str) -> bool:
        kw = keyword.lower()
        if kw in self.title.lower():
            return True
        return any(kw in t.lower() for t in self.tags)


class TodoManager:
    def __init__(self, path: str = "todos.json"):
        self.path = Path(path)
        self.todos: list[Todo] = []
        self._next_id = 1
        self.load()

    def add(self, title: str, category="general", tags=None) -> Todo:
        todo = Todo(id=self._next_id, title=title, category=category, tags=tags or [])
        self.todos.append(todo)
        self._next_id += 1
        self.save()
        return todo

    def complete(self, todo_id: int) -> Optional[Todo]:
        for t in self.todos:
            if t.id == todo_id:
                t.complete()
                self.save()
                return t
        return None

    def delete(self, todo_id: int) -> bool:
        before = len(self.todos)
        self.todos = [t for t in self.todos if t.id != todo_id]
        if len(self.todos) < before:
            self.save()
            return True
        return False

    def search(self, keyword: str = "") -> list[Todo]:
        if not keyword:
            return self.todos
        return [t for t in self.todos if t.match(keyword)]

    def by_category(self, cat: str) -> list[Todo]:
        return [t for t in self.todos if t.category == cat]

    def stats(self) -> dict:
        total = len(self.todos)
        done = sum(1 for t in self.todos if t.status == Status.DONE)
        return {"total": total, "done": done, "pending": total - done}

    def save(self):
        data = []
        for t in self.todos:
            d = asdict(t)
            d["status"] = t.status.name
            d["created_at"] = t.created_at.isoformat()
            d["done_at"] = t.done_at.isoformat() if t.done_at else None
            data.append(d)
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self):
        if not self.path.exists():
            return
        with open(self.path) as f:
            data = json.load(f)
        self.todos.clear()
        for d in data:
            self.todos.append(Todo(
                id=d["id"],
                title=d["title"],
                status=Status[d["status"]],
                category=d.get("category", "general"),
                tags=d.get("tags", []),
                created_at=datetime.fromisoformat(d["created_at"]),
                done_at=datetime.fromisoformat(d["done_at"]) if d.get("done_at") else None,
            ))
        self._next_id = max((t.id for t in self.todos), default=0) + 1


if __name__ == "__main__":
    mgr = TodoManager()

    while True:
        cmd = input("\n命令 (add/list/done/del/search/stats/quit): ").strip()
        if cmd == "quit":
            break
        elif cmd == "add":
            title = input("标题: ")
            cat = input("分类 [general]: ") or "general"
            tags = input("标签（逗号分隔）: ").split(",") if input("标签? (y/n): ") == "y" else []
            t = mgr.add(title, cat, [x.strip() for x in tags if x.strip()])
            print(f"已添加 #{t.id}")
        elif cmd == "list":
            cat = input("分类过滤（回车全部）: ")
            todos = mgr.by_category(cat) if cat else mgr.todos
            for t in todos:
                status = "✓" if t.status == Status.DONE else " "
                tags = f" [{','.join(t.tags)}]" if t.tags else ""
                print(f"[{status}] {t.id}. {t.title} ({t.category}){tags}")
        elif cmd.startswith("done"):
            mgr.complete(int(cmd.split()[-1]))
        elif cmd.startswith("del"):
            mgr.delete(int(cmd.split()[-1]))
        elif cmd.startswith("search"):
            kw = cmd.split(maxsplit=1)[1] if " " in cmd else input("关键词: ")
            for t in mgr.search(kw):
                print(f"[{t.status.name}] {t.title}")
        elif cmd == "stats":
            s = mgr.stats()
            print(f"总计: {s['total']}, 已完成: {s['done']}, 待办: {s['pending']}")