"""
Day 63 - SQLite Todo CRUD（纯 sqlite3 实现）
=============================================
不依赖 SQLAlchemy，直接使用 Python 内置的 sqlite3 模块。
这是从"手写 SQL"到"ORM 使用"的过渡练习。

功能：创建、查看、完成、删除、搜索待办事项。

运行方式：python3 day63_sqlite_todo.py
"""

import sqlite3
import sys
from datetime import datetime

# 数据库文件名
DB_FILE = "todo.db"


# ============================================================
# 数据库初始化
# ============================================================

def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 让查询结果支持按列名访问
    return conn


def init_db():
    """初始化数据库，创建 todos 表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            priority    TEXT    DEFAULT 'medium'
                            CHECK(priority IN ('low', 'medium', 'high')),
            completed   INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now', 'localtime')),
            updated_at  TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    conn.close()


# ============================================================
# CRUD 函数
# ============================================================

def create_todo(title, description="", priority="medium"):
    """
    创建待办事项。

    参数：
      title       - 标题（必填）
      description - 描述（可选）
      priority    - 优先级：low / medium / high（默认 medium）

    返回值：新创建的待办 ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, priority) VALUES (?, ?, ?)",
        (title, description, priority)
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    print(f"[创建成功] id={todo_id}, title='{title}', priority={priority}")
    return todo_id


def list_todos(show_all=False):
    """
    列出待办事项。

    参数：
      show_all - True=显示全部, False=只显示未完成的
    """
    conn = get_connection()
    cursor = conn.cursor()

    if show_all:
        cursor.execute("""
            SELECT id, title, description, priority, completed, created_at
            FROM todos
            ORDER BY
                CASE priority
                    WHEN 'high'   THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low'    THEN 3
                END,
                created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT id, title, description, priority, completed, created_at
            FROM todos
            WHERE completed = 0
            ORDER BY
                CASE priority
                    WHEN 'high'   THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low'    THEN 3
                END,
                created_at DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("（当前没有待办事项）")
        return []

    print(f"\n{'=' * 60}")
    status_text = "全部待办" if show_all else "未完成待办"
    print(f"  {status_text} — 共 {len(rows)} 项")
    print(f"{'=' * 60}")
    for row in rows:
        status = "✓" if row["completed"] else "○"
        priority_map = {"high": "🔴高", "medium": "🟡中", "low": "🟢低"}
        pri = priority_map.get(row["priority"], row["priority"])
        desc = f" — {row['description']}" if row["description"] else ""
        print(f"  [{status}] #{row['id']:3d} [{pri}] {row['title']}{desc}")
        print(f"         创建于 {row['created_at']}")
    print(f"{'=' * 60}\n")
    return rows


def complete_todo(todo_id):
    """
    将待办标记为已完成。

    参数：
      todo_id - 待办 ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE todos SET completed = 1, updated_at = datetime('now', 'localtime') WHERE id = ?",
        (todo_id,)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()

    if affected > 0:
        print(f"[完成] id={todo_id} 已标记为完成")
    else:
        print(f"[警告] id={todo_id} 不存在，请检查")
    return affected > 0


def delete_todo(todo_id):
    """
    删除待办事项。

    参数：
      todo_id - 待办 ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()

    if affected > 0:
        print(f"[删除成功] id={todo_id} 已删除")
    else:
        print(f"[警告] id={todo_id} 不存在，请检查")
    return affected > 0


def search_todos(keyword):
    """
    搜索待办事项。
    模糊匹配标题和描述（LIKE 查询）。

    参数：
      keyword - 搜索关键词
    """
    conn = get_connection()
    cursor = conn.cursor()
    like_pattern = f"%{keyword}%"
    cursor.execute(
        """
        SELECT id, title, description, priority, completed, created_at
        FROM todos
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY created_at DESC
        """,
        (like_pattern, like_pattern)
    )
    rows = cursor.fetchall()
    conn.close()

    print(f"\n搜索关键词: '{keyword}' — 找到 {len(rows)} 项结果")
    if rows:
        for row in rows:
            status = "✓" if row["completed"] else "○"
            print(f"  [{status}] #{row['id']} {row['title']}")
    else:
        print("  （无匹配结果）")
    return rows


def stats():
    """显示待办事项统计信息"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM todos")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 0")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 1")
    done = cursor.fetchone()[0]

    conn.close()

    print(f"\n{'=' * 40}")
    print(f"  统计信息")
    print(f"{'=' * 40}")
    print(f"  总计：        {total}")
    print(f"  待完成：      {pending}")
    print(f"  已完成：      {done}")
    if total > 0:
        completion = done / total * 100
        print(f"  完成率：      {completion:.1f}%")
    print(f"{'=' * 40}\n")


# ============================================================
# 交互式命令行界面（CLI）
# ============================================================

