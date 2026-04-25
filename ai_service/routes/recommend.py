import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from services.groq_client import GroqClient
from services.sanitiser import sanitise_input

recommend_bp = Blueprint("recommend", __name__)
groq_client  = GroqClient()


@recommend_bp.route("/recommend", methods=["POST"])
def recommend():

    # ── Step 1: Check JSON body exists ───────────────────────────────────────
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "error":  "Request body must be valid JSON",
            "status": 400
        }), 400

    # ── Step 2: Check resource field exists ──────────────────────────────────
    resource = data.get("resource", "").strip()
    if not resource:
        return jsonify({
            "error":  "'resource' field is required and cannot be empty",
            "status": 400
        }), 400

    # ── Step 3: Check length ──────────────────────────────────────────────────
    if len(resource) > 2000:
        return jsonify({
            "error":  "'resource' field exceeds maximum length of 2000 characters",
            "status": 400
        }), 400

    # ── Step 4: Sanitise input ────────────────────────────────────────────────
    clean, injection_detected = sanitise_input(resource)
    if injection_detected:
        return jsonify({
            "error":  "Invalid input detected. Request rejected.",
            "status": 400
        }), 400

    # ── Step 5: Call Groq and return 3 recommendations ───────────────────────
    result = groq_client.recommend(clean)
    return jsonify(result), 200