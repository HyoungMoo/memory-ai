from __future__ import annotations

from database.db import get_connection


def save_memory(user_id: int, content: str, emotion: str = None, keyword: str = None):
    """기억 저장 (embedding은 비동기로 나중에 붙이거나 rag_service 직접 사용)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memories (user_id, content, emotion, keyword) VALUES (?, ?, ?, ?)",
        (user_id, content, emotion, keyword),
    )
    conn.commit()
    conn.close()


def get_memories(user_id: int, limit: int = 10) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT content, emotion, keyword, created_at FROM memories WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_memory_context(user_id: int) -> str:
    memories = get_memories(user_id)
    if not memories:
        return "등록된 기억이 없습니다."
    lines = []
    for m in memories:
        line = f"- {m['content']}"
        if m["emotion"]:
            line += f" (감정: {m['emotion']})"
        lines.append(line)
    return "\n".join(lines)


def save_conversation(user_id: int, role: str, message: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversations (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, role, message),
    )
    conn.commit()
    conn.close()


def get_conversation_count(user_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM conversations WHERE user_id = ? AND role = 'user'",
        (user_id,),
    )
    count = cur.fetchone()[0]
    conn.close()
    return count


def auto_summarize_if_needed(user_id: int, every: int = 10):
    """사용자 발화가 every 배수에 도달할 때마다 자동 요약해서 memories에 저장."""
    count = get_conversation_count(user_id)
    if count > 0 and count % every == 0:
        from services.ai_service import summarize_conversations
        recent = get_recent_conversations(user_id, limit=every * 2)
        summary = summarize_conversations(recent)
        save_memory(user_id, summary, emotion="평온", keyword="자동요약")


def get_recent_conversations(user_id: int, limit: int = 6) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, message FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return list(reversed([dict(row) for row in rows]))
