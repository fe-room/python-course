"""
CRUD 操作 — Repository 模式
封装 Todo 表的所有数据库操作，路由只负责 HTTP 语义。
"""
from sqlalchemy.orm import Session
from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate


class TodoRepository:
    """Todo 表的 Repository，所有数据库读写操作均通过此类完成。"""

    def __init__(self, db: Session):
        """注入 SQLAlchemy Session。"""
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Todo]:
        """获取 Todo 列表，支持分页。"""
        return self.db.query(Todo).offset(skip).limit(limit).all()

    def get_by_id(self, todo_id: int) -> Todo | None:
        """根据主键获取单个 Todo，不存在时返回 None。"""
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

    def create(self, data: TodoCreate) -> Todo:
        """创建新 Todo，提交后刷新返回完整记录。"""
        todo = Todo(**data.model_dump())
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def update(self, todo: Todo, data: TodoUpdate) -> Todo:
        """部分更新已有 Todo，仅修改传入了的字段。"""
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(todo, field, value)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo: Todo) -> None:
        """删除指定 Todo 记录。"""
        self.db.delete(todo)
        self.db.commit()

    def search(self, q: str = "", done: bool | None = None) -> list[Todo]:
        """
        按关键词和/或完成状态搜索 Todo。

        参数
        ----
        q : str
            标题关键词模糊匹配。
        done : bool | None
            过滤完成状态；None 表示不过滤。
        """
        query = self.db.query(Todo)
        if q:
            query = query.filter(Todo.title.contains(q))
        if done is not None:
            query = query.filter(Todo.done == done)
        return query.all()

    def count(self) -> int:
        """返回 Todo 表总记录数。"""
        return self.db.query(Todo).count()
