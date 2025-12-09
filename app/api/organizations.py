"""Organizations API endpoints."""
from flask import Blueprint, g

from app.extensions import db
from app.models import Organization, User
from app.api.utils import (
    token_required,
    organization_required,
    success_response,
    error_response,
)

organizations_bp = Blueprint("organizations", __name__)


@organizations_bp.route("/current", methods=["GET"])
@token_required
@organization_required
def get_current_organization():
    """
    Get current organization details.

    Returns:
        200: Organization details
    """
    org = g.current_organization

    # Get member count
    member_count = User.query.filter_by(organization_id=org.id, is_active=True).count()

    return success_response(
        {
            "id": org.id,
            "name": org.name,
            "subscription_tier": org.subscription_tier.value,
            "settings": org.settings,
            "member_count": member_count,
            "created_at": org.created_at.isoformat(),
            "updated_at": org.updated_at.isoformat(),
        }
    )


@organizations_bp.route("/current", methods=["PUT"])
@token_required
@organization_required
def update_current_organization():
    """
    Update current organization.

    Request Body:
        {
            "name": "Updated Name",
            "settings": {...}
        }

    Returns:
        200: Organization updated
    """
    from flask import request

    org = g.current_organization
    data = request.get_json()

    if "name" in data:
        org.name = data["name"]
    if "settings" in data:
        org.settings = data["settings"]

    db.session.commit()

    return success_response(
        {
            "id": org.id,
            "name": org.name,
            "subscription_tier": org.subscription_tier.value,
            "settings": org.settings,
            "updated_at": org.updated_at.isoformat(),
        },
        "Organization updated successfully",
    )


@organizations_bp.route("/members", methods=["GET"])
@token_required
@organization_required
def list_members():
    """
    List all members of the current organization.

    Returns:
        200: List of members
    """
    members = User.query.filter_by(
        organization_id=g.current_organization.id, is_active=True
    ).all()

    members_data = [
        {
            "id": m.id,
            "email": m.email,
            "role": m.role.value,
            "created_at": m.created_at.isoformat(),
            "last_login": m.last_login.isoformat() if m.last_login else None,
        }
        for m in members
    ]

    return success_response({"members": members_data, "total": len(members_data)})
