from __future__ import annotations

from database.db import get_connection
from services.ai_service import SESSION_CATEGORIES


def start_session(user_id: int, category: str) -> dict:
    """새 회상 세션 시작. 기존 active 세션은 종료."""
    if category not in SESSION_CATEGORIES:
        raise ValueError(f"유효하지 않은 카테고리: {category}")

    conn = get_connection()
    cur = conn.cursor()

    # 기존 active 세션 종료
    cur.execute(
        "UPDATE sessions SET status='ended', ended_at=CURRENT_TIMESTAMP WHERE user_id=? AND status='active'",
        (user_id,),
    )

    cur.execute(
        "INSERT INTO sessions (user_id, category, status) VALUES (?, ?, 'active')",
        (user_id, category),
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {"session_id": session_id, "category": category, "label": SESSION_CATEGORIES[category]}


def end_session(user_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE sessions SET status='ended', ended_at=CURRENT_TIMESTAMP WHERE user_id=? AND status='active'",
        (user_id,),
    )
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_active_session(user_id: int) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM sessions WHERE user_id=? AND status='active' ORDER BY started_at DESC LIMIT 1",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["label"] = SESSION_CATEGORIES.get(d["category"], d["category"])
    return d


def get_session_history(user_id: int, limit: int = 10) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM sessions WHERE user_id=? ORDER BY started_at DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["label"] = SESSION_CATEGORIES.get(d["category"], d["category"])
        result.append(d)
    return result
