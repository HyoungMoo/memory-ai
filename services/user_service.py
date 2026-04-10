from __future__ import annotations

from database.db import get_connection


def create_user(name: str, age: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user(user_id: int) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
