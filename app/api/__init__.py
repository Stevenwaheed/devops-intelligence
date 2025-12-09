"""API package initialization and blueprint registration."""
from flask import Blueprint


def register_blueprints(app):
    """Register all API blueprints."""
    from app.api.auth import auth_bp
    from app.api.organizations import organizations_bp
    from app.api.projects import projects_bp
    from app.api.api_gateway import api_gateway_bp
    from app.api.database_optimizer import database_optimizer_bp
    from app.api.dependency_scanner import dependency_scanner_bp
    from app.api.insights import insights_bp

    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(organizations_bp, url_prefix="/api/v1/organizations")
    app.register_blueprint(projects_bp, url_prefix="/api/v1/projects")
    app.register_blueprint(api_gateway_bp, url_prefix="/api/v1/api-gateway")
    app.register_blueprint(
        database_optimizer_bp, url_prefix="/api/v1/database-optimizer"
    )
    app.register_blueprint(
        dependency_scanner_bp, url_prefix="/api/v1/dependency-scanner"
    )
    app.register_blueprint(insights_bp, url_prefix="/api/v1/insights")
