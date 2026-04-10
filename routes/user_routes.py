from flask import Blueprint, request, jsonify, session
from services.user_service import create_user, get_user, get_all_users

user_bp = Blueprint("user", __name__, url_prefix="/api")


@user_bp.route("/users", methods=["GET"])
def list_users():
    return jsonify(get_all_users())


@user_bp.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name", "").strip()
    age = data.get("age")

    if not name:
        return jsonify({"error": "이름을 입력해주세요."}), 400

    user_id = create_user(name, age)
    return jsonify({"id": user_id, "name": name, "age": age}), 201


@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user_info(user_id):
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
    return jsonify(user)


@user_bp.route("/session", methods=["POST"])
def set_session():
    data = request.get_json()
    user_id = data.get("user_id")
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
    session["user_id"] = user_id
    return jsonify({"message": f"{user['name']}님 안녕하세요!", "user": user})
