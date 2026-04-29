import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from services.groq_client import GroqClient
from services.sanitiser import sanitise_input

describe_bp = Blueprint("describe", __name__)
groq_client = GroqClient()

@describe_bp.route("/describe", methods=["POST"])
def describe():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "error": "Request body must be valid JSON",
            "status": 400
        }), 400

    resource = data.get("resource", "").strip()
    if not resource:
        return jsonify({
            "error": "'resource' field is required and cannot be empty",
            "status": 400
        }), 400

    if len(resource) > 2000:
        return jsonify({
            "error": "'resource' field exceeds maximum length of 2000 characters",
            "status": 400
        }), 400

    clean_resource, injection_detected = sanitise_input(resource)
    if injection_detected:
        return jsonify({
            "error": "Invalid input detected. Request rejected.",
            "status": 400
        }), 400

    result = groq_client.describe(clean_resource)
    return jsonify(result), 200