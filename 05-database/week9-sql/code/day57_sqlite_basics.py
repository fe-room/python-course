"""
Day 57 - SQLite 基础操作
=========================
使用 Python 内置 sqlite3 模块操作 SQLite 数据库。
重点：参数化查询（? 占位符）防止 SQL 注入攻击。

运行方式：python3 day57_sqlite_basics.py
"""

import sqlite3


def create_table(cursor):
    """创建学生表"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            age         INTEGER NOT NULL,
            grade       TEXT    NOT NULL,
            enrolled_at TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] 表 students 已创建")


def insert_student(cursor, name, age, grade):
    """
    参数化插入 — 使用 ? 占位符
    永远不要用 f-string 拼接 SQL！否则会导致 SQL 注入攻击。
    """
    sql = "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)"
    cursor.execute(sql, (name, age, grade))
    print(f"[OK] 插入学生：{name}")


def insert_many_students(cursor, students_list):
    """批量插入 — executemany 同样使用参数化"""
    sql = "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)"
    cursor.executemany(sql, students_list)
    print(f"[OK] 批量插入 {len(students_list)} 条记录")


def select_all(cursor):
    """查询所有学生"""
    cursor.execute("SELECT id, name, age, grade, enrolled_at FROM students")
    rows = cursor.fetchall()
    print(f"\n[全体学生] 共 {len(rows)} 人")
    for row in rows:
        print(f"  id={row[0]}, name={row[1]}, age={row[2]}, grade={row[3]}, enrolled={row[4]}")
    return rows


def select_by_grade(cursor, grade):
    """按年级筛选 — 参数化 WHERE"""
    sql = "SELECT id, name, age, grade FROM students WHERE grade = ?"
    cursor.execute(sql, (grade,))
    rows = cursor.fetchall()
    print(f"\n[按年级筛选] grade={grade}，共 {len(rows)} 人")
    for row in rows:
        print(f"  id={row[0]}, name={row[1]}, age={row[2]}, grade={row[3]}")
    return rows


def unsafe_query(cursor, name):
    """
    演示 SQL 注入风险（仅供教学演示，请勿用于实际项目）
    当 name = "' OR '1'='1" 时，会返回所有记录！
    """
    # 危险写法 — 永远不要这样写！
    sql = f"SELECT id, name, age, grade FROM students WHERE name = '{name}'"
    print(f"\n[危险] 执行拼接 SQL：{sql}")
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"[危险] 返回了 {len(rows)} 条记录（预期只返回 1 条）")
    return rows


def safe_query(cursor, name):
    """安全查询 — 参数化写法可以免疫 SQL 注入"""
    sql = "SELECT id, name, age, grade FROM students WHERE name = ?"
    cursor.execute(sql, (name,))
    rows = cursor.fetchall()
    print(f"\n[安全] 参数化查询返回 {len(rows)} 条记录")
    return rows


def main():
    # 使用 :memory: 内存数据库，无需创建文件，测试完毕后自动销毁
    print("=" * 50)
    print("SQLite 基础操作演示（:memory: 数据库）")
    print("=" * 50)

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # 1. 建表
    create_table(cursor)

    # 2. 插入单条数据
    insert_student(cursor, "张三", 20, "A")
    insert_student(cursor, "李四", 22, "B")
    insert_student(cursor, "王五", 21, "A")

    # 3. 批量插入
    students = [
        ("赵六", 23, "B"),
        ("孙七", 19, "A"),
        ("周八", 20, "C"),
    ]
    insert_many_students(cursor, students)

    # 4. 提交事务
    conn.commit()

    # 5. 查询
    select_all(cursor)
    select_by_grade(cursor, "A")

    # 6. SQL 注入演示
    malicious_name = "' OR '1'='1"  # 恶意输入
    unsafe_query(cursor, malicious_name)
    safe_query(cursor, malicious_name)  # 安全版本会返回空结果

    # 7. 关闭连接
    conn.close()
    print("\n[完成] 数据库连接已关闭")


if __name__ == "__main__":
    main()
