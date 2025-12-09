"""Utility functions for API endpoints."""
from functools import wraps
from flask import request, jsonify, g
from typing import Optional, Tuple, Any
import jwt
from datetime import datetime

from app.extensions import db
from app.models import User, Organization
from config import get_config


def paginate_query(query, page: int = 1, per_page: int = 20):
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Items per page

    Returns:
        dict: Pagination metadata and items
    """
    config = get_config()
    per_page = min(per_page, config.API_PAGINATION_MAX)
    per_page = max(per_page, 1)
    page = max(page, 1)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "items": pagination.items,
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


def get_pagination_params() -> Tuple[int, int]:
    """
    Extract pagination parameters from request.

    Returns:
        Tuple of (page, per_page)
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", get_config().API_PAGINATION_DEFAULT, type=int)
    return page, per_page


def token_required(f):
    """
    Decorator to require JWT token authentication.

    Usage:
        @token_required
        def protected_route():
            # Access current user via g.current_user
            pass
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Decode token
            config = get_config()
            data = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = db.session.get(User, data["user_id"])

            if not current_user or not current_user.is_active:
                return jsonify({"error": "Invalid token"}), 401

            # Store user in Flask's g object
            g.current_user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": "Token validation failed"}), 401

        return f(*args, **kwargs)

    return decorated


def organization_required(f):
    """
    Decorator to ensure user belongs to an organization.
    Must be used after @token_required.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, "current_user"):
            return jsonify({"error": "Authentication required"}), 401

        organization = db.session.get(Organization, g.current_user.organization_id)
        if not organization:
            return jsonify({"error": "Organization not found"}), 404

        g.current_organization = organization
        return f(*args, **kwargs)

    return decorated


def validate_json(*required_fields):
    """
    Decorator to validate JSON request body.

    Usage:
        @validate_json('name', 'email')
        def create_user():
            data = request.get_json()
            # data is guaranteed to have 'name' and 'email'
    """

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400

            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body is empty"}), 400

            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return (
                    jsonify(
                        {
                            "error": "Missing required fields",
                            "fields": missing_fields,
                        }
                    ),
                    400,
                )

            return f(*args, **kwargs)

        return decorated

    return decorator


def success_response(data: Any = None, message: str = None, status_code: int = 200):
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code

    Returns:
        Flask response tuple
    """
    response = {}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message

    return jsonify(response), status_code


def error_response(error: str, status_code: int = 400, details: Any = None):
    """
    Create a standardized error response.

    Args:
        error: Error message
        status_code: HTTP status code
        details: Optional error details

    Returns:
        Flask response tuple
    """
    response = {"error": error}
    if details:
        response["details"] = details

    return jsonify(response), status_code


def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Serialize datetime to ISO format string.

    Args:
        dt: Datetime object

    Returns:
        ISO format string or None
    """
    if dt is None:
        return None
    return dt.isoformat()


def get_filter_params(allowed_filters: list) -> dict:
    """
    Extract filter parameters from request args.

    Args:
        allowed_filters: List of allowed filter parameter names

    Returns:
        Dictionary of filter parameters
    """
    filters = {}
    for filter_name in allowed_filters:
        value = request.args.get(filter_name)
        if value is not None:
            filters[filter_name] = value
    return filters


def apply_filters(query, model, filters: dict):
    """
    Apply filters to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        model: SQLAlchemy model class
        filters: Dictionary of filter parameters

    Returns:
        Filtered query
    """
    for field, value in filters.items():
        if hasattr(model, field):
            query = query.filter(getattr(model, field) == value)
    return query
