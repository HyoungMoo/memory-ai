from __future__ import annotations

from flask import Blueprint, request, jsonify
from services.session_service import start_session, end_session, get_active_session, get_session_history
from services.ai_service import SESSION_CATEGORIES

session_bp = Blueprint("session", __name__, url_prefix="/api")


@session_bp.route("/sessions/categories", methods=["GET"])
def list_categories():
    return jsonify([
        {"key": k, "label": v} for k, v in SESSION_CATEGORIES.items()
    ])


@session_bp.route("/sessions/start", methods=["POST"])
def start():
    data = request.get_json()
    user_id = data.get("user_id")
    category = data.get("category")
    if not user_id or not category:
        return jsonify({"error": "user_id와 category는 필수입니다."}), 400
    try:
        session = start_session(user_id, category)
        return jsonify(session), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@session_bp.route("/sessions/end", methods=["POST"])
def end():
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id는 필수입니다."}), 400
    end_session(user_id)
    return jsonify({"message": "세션이 종료되었습니다."})


@session_bp.route("/sessions/active/<int:user_id>", methods=["GET"])
def active(user_id):
    session = get_active_session(user_id)
    return jsonify(session)


@session_bp.route("/sessions/history/<int:user_id>", methods=["GET"])
def history(user_id):
    return jsonify(get_session_history(user_id))