def print_help():
    """打印帮助信息"""
    print("""
┌─────────────────────────────────────────────────────┐
│  Todo CLI 命令列表                                  │
├─────────────────────────────────────────────────────┤
│  add <标题>         — 添加待办（默认优先级 medium） │
│  add <标题> -p high  — 添加高优先级待办             │
│  add <标题> -d <描述>— 添加待办并附加描述           │
│  list               — 列出未完成的待办              │
│  list --all         — 列出所有待办（含已完成）      │
│  done <id>          — 标记待办为已完成              │
│  delete <id>        — 删除待办                      │
│  search <关键词>    — 搜索待办                      │
│  stats              — 显示统计信息                  │
│  help               — 显示此帮助                    │
│  exit / quit        — 退出程序                      │
└─────────────────────────────────────────────────────┘
    """)


def run_cli():
    """运行交互式命令行界面"""
    init_db()
    print(f"Todo 管理器 | 数据库: {DB_FILE}")
    print("输入 help 查看命令列表")

    while True:
        try:
            cmd_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not cmd_input:
            continue

        parts = cmd_input.split()
        command = parts[0].lower()

        if command in ("exit", "quit", "q"):
            print("再见！")
            break

        elif command == "help":
            print_help()

        elif command == "add":
            # 解析参数
            title_parts = []
            description = ""
            priority = "medium"
            i = 1
            while i < len(parts):
                if parts[i] == "-p" and i + 1 < len(parts):
                    i += 1
                    priority = parts[i]
                    if priority not in ("low", "medium", "high"):
                        print(f"[错误] 无效优先级: {priority}，使用 medium")
                        priority = "medium"
                elif parts[i] == "-d" and i + 1 < len(parts):
                    i += 1
                    description = parts[i]
                else:
                    title_parts.append(parts[i])
                i += 1
            if not title_parts:
                print("[错误] 请输入标题")
                continue
            title = " ".join(title_parts)
            create_todo(title, description, priority)

        elif command.startswith("list") and "--all" in parts:
            list_todos(show_all=True)

        elif command == "list":
            list_todos(show_all=False)

        elif command == "done":
            if len(parts) < 2:
                print("[错误] 请指定 ID，例如: done 1")
                continue
            try:
                todo_id = int(parts[1])
                complete_todo(todo_id)
            except ValueError:
                print("[错误] ID 必须是数字")

        elif command == "delete":
            if len(parts) < 2:
                print("[错误] 请指定 ID，例如: delete 1")
                continue
            try:
                todo_id = int(parts[1])
                delete_todo(todo_id)
            except ValueError:
                print("[错误] ID 必须是数字")

        elif command == "search":
            if len(parts) < 2:
                print("[错误] 请输入搜索关键词")
                continue
            keyword = " ".join(parts[1:])
            search_todos(keyword)

        elif command == "stats":
            stats()

        else:
            print(f"[错误] 未知命令: {command}")
            print("输入 help 查看可用命令")


# ============================================================
# 演示模式（自动执行示例操作）
# ============================================================

def demo():
    """自动演示所有功能"""
    print("=" * 60)
    print("  Todo CRUD 演示（纯 sqlite3 实现）")
    print("=" * 60)

    init_db()

    # 1. 创建
    print("\n--- [1] 创建待办事项 ---")
    create_todo("完成 Python 课程作业", "第 63 天 SQLite Todo 练习", "high")
    create_todo("购买日用品", "牛奶、面包、鸡蛋", "medium")
    create_todo("健身", "跑步 5 公里", "low")
    create_todo("阅读《Python 核心编程》", "第 10 章", "medium")
    create_todo("写周报", "", "high")

    # 2. 列表
    print("\n--- [2] 列出待办（未完成） ---")
    list_todos()

    # 3. 完成
    print("\n--- [3] 完成待办 ---")
    complete_todo(1)
    complete_todo(3)

    # 4. 搜索
    print("\n--- [4] 搜索待办 ---")
    search_todos("Python")
    search_todos("健身")

    # 5. 统计
    print("\n--- [5] 统计信息 ---")
    stats()

    # 6. 列出全部
    print("\n--- [6] 列出全部（含已完成） ---")
    list_todos(show_all=True)

    # 7. 删除
    print("\n--- [7] 删除待办 ---")
    delete_todo(5)
    list_todos(show_all=True)

    # 清理演示数据
    import os
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"\n[清理] 已删除演示数据库 {DB_FILE}")

    print(f"\n{'=' * 60}")
    print("  演示结束！运行 python3 day63_sqlite_todo.py 进入交互模式。")
    print("=" * 60)


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    # 如果命令行有参数，进入交互式模式；否则运行演示
    if len(sys.argv) > 1:
        # 非交互模式：执行单个命令
        init_db()
        cmd = " ".join(sys.argv[1:])
        print(f"执行: {cmd}")
        # 简单处理 single command
        if cmd.startswith("add "):
            rest = cmd[4:]
            title = rest
            create_todo(title)
        elif cmd == "list":
            list_todos(show_all=True)
        elif cmd.startswith("done "):
            complete_todo(int(cmd.split()[1]))
        elif cmd.startswith("delete "):
            delete_todo(int(cmd.split()[1]))
        else:
            run_cli()
    else:
        # 没有参数 → 运行演示
        demo()
