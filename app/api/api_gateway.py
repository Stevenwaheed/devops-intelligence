"""API Gateway endpoints."""
from flask import Blueprint, request, g
from sqlalchemy import desc, func
from datetime import datetime, timedelta

from app.extensions import db, cache
from app.models import (
    APIProvider,
    APIConfiguration,
    APIRequest,
    APIBudget,
    APIAlert,
    Project,
)
from app.api.utils import (
    token_required,
    organization_required,
    validate_json,
    success_response,
    error_response,
    paginate_query,
    get_pagination_params,
)

api_gateway_bp = Blueprint("api_gateway", __name__)


# API Providers
@api_gateway_bp.route("/providers", methods=["GET"])
@token_required
@organization_required
def list_providers():
    """List all API providers for the organization."""
    providers = APIProvider.query.filter_by(
        organization_id=g.current_organization.id
    ).all()

    providers_data = [
        {
            "id": p.id,
            "name": p.name,
            "provider_type": p.provider_type.value,
            "is_active": p.is_active,
            "priority_order": p.priority_order,
            "created_at": p.created_at.isoformat(),
        }
        for p in providers
    ]

    return success_response({"providers": providers_data})


@api_gateway_bp.route("/providers", methods=["POST"])
@token_required
@organization_required
@validate_json("name", "provider_type", "credentials")
def create_provider():
    """Create a new API provider."""
    data = request.get_json()

    # TODO: Encrypt credentials before storing
    provider = APIProvider(
        organization_id=g.current_organization.id,
        name=data["name"],
        provider_type=data["provider_type"],
        credentials_encrypted=data["credentials"],  # Should be encrypted
        is_active=data.get("is_active", True),
        priority_order=data.get("priority_order", 0),
        extra_metadata=data.get("extra_metadata", {}),
    )

    db.session.add(provider)
    db.session.commit()

    return success_response(
        {
            "id": provider.id,
            "name": provider.name,
            "provider_type": provider.provider_type.value,
        },
        "Provider created successfully",
        201,
    )


# API Requests Analytics
@api_gateway_bp.route("/requests", methods=["GET"])
@token_required
@organization_required
def list_requests():
    """
    List API requests with filtering and pagination.

    Query Parameters:
        project_id: Filter by project
        provider_id: Filter by provider
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        page: Page number
        per_page: Items per page
    """
    page, per_page = get_pagination_params()

    # Base query - join with projects to filter by organization
    query = (
        APIRequest.query.join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .order_by(desc(APIRequest.timestamp))
    )

    # Apply filters
    project_id = request.args.get("project_id", type=int)
    if project_id:
        query = query.filter(APIRequest.project_id == project_id)

    provider_id = request.args.get("provider_id", type=int)
    if provider_id:
        query = query.filter(APIRequest.provider_id == provider_id)

    start_date = request.args.get("start_date")
    if start_date:
        query = query.filter(APIRequest.timestamp >= datetime.fromisoformat(start_date))

    end_date = request.args.get("end_date")
    if end_date:
        query = query.filter(APIRequest.timestamp <= datetime.fromisoformat(end_date))

    result = paginate_query(query, page, per_page)

    requests_data = [
        {
            "id": r.id,
            "project_id": r.project_id,
            "provider_id": r.provider_id,
            "timestamp": r.timestamp.isoformat(),
            "endpoint": r.endpoint,
            "method": r.method,
            "status_code": r.status_code,
            "latency_ms": r.latency_ms,
            "cost_usd": r.cost_usd,
            "tokens_used": r.tokens_used,
            "environment": r.environment,
        }
        for r in result["items"]
    ]

    return success_response(
        {
            "requests": requests_data,
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            },
        }
    )


@api_gateway_bp.route("/requests", methods=["POST"])
@token_required
def log_request():
    """
    Log an API request (used by the proxy).

    Request Body:
        {
            "project_id": 1,
            "provider_id": 1,
            "endpoint": "/v1/chat/completions",
            "method": "POST",
            "status_code": 200,
            "latency_ms": 150.5,
            "cost_usd": 0.002,
            "tokens_used": {"prompt": 100, "completion": 50},
            "environment": "production"
        }
    """
    data = request.get_json()

    api_request = APIRequest(
        project_id=data["project_id"],
        provider_id=data["provider_id"],
        endpoint=data["endpoint"],
        method=data["method"],
        status_code=data["status_code"],
        latency_ms=data["latency_ms"],
        cost_usd=data.get("cost_usd", 0.0),
        tokens_used=data.get("tokens_used"),
        user_identifier=data.get("user_identifier"),
        environment=data.get("environment", "production"),
        error_message=data.get("error_message"),
        extra_metadata=data.get("extra_metadata"),
    )

    db.session.add(api_request)
    db.session.commit()

    return success_response({"id": api_request.id}, "Request logged successfully", 201)


