import os
from flask import Blueprint, request, jsonify, current_app
from utils.image_search import save_user_image, get_user_images

image_bp = Blueprint("image", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@image_bp.route("/images/<int:user_id>", methods=["GET"])
def list_images(user_id):
    return jsonify(get_user_images(user_id))


@image_bp.route("/images/upload", methods=["POST"])
def upload_image():
    user_id = request.form.get("user_id")
    keyword = request.form.get("keyword", "").strip()
    description = request.form.get("description", "").strip()
    file = request.files.get("file")

    if not user_id or not keyword or not file:
        return jsonify({"error": "user_id, keyword, file은 필수입니다."}), 400
    if not _allowed(file.filename):
        return jsonify({"error": "허용되지 않는 파일 형식입니다."}), 400

    upload_dir = os.path.join(
        current_app.root_path, "static", "images", "users", str(user_id)
    )
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{keyword}_{file.filename}"
    file.save(os.path.join(upload_dir, filename))

    save_user_image(int(user_id), keyword, filename, description or None)

    return jsonify({"message": "사진이 저장되었습니다.", "filename": filename}), 201
