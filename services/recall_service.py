from __future__ import annotations

import random
from database.db import get_connection
from services.ai_service import generate_recall_question, evaluate_recall_answer


def get_random_memory(user_id: int) -> dict | None:
    """회상 테스트용 랜덤 기억 1개 반환."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, content FROM memories WHERE user_id=? AND keyword != '자동요약'",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return None
    return dict(random.choice(rows))


def create_recall_test(user_id: int, session_id: int = None) -> dict | None:
    """기억 하나를 골라 질문을 생성하고 DB에 저장."""
    memory = get_random_memory(user_id)
    if not memory:
        return None

    qa = generate_recall_question(memory["content"])
    question = qa.get("question", "")
    expected = qa.get("expected", "")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO recall_tests (user_id, session_id, memory_id, question, expected)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, session_id, memory["id"], question, expected),
    )
    test_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {"test_id": test_id, "question": question}


def submit_recall_answer(test_id: int, user_answer: str) -> dict:
    """사용자 답변을 평가하고 결과를 DB에 저장."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT question, expected FROM recall_tests WHERE id=?",
        (test_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": "테스트를 찾을 수 없습니다."}

    result = evaluate_recall_answer(row["question"], row["expected"], user_answer)
    success = 1 if result.get("success") else 0

    cur.execute(
        "UPDATE recall_tests SET user_answer=?, success=? WHERE id=?",
        (user_answer, success, test_id),
    )
    conn.commit()
    conn.close()

    return {
        "success": bool(success),
        "feedback": result.get("feedback", ""),
        "expected": row["expected"],
    }


def get_recall_stats(user_id: int, days: int = 7) -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT COUNT(*) as total,
                  SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) as correct
           FROM recall_tests
           WHERE user_id=? AND success IS NOT NULL
             AND created_at >= datetime('now', ?)""",
        (user_id, f"-{days} days"),
    )
    row = cur.fetchone()
    conn.close()
    total = row["total"] or 0
    correct = row["correct"] or 0
    return {
        "total": total,
        "correct": correct,
        "rate": round(correct / total * 100) if total > 0 else 0,
    }