# Analytics
@api_gateway_bp.route("/analytics/cost", methods=["GET"])
@token_required
@organization_required
@cache.cached(timeout=300, query_string=True)
def get_cost_analytics():
    """
    Get cost analytics for API usage.

    Query Parameters:
        project_id: Filter by project
        days: Number of days to analyze (default: 30)
    """
    project_id = request.args.get("project_id", type=int)
    days = request.args.get("days", 30, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    # Base query
    query = (
        db.session.query(
            func.date(APIRequest.timestamp).label("date"),
            func.sum(APIRequest.cost_usd).label("total_cost"),
            func.count(APIRequest.id).label("request_count"),
        )
        .join(Project)
        .filter(
            Project.organization_id == g.current_organization.id,
            APIRequest.timestamp >= start_date,
        )
        .group_by(func.date(APIRequest.timestamp))
        .order_by(func.date(APIRequest.timestamp))
    )

    if project_id:
        query = query.filter(APIRequest.project_id == project_id)

    results = query.all()

    analytics_data = [
        {
            "date": str(r.date),
            "total_cost": float(r.total_cost or 0),
            "request_count": r.request_count,
        }
        for r in results
    ]

    # Calculate totals
    total_cost = sum(r["total_cost"] for r in analytics_data)
    total_requests = sum(r["request_count"] for r in analytics_data)

    return success_response(
        {
            "daily_analytics": analytics_data,
            "summary": {
                "total_cost": total_cost,
                "total_requests": total_requests,
                "average_cost_per_request": (
                    total_cost / total_requests if total_requests > 0 else 0
                ),
                "period_days": days,
            },
        }
    )


@api_gateway_bp.route("/analytics/latency", methods=["GET"])
@token_required
@organization_required
@cache.cached(timeout=300, query_string=True)
def get_latency_analytics():
    """Get latency analytics for API usage."""
    project_id = request.args.get("project_id", type=int)
    days = request.args.get("days", 7, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    query = (
        db.session.query(
            APIProvider.name.label("provider_name"),
            func.avg(APIRequest.latency_ms).label("avg_latency"),
            func.min(APIRequest.latency_ms).label("min_latency"),
            func.max(APIRequest.latency_ms).label("max_latency"),
            func.count(APIRequest.id).label("request_count"),
        )
        .join(APIProvider)
        .join(Project)
        .filter(
            Project.organization_id == g.current_organization.id,
            APIRequest.timestamp >= start_date,
        )
        .group_by(APIProvider.name)
    )

    if project_id:
        query = query.filter(APIRequest.project_id == project_id)

    results = query.all()

    latency_data = [
        {
            "provider": r.provider_name,
            "avg_latency_ms": float(r.avg_latency or 0),
            "min_latency_ms": float(r.min_latency or 0),
            "max_latency_ms": float(r.max_latency or 0),
            "request_count": r.request_count,
        }
        for r in results
    ]

    return success_response({"latency_by_provider": latency_data})


# Budgets
@api_gateway_bp.route("/budgets", methods=["GET"])
@token_required
@organization_required
def list_budgets():
    """List all budgets."""
    budgets = (
        APIBudget.query.join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .all()
    )

    budgets_data = [
        {
            "id": b.id,
            "project_id": b.project_id,
            "period_start": b.period_start.isoformat(),
            "period_end": b.period_end.isoformat(),
            "allocated_amount_usd": b.allocated_amount_usd,
            "spent_amount_usd": b.spent_amount_usd,
            "utilization_pct": (
                (b.spent_amount_usd / b.allocated_amount_usd * 100)
                if b.allocated_amount_usd > 0
                else 0
            ),
        }
        for b in budgets
    ]

    return success_response({"budgets": budgets_data})


@api_gateway_bp.route("/budgets", methods=["POST"])
@token_required
@organization_required
@validate_json("project_id", "period_start", "period_end", "allocated_amount_usd")
def create_budget():
    """Create a new budget."""
    data = request.get_json()

    # Verify project belongs to organization
    project = Project.query.filter_by(
        id=data["project_id"], organization_id=g.current_organization.id
    ).first()

    if not project:
        return error_response("Project not found", 404)

    budget = APIBudget(
        project_id=data["project_id"],
        period_start=datetime.fromisoformat(data["period_start"]),
        period_end=datetime.fromisoformat(data["period_end"]),
        allocated_amount_usd=data["allocated_amount_usd"],
        alert_thresholds=data.get("alert_thresholds", {"warning": 80, "critical": 95}),
        actions_on_exceed=data.get("actions_on_exceed", {"throttle": True}),
    )

    db.session.add(budget)
    db.session.commit()

    return success_response(
        {"id": budget.id, "project_id": budget.project_id},
        "Budget created successfully",
        201,
    )
