"""Insights API endpoints."""
from flask import Blueprint, request, g
from sqlalchemy import desc

from app.extensions import db
from app.models import Insight, Project
from app.api.utils import (
    token_required,
    organization_required,
    success_response,
    error_response,
    paginate_query,
    get_pagination_params,
)

insights_bp = Blueprint("insights", __name__)


@insights_bp.route("", methods=["GET"])
@token_required
@organization_required
def list_insights():
    """
    List AI-generated insights.

    Query Parameters:
        project_id: Filter by project
        category: Filter by category
        severity: Filter by severity
        resolved: Filter by resolved status
        page: Page number
        per_page: Items per page
    """
    page, per_page = get_pagination_params()

    query = (
        Insight.query.join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .order_by(desc(Insight.created_at))
    )

    # Apply filters
    project_id = request.args.get("project_id", type=int)
    if project_id:
        query = query.filter(Insight.project_id == project_id)

    category = request.args.get("category")
    if category:
        query = query.filter(Insight.category == category)

    severity = request.args.get("severity")
    if severity:
        query = query.filter(Insight.severity == severity)

    resolved = request.args.get("resolved")
    if resolved is not None:
        if resolved.lower() == "true":
            query = query.filter(Insight.resolved_at.isnot(None))
        else:
            query = query.filter(Insight.resolved_at.is_(None))

    result = paginate_query(query, page, per_page)

    insights_data = [
        {
            "id": i.id,
            "project_id": i.project_id,
            "category": i.category.value,
            "severity": i.severity.value,
            "title": i.title,
            "description": i.description,
            "evidence": i.evidence,
            "recommended_actions": i.recommended_actions,
            "estimated_impact": i.estimated_impact,
            "created_at": i.created_at.isoformat(),
            "acknowledged_at": i.acknowledged_at.isoformat() if i.acknowledged_at else None,
            "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
        }
        for i in result["items"]
    ]

    return success_response(
        {
            "insights": insights_data,
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            },
        }
    )


@insights_bp.route("/<int:insight_id>/acknowledge", methods=["POST"])
@token_required
@organization_required
def acknowledge_insight(insight_id):
    """Acknowledge an insight."""
    from datetime import datetime

    insight = (
        Insight.query.join(Project)
        .filter(
            Insight.id == insight_id,
            Project.organization_id == g.current_organization.id,
        )
        .first()
    )

    if not insight:
        return error_response("Insight not found", 404)

    insight.acknowledged_at = datetime.utcnow()
    db.session.commit()

    return success_response(
        {"id": insight.id, "acknowledged_at": insight.acknowledged_at.isoformat()},
        "Insight acknowledged",
    )


@insights_bp.route("/<int:insight_id>/resolve", methods=["POST"])
@token_required
@organization_required
def resolve_insight(insight_id):
    """Mark an insight as resolved."""
    from datetime import datetime

    insight = (
        Insight.query.join(Project)
        .filter(
            Insight.id == insight_id,
            Project.organization_id == g.current_organization.id,
        )
        .first()
    )

    if not insight:
        return error_response("Insight not found", 404)

    insight.resolved_at = datetime.utcnow()
    db.session.commit()

    return success_response(
        {"id": insight.id, "resolved_at": insight.resolved_at.isoformat()},
        "Insight resolved",
    )
