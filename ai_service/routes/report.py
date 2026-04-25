import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from services.groq_client import GroqClient
from services.sanitiser import sanitise_input

report_bp   = Blueprint("report", __name__)
groq_client = GroqClient()


@report_bp.route("/generate-report", methods=["POST"])
def generate_report():

    # ── Step 1: Check JSON body exists ───────────────────────────────────────
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "error":  "Request body must be valid JSON",
            "status": 400
        }), 400

    # ── Step 2: Check environment field exists ────────────────────────────────
    environment = data.get("environment", "").strip()
    if not environment:
        return jsonify({
            "error":  "'environment' field is required and cannot be empty",
            "status": 400
        }), 400

    # ── Step 3: Check length ──────────────────────────────────────────────────
    if len(environment) > 3000:
        return jsonify({
            "error":  "'environment' field exceeds maximum length of 3000 characters",
            "status": 400
        }), 400

    # ── Step 4: Sanitise input ────────────────────────────────────────────────
    clean, injection_detected = sanitise_input(environment)
    if injection_detected:
        return jsonify({
            "error":  "Invalid input detected. Request rejected.",
            "status": 400
        }), 400

    # ── Step 5: Call Groq and return structured report ────────────────────────
    result = groq_client.generate_report(clean)
    return jsonify(result), 200