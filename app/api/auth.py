"""Authentication API endpoints."""
from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
import jwt

from app.extensions import db, limiter
from app.models import User, Organization, UserRole, SubscriptionTier
from app.api.utils import (
    validate_json,
    success_response,
    error_response,
    token_required,
)
from config import get_config

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per hour")
@validate_json("email", "password", "organization_name")
def register():
    """
    Register a new user and organization.

    Request Body:
        {
            "email": "user@example.com",
            "password": "secure_password",
            "organization_name": "My Organization"
        }

    Returns:
        201: User and organization created
        400: Validation error
        409: User already exists
    """
    data = request.get_json()

    # Check if user already exists
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return error_response("User with this email already exists", 409)

    # Create organization
    organization = Organization(
        name=data["organization_name"],
        subscription_tier=SubscriptionTier.FREE,
        settings={},
    )
    db.session.add(organization)
    db.session.flush()  # Get organization ID

    # Create user
    user = User(
        email=data["email"],
        organization_id=organization.id,
        role=UserRole.OWNER,
        is_active=True,
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    # Generate token
    config = get_config()
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + config.JWT_ACCESS_TOKEN_EXPIRES,
        },
        config.JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return success_response(
        {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
            },
            "organization": {
                "id": organization.id,
                "name": organization.name,
                "subscription_tier": organization.subscription_tier.value,
            },
            "token": token,
        },
        "User registered successfully",
        201,
    )


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
@validate_json("email", "password")
def login():
    """
    Authenticate user and return JWT token.

    Request Body:
        {
            "email": "user@example.com",
            "password": "secure_password"
        }

    Returns:
        200: Authentication successful
        401: Invalid credentials
    """
    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return error_response("Invalid email or password", 401)

    if not user.is_active:
        return error_response("Account is disabled", 401)

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate token
    config = get_config()
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + config.JWT_ACCESS_TOKEN_EXPIRES,
        },
        config.JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return success_response(
        {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "organization_id": user.organization_id,
            },
            "token": token,
        },
        "Login successful",
    )


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user():
    """
    Get current authenticated user information.

    Returns:
        200: User information
        401: Not authenticated
    """
    user = g.current_user

    return success_response(
        {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "organization_id": user.organization_id,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
    )


@auth_bp.route("/refresh", methods=["POST"])
@token_required
def refresh_token():
    """
    Refresh JWT token.

    Returns:
        200: New token generated
        401: Not authenticated
    """
    user = g.current_user

    # Generate new token
    config = get_config()
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + config.JWT_ACCESS_TOKEN_EXPIRES,
        },
        config.JWT_SECRET_KEY,
        algorithm="HS256",
    )

    return success_response({"token": token}, "Token refreshed successfully")


@auth_bp.route("/change-password", methods=["POST"])
@token_required
@validate_json("current_password", "new_password")
def change_password():
    """
    Change user password.

    Request Body:
        {
            "current_password": "old_password",
            "new_password": "new_password"
        }

    Returns:
        200: Password changed
        400: Invalid current password
    """
    user = g.current_user
    data = request.get_json()

    if not user.check_password(data["current_password"]):
        return error_response("Current password is incorrect", 400)

    user.set_password(data["new_password"])
    db.session.commit()

    return success_response(message="Password changed successfully")
