"""Application factory and initialization."""
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from config import get_config
from app.extensions import db, cache, limiter, celery
from app.api import register_blueprints


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(get_config(config_name))

    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"])
    Migrate(app, db)

    # Initialize Celery
    celery.conf.update(app.config)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route("/health")
    def health():
        return {"status": "healthy", "service": "devguard"}, 200

    return app


def register_error_handlers(app):
    """Register error handlers."""
    from flask import jsonify

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({"error": "Rate limit exceeded"}), 429


# Create Celery app
celery_app = celery
