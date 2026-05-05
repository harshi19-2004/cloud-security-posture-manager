import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")


def create_app():
    app = Flask(__name__)

    # ── Rate limiter ──────────────────────────────────────────────────────────
    Limiter(
        get_remote_address,
        app=app,
        default_limits=["30 per minute"],
        storage_uri="memory://",
    )

    # ── Register blueprints ───────────────────────────────────────────────────
    from routes.describe  import describe_bp
    from routes.recommend import recommend_bp
    from routes.report    import report_bp
    from routes.health    import health_bp

    app.register_blueprint(describe_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(health_bp)

    # ── Apply security headers ────────────────────────────────────────────────
    from services.security_headers import apply_security_headers

    @app.after_request
    def add_security_headers(response):
        return apply_security_headers(response)

    # ── Pre-load sentence-transformers ────────────────────────────────────────
    from services.embeddings import preload_at_startup
    preload_at_startup()

    # ── Seed ChromaDB at startup ──────────────────────────────────────────────
    from services.chroma_seeder import seed_chromadb
    seed_chromadb()

    # ── Root route ────────────────────────────────────────────────────────────
    @app.route("/", methods=["GET"])
    def home():
        from services.embeddings   import is_model_loaded
        from services.chroma_seeder import get_seeded_count
        return jsonify({
            "message":        "Tool-59 AI Service is running",
            "status":         "ok",
            "model_loaded":   is_model_loaded(),
            "chroma_docs":    get_seeded_count(),
            "endpoints": [
                "POST /describe",
                "POST /recommend",
                "POST /generate-report",
                "GET  /health"
            ]
        }), 200

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found", "status": 404}), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Rate limit exceeded", "status": 429}), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error", "status": 500}), 500

    return app


app = create_app()

if __name__ == "__main__":
    port  = int(os.getenv("AI_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"[Tool-59 AI Service] Starting on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug)