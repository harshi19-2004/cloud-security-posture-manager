"""
embeddings.py
Day 11 — AI Developer 1

Pre-loads sentence-transformers model at startup.
This makes first AI request faster — model is ready before
anyone sends a request.
"""

import logging
import threading

logger = logging.getLogger(__name__)

# Global model variable
_model        = None
_model_loaded = False
_model_lock   = threading.Lock()

MODEL_NAME = "all-MiniLM-L6-v2"


def load_model():
    """
    Load sentence-transformers model.
    Called once at startup in background thread.
    """
    global _model, _model_loaded

    with _model_lock:
        if _model_loaded:
            return _model

        try:
            logger.info(f"Loading sentence-transformers model: {MODEL_NAME}")
            from sentence_transformers import SentenceTransformer
            _model        = SentenceTransformer(MODEL_NAME)
            _model_loaded = True
            logger.info("sentence-transformers model loaded successfully!")
            return _model

        except Exception as e:
            logger.error(f"Failed to load sentence-transformers: {e}")
            _model_loaded = False
            return None


def get_model():
    """
    Get the loaded model.
    Returns None if model not loaded yet.
    """
    return _model


def is_model_loaded() -> bool:
    """Check if model is loaded and ready."""
    return _model_loaded


def encode_text(text: str) -> list | None:
    """
    Convert text to vector using sentence-transformers.
    Returns list of floats or None if model not ready.
    """
    model = get_model()
    if model is None:
        logger.warning("encode_text called but model not loaded yet")
        return None

    try:
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"encode_text failed: {e}")
        return None


def preload_at_startup():
    """
    Called at app startup — loads model in background thread.
    App starts immediately, model loads in background.
    """
    thread = threading.Thread(
        target=load_model,
        daemon=True,
        name="sentence-transformer-loader"
    )
    thread.start()
    logger.info("sentence-transformers pre-loading started in background...")