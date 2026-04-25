import time
from flask import Blueprint, jsonify

health_bp   = Blueprint("health", __name__)
_start_time = time.time()

@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":         "ok",
        "model":          "llama-3.3-70b-versatile",
        "uptime_seconds": int(time.time() - _start_time),
        "service":        "Tool-59 AI Service"
    }), 200