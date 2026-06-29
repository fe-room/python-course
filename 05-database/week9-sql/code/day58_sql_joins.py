"""
Day 58 - SQL JOIN 与聚合查询
=============================
创建 users + orders 两张表，演示 LEFT JOIN、GROUP BY 和聚合函数。

运行方式：python3 day58_sql_joins.py
"""

import sqlite3


def setup_database(cursor):
    """创建 users 和 orders 表，并插入示例数据"""
    # --- 用户表 ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            city    TEXT    NOT NULL
        )
    """)

    # --- 订单表（通过 user_id 关联 users） ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            product     TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            order_date  TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 插入用户
    users_data = [
        ("张三", "北京"),
        ("李四", "上海"),
        ("王五", "北京"),
        ("赵六", "广州"),
        ("孙七", "深圳"),
    ]
    cursor.executemany("INSERT INTO users (name, city) VALUES (?, ?)", users_data)

    # 插入订单（注意：孙七(user_id=5) 没有订单）
    orders_data = [
        (1, "笔记本电脑", 5999.00, "2024-01-15"),   # 张三
        (1, "鼠标",       199.00,  "2024-02-20"),   # 张三
        (2, "键盘",       399.00,  "2024-03-10"),   # 李四
        (3, "显示器",     1299.00, "2024-03-15"),   # 王五
        (3, "耳机",       299.00,  "2024-04-01"),   # 王五
        (3, "摄像头",     499.00,  "2024-04-10"),   # 王五
        (4, "平板电脑",   2999.00, "2024-05-01"),   # 赵六
        (1, "充电器",     99.00,   "2024-05-12"),   # 张三
    ]
    cursor.executemany(
        "INSERT INTO orders (user_id, product, amount, order_date) VALUES (?, ?, ?, ?)",
        orders_data
    )

    print(f"[OK] 已插入 {len(users_data)} 位用户, {len(orders_data)} 条订单\n")


def query_inner_join(cursor):
    """
    INNER JOIN：只返回有订单的用户
    """
    sql = """
        SELECT users.name, orders.product, orders.amount, orders.order_date
        FROM users
        INNER JOIN orders ON users.id = orders.user_id
        ORDER BY users.name, orders.order_date
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"[INNER JOIN] 有订单记录的用户 — {len(rows)} 条")
    for row in rows:
        print(f"  {row[0]} | {row[1]} | ¥{row[2]:>7.2f} | {row[3]}")
    return rows


def query_left_join(cursor):
    """
    LEFT JOIN：返回所有用户，没有订单的用户显示 NULL
    """
    sql = """
        SELECT users.name, orders.product, orders.amount
        FROM users
        LEFT JOIN orders ON users.id = orders.user_id
        ORDER BY users.name
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"\n[LEFT JOIN] 所有用户（含无订单用户）— {len(rows)} 条")
    for row in rows:
        product = row[1] if row[1] else "(无订单)"
        amount = f"¥{row[2]:>7.2f}" if row[2] else "    -"
        print(f"  {row[0]:<4} | {product:<10} | {amount}")
    return rows


def query_left_join_group_by(cursor):
    """
    LEFT JOIN + GROUP BY + 聚合函数
    统计每位用户的：订单数、总金额、平均金额
    """
    sql = """
        SELECT
            users.id,
            users.name,
            users.city,
            COUNT(orders.id)                    AS order_count,
            COALESCE(SUM(orders.amount), 0)     AS total_amount,
            COALESCE(ROUND(AVG(orders.amount), 2), 0) AS avg_amount,
            COALESCE(MAX(orders.amount), 0)     AS max_amount
        FROM users
        LEFT JOIN orders ON users.id = orders.user_id
        GROUP BY users.id
        ORDER BY total_amount DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"\n[LEFT JOIN + GROUP BY] 每位用户的订单统计")
    print(f"  {'ID':<3} {'姓名':<4} {'城市':<4} {'订单数':<6} {'总金额':<10} {'平均金额':<10} {'最大单笔':<10}")
    print(f"  {'-'*47}")
    for row in rows:
        print(f"  {row[0]:<3} {row[1]:<4} {row[2]:<4} {row[3]:<6} ¥{row[4]:<8.2f} ¥{row[5]:<8.2f} ¥{row[6]:<8.2f}")
    return rows


def query_having(cursor):
    """
    HAVING：对 GROUP BY 后的结果进行过滤
    找出总消费超过 1000 的用户
    """
    sql = """
        SELECT
            users.name,
            COUNT(orders.id)    AS order_count,
            SUM(orders.amount)  AS total_amount
        FROM users
        LEFT JOIN orders ON users.id = orders.user_id
        GROUP BY users.id
        HAVING total_amount > 1000
        ORDER BY total_amount DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(f"\n[HAVING] 总消费 > ¥1000 的用户")
    for row in rows:
        print(f"  {row[0]:<4} | {row[1]} 笔订单 | 合计 ¥{row[2]:.2f}")
    return rows


def main():
    print("=" * 55)
    print("SQL JOIN 与聚合查询演示（:memory: 数据库）")
    print("=" * 55)

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # 1. 建表 & 插入数据
    setup_database(cursor)
    conn.commit()

    # 2. INNER JOIN
    query_inner_join(cursor)

    # 3. LEFT JOIN
    query_left_join(cursor)

    # 4. LEFT JOIN + GROUP BY + 聚合
    query_left_join_group_by(cursor)

    # 5. HAVING 过滤
    query_having(cursor)

    conn.close()
    print(f"\n{'=' * 55}")
    print("演示结束。观察 JOIN 如何关联多张表，")
    print("GROUP BY 如何分组，NULL 值的处理方式。")
    print("=" * 55)


if __name__ == "__main__":
    main()
