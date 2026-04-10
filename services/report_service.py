from __future__ import annotations

from database.db import get_connection
from services.recall_service import get_recall_stats


def get_weekly_report(user_id: int) -> dict:
    conn = get_connection()
    cur = conn.cursor()

    # 주간 대화 횟수
    cur.execute(
        """SELECT COUNT(*) as cnt FROM conversations
           WHERE user_id=? AND role='user'
             AND created_at >= datetime('now', '-7 days')""",
        (user_id,),
    )
    chat_count = cur.fetchone()["cnt"]

    # 감정 분포 (memories 기준)
    cur.execute(
        """SELECT emotion, COUNT(*) as cnt FROM memories
           WHERE user_id=? AND emotion IS NOT NULL
           GROUP BY emotion ORDER BY cnt DESC""",
        (user_id,),
    )
    emotions = [dict(r) for r in cur.fetchall()]

    # 세션 이력
    cur.execute(
        """SELECT category, COUNT(*) as cnt FROM sessions
           WHERE user_id=? AND started_at >= datetime('now', '-7 days')
           GROUP BY category ORDER BY cnt DESC""",
        (user_id,),
    )
    session_counts = [dict(r) for r in cur.fetchall()]

    # 일별 대화 수 (최근 7일)
    cur.execute(
        """SELECT date(created_at) as day, COUNT(*) as cnt
           FROM conversations
           WHERE user_id=? AND role='user'
             AND created_at >= datetime('now', '-7 days')
           GROUP BY day ORDER BY day""",
        (user_id,),
    )
    daily_chats = [dict(r) for r in cur.fetchall()]

    conn.close()

    # 회상 테스트 통계
    recall = get_recall_stats(user_id, days=7)

    # 주요 감정 판단
    dominant_emotion = emotions[0]["emotion"] if emotions else "데이터 없음"

    # 활동 수준 판단
    if chat_count >= 14:
        activity = "매우 활발"
    elif chat_count >= 7:
        activity = "활발"
    elif chat_count >= 3:
        activity = "보통"
    else:
        activity = "부족"

    return {
        "chat_count": chat_count,
        "activity": activity,
        "dominant_emotion": dominant_emotion,
        "emotions": emotions,
        "recall": recall,
        "session_counts": session_counts,
        "daily_chats": daily_chats,
    }
