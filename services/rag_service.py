from __future__ import annotations

import json
import math
from openai import OpenAI
from config import Config
from database.db import get_connection

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=Config.OPENAI_API_KEY)
    return _client


def get_embedding(text: str) -> list[float]:
    response = _get_client().embeddings.create(
        model="text-embedding-ada-002",
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def save_memory_with_embedding(user_id: int, content: str, emotion: str = None, keyword: str = None):
    embedding = get_embedding(content)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memories (user_id, content, emotion, keyword, embedding) VALUES (?, ?, ?, ?, ?)",
        (user_id, content, emotion, keyword, json.dumps(embedding)),
    )
    conn.commit()
    conn.close()


def get_relevant_memories(user_id: int, query: str, top_k: int = 3) -> str:
    """쿼리와 가장 관련 있는 기억 top_k개를 벡터 유사도로 찾아 반환."""
    query_vec = get_embedding(query)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT content, emotion, embedding FROM memories WHERE user_id = ? AND embedding IS NOT NULL",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        # embedding 없는 기억도 fallback으로 포함
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT content, emotion FROM memories WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, top_k),
        )
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return "등록된 기억이 없습니다."
        return "\n".join(
            f"- {r['content']}" + (f" (감정: {r['emotion']})" if r['emotion'] else "")
            for r in rows
        )

    scored = []
    for row in rows:
        vec = json.loads(row["embedding"])
        score = cosine_similarity(query_vec, vec)
        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    lines = []
    for score, row in top:
        line = f"- {row['content']}"
        if row["emotion"]:
            line += f" (감정: {row['emotion']})"
        lines.append(line)

    return "\n".join(lines)
