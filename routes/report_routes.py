from __future__ import annotations

from flask import Blueprint, request, jsonify
from services.report_service import get_weekly_report

report_bp = Blueprint("report", __name__, url_prefix="/api")


@report_bp.route("/report/<int:user_id>", methods=["GET"])
def report(user_id):
    return jsonify(get_weekly_report(user_id))
