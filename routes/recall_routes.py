from __future__ import annotations

from flask import Blueprint, request, jsonify
from services.recall_service import create_recall_test, submit_recall_answer, get_recall_stats

recall_bp = Blueprint("recall", __name__, url_prefix="/api")


@recall_bp.route("/recall/question", methods=["POST"])
def question():
    data = request.get_json()
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    if not user_id:
        return jsonify({"error": "user_id는 필수입니다."}), 400

    test = create_recall_test(user_id, session_id)
    if not test:
        return jsonify({"error": "등록된 기억이 없어 테스트를 만들 수 없습니다."}), 404
    return jsonify(test)


@recall_bp.route("/recall/answer", methods=["POST"])
def answer():
    data = request.get_json()
    test_id = data.get("test_id")
    user_answer = data.get("answer", "").strip()
    if not test_id or not user_answer:
        return jsonify({"error": "test_id와 answer는 필수입니다."}), 400

    result = submit_recall_answer(test_id, user_answer)
    return jsonify(result)


@recall_bp.route("/recall/stats/<int:user_id>", methods=["GET"])
def stats(user_id):
    days = int(request.args.get("days", 7))
    return jsonify(get_recall_stats(user_id, days))
