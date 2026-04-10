from __future__ import annotations

from flask import Blueprint, request, jsonify
from services.memory_service import save_memory, get_memories
from services.rag_service import save_memory_with_embedding
from database.db import get_connection

memory_bp = Blueprint("memory", __name__, url_prefix="/api")


@memory_bp.route("/memories/<int:user_id>", methods=["GET"])
def list_memories(user_id):
    return jsonify(get_memories(user_id))


@memory_bp.route("/memories", methods=["POST"])
def add_memory():
    data = request.get_json()
    user_id = data.get("user_id")
    content = data.get("content", "").strip()
    emotion = data.get("emotion")
    keyword = data.get("keyword")

    if not user_id or not content:
        return jsonify({"error": "user_id와 content는 필수입니다."}), 400

    # embedding 포함 저장 (RAG용)
    save_memory_with_embedding(user_id, content, emotion, keyword)
    return jsonify({"message": "기억이 저장되었습니다."}), 201


@memory_bp.route("/emotions/<int:user_id>", methods=["GET"])
def emotion_stats(user_id):
    """감정 분포 통계 반환."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT emotion, COUNT(*) as count
        FROM memories
        WHERE user_id = ? AND emotion IS NOT NULL
        GROUP BY emotion
        ORDER BY count DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])
