from __future__ import annotations

from flask import Blueprint, request, jsonify, session
from services.ai_service import generate_response, analyze_emotion
from services.memory_service import save_conversation, auto_summarize_if_needed
from services.rag_service import get_relevant_memories
from services.session_service import get_active_session
from services.user_service import get_user
from utils.image_search import get_image_by_keyword

chat_bp = Blueprint("chat", __name__, url_prefix="/api")


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    user_id = data.get("user_id") or session.get("user_id")

    if not user_input:
        return jsonify({"error": "메시지를 입력해주세요."}), 400
    if not user_id:
        return jsonify({"error": "사용자를 먼저 선택해주세요."}), 400

    user = get_user(user_id)
    if not user:
        return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

    # 활성 세션 확인
    active_session = get_active_session(user_id)
    session_category = active_session["category"] if active_session else None

    # 감정 분석 + RAG 기억 검색
    emotion = analyze_emotion(user_input)
    memory_context = get_relevant_memories(user_id, query=user_input, top_k=3)

    # 세션 카테고리 인식 응답 생성
    answer = generate_response(
        user_input, memory_context, user["name"],
        session_category=session_category,
    )

    save_conversation(user_id, "user", user_input)
    save_conversation(user_id, "assistant", answer)
    auto_summarize_if_needed(user_id)

    image = get_image_by_keyword(user_input, user_id=user_id)

    return jsonify({
        "response": answer,
        "emotion": emotion,
        "image": image,
        "session": {"category": session_category, "label": active_session["label"]} if active_session else None,
    })
