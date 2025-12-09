"""Database Optimizer endpoints."""
from flask import Blueprint, request, g
from sqlalchemy import desc, func
from datetime import datetime, timedelta

from app.extensions import db, cache
from app.models import (
    DatabaseConnection,
    QueryPattern,
    QueryOptimization,
    DatabaseMetric,
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

database_optimizer_bp = Blueprint("database_optimizer", __name__)


# Database Connections
@database_optimizer_bp.route("/connections", methods=["GET"])
@token_required
@organization_required
def list_connections():
    """List all database connections."""
    connections = (
        DatabaseConnection.query.join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .all()
    )

    connections_data = [
        {
            "id": c.id,
            "project_id": c.project_id,
            "name": c.name,
            "database_type": c.database_type.value,
            "is_active": c.is_active,
            "created_at": c.created_at.isoformat(),
        }
        for c in connections
    ]

    return success_response({"connections": connections_data})


@database_optimizer_bp.route("/connections", methods=["POST"])
@token_required
@organization_required
@validate_json("project_id", "name", "database_type", "connection_string")
def create_connection():
    """Create a new database connection."""
    data = request.get_json()

    # Verify project belongs to organization
    project = Project.query.filter_by(
        id=data["project_id"], organization_id=g.current_organization.id
    ).first()

    if not project:
        return error_response("Project not found", 404)

    # TODO: Encrypt connection string before storing
    connection = DatabaseConnection(
        project_id=data["project_id"],
        name=data["name"],
        database_type=data["database_type"],
        connection_string_encrypted=data["connection_string"],  # Should be encrypted
        is_active=data.get("is_active", True),
        extra_metadata=data.get("extra_metadata", {}),
    )

    db.session.add(connection)
    db.session.commit()

    return success_response(
        {
            "id": connection.id,
            "name": connection.name,
            "database_type": connection.database_type.value,
        },
        "Connection created successfully",
        201,
    )


# Query Patterns
@database_optimizer_bp.route("/query-patterns", methods=["GET"])
@token_required
@organization_required
def list_query_patterns():
    """
    List query patterns with filtering and pagination.

    Query Parameters:
        connection_id: Filter by connection
        start_date: Filter by start date
        end_date: Filter by end date
        min_execution_time: Minimum execution time in ms
        page: Page number
        per_page: Items per page
    """
    page, per_page = get_pagination_params()

    # Base query
    query = (
        QueryPattern.query.join(DatabaseConnection)
        .join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .order_by(desc(QueryPattern.timestamp))
    )

    # Apply filters
    connection_id = request.args.get("connection_id", type=int)
    if connection_id:
        query = query.filter(QueryPattern.connection_id == connection_id)

    start_date = request.args.get("start_date")
    if start_date:
        query = query.filter(QueryPattern.timestamp >= datetime.fromisoformat(start_date))

    end_date = request.args.get("end_date")
    if end_date:
        query = query.filter(QueryPattern.timestamp <= datetime.fromisoformat(end_date))

    min_execution_time = request.args.get("min_execution_time", type=float)
    if min_execution_time:
        query = query.filter(QueryPattern.execution_time_ms >= min_execution_time)

    result = paginate_query(query, page, per_page)

    patterns_data = [
        {
            "id": p.id,
            "connection_id": p.connection_id,
            "timestamp": p.timestamp.isoformat(),
            "query_fingerprint": p.query_fingerprint,
            "query_structure": p.query_structure[:200],  # Truncate for list view
            "execution_time_ms": p.execution_time_ms,
            "rows_examined": p.rows_examined,
            "rows_returned": p.rows_returned,
            "frequency_count": p.frequency_count,
        }
        for p in result["items"]
    ]

    return success_response(
        {
            "patterns": patterns_data,
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            },
        }
    )


@database_optimizer_bp.route("/query-patterns", methods=["POST"])
@token_required
def log_query_pattern():
    """
    Log a query pattern (used by the monitoring agent).

    Request Body:
        {
            "connection_id": 1,
            "query_fingerprint": "abc123...",
            "query_structure": "SELECT * FROM users WHERE id = ?",
            "execution_time_ms": 45.2,
            "rows_examined": 1000,
            "rows_returned": 10,
            "index_usage": {...},
            "explain_plan": {...}
        }
    """
    data = request.get_json()

    pattern = QueryPattern(
        connection_id=data["connection_id"],
        query_fingerprint=data["query_fingerprint"],
        query_structure=data["query_structure"],
        execution_time_ms=data["execution_time_ms"],
        rows_examined=data.get("rows_examined", 0),
        rows_returned=data.get("rows_returned", 0),
        index_usage=data.get("index_usage"),
        explain_plan=data.get("explain_plan"),
        frequency_count=data.get("frequency_count", 1),
    )

    db.session.add(pattern)
    db.session.commit()

    return success_response({"id": pattern.id}, "Query pattern logged successfully", 201)


# Optimizations
@database_optimizer_bp.route("/optimizations", methods=["GET"])
@token_required
@organization_required
def list_optimizations():
    """
    List query optimizations.

    Query Parameters:
        connection_id: Filter by connection
        is_applied: Filter by applied status
        min_improvement: Minimum estimated improvement percentage
    """
    page, per_page = get_pagination_params()

    # Base query
    query = (
        QueryOptimization.query.join(QueryPattern)
        .join(DatabaseConnection)
        .join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .order_by(desc(QueryOptimization.estimated_improvement_pct))
    )

    # Apply filters
    connection_id = request.args.get("connection_id", type=int)
    if connection_id:
        query = query.filter(QueryPattern.connection_id == connection_id)

    is_applied = request.args.get("is_applied")
    if is_applied is not None:
        query = query.filter(
            QueryOptimization.is_applied == (is_applied.lower() == "true")
        )

    min_improvement = request.args.get("min_improvement", type=float)
    if min_improvement:
        query = query.filter(
            QueryOptimization.estimated_improvement_pct >= min_improvement
        )

    result = paginate_query(query, page, per_page)

    optimizations_data = [
        {
            "id": o.id,
            "pattern_id": o.pattern_id,
            "optimization_type": o.optimization_type.value,
            "current_performance_score": o.current_performance_score,
            "estimated_improvement_pct": o.estimated_improvement_pct,
            "recommendation_text": o.recommendation_text,
            "complexity_score": o.complexity_score,
            "is_applied": o.is_applied,
            "applied_at": o.applied_at.isoformat() if o.applied_at else None,
            "actual_improvement_pct": o.actual_improvement_pct,
        }
        for o in result["items"]
    ]

    return success_response(
        {
            "optimizations": optimizations_data,
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            },
        }
    )


@database_optimizer_bp.route("/optimizations/<int:optimization_id>/apply", methods=["POST"])
@token_required
@organization_required
def apply_optimization(optimization_id):
    """Mark an optimization as applied."""
    optimization = (
        QueryOptimization.query.join(QueryPattern)
        .join(DatabaseConnection)
        .join(Project)
        .filter(
            QueryOptimization.id == optimization_id,
            Project.organization_id == g.current_organization.id,
        )
        .first()
    )

    if not optimization:
        return error_response("Optimization not found", 404)

    optimization.is_applied = True
    optimization.applied_at = datetime.utcnow()

    db.session.commit()

    return success_response(
        {"id": optimization.id, "applied_at": optimization.applied_at.isoformat()},
        "Optimization marked as applied",
    )


# Analytics
@database_optimizer_bp.route("/analytics/performance", methods=["GET"])
@token_required
@organization_required
@cache.cached(timeout=300, query_string=True)
def get_performance_analytics():
    """
    Get database performance analytics.

    Query Parameters:
        connection_id: Filter by connection
        days: Number of days to analyze (default: 7)
    """
    connection_id = request.args.get("connection_id", type=int)
    days = request.args.get("days", 7, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    # Query average execution times
    query = (
        db.session.query(
            func.date(QueryPattern.timestamp).label("date"),
            func.avg(QueryPattern.execution_time_ms).label("avg_execution_time"),
            func.count(QueryPattern.id).label("query_count"),
        )
        .join(DatabaseConnection)
        .join(Project)
        .filter(
            Project.organization_id == g.current_organization.id,
            QueryPattern.timestamp >= start_date,
        )
        .group_by(func.date(QueryPattern.timestamp))
        .order_by(func.date(QueryPattern.timestamp))
    )

    if connection_id:
        query = query.filter(QueryPattern.connection_id == connection_id)

    results = query.all()

    analytics_data = [
        {
            "date": str(r.date),
            "avg_execution_time_ms": float(r.avg_execution_time or 0),
            "query_count": r.query_count,
        }
        for r in results
    ]

    return success_response({"daily_performance": analytics_data})


@database_optimizer_bp.route("/analytics/slow-queries", methods=["GET"])
@token_required
@organization_required
@cache.cached(timeout=300, query_string=True)
def get_slow_queries():
    """Get top slow queries."""
    connection_id = request.args.get("connection_id", type=int)
    limit = request.args.get("limit", 10, type=int)
    days = request.args.get("days", 7, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    query = (
        db.session.query(
            QueryPattern.query_fingerprint,
            QueryPattern.query_structure,
            func.avg(QueryPattern.execution_time_ms).label("avg_execution_time"),
            func.max(QueryPattern.execution_time_ms).label("max_execution_time"),
            func.count(QueryPattern.id).label("execution_count"),
        )
        .join(DatabaseConnection)
        .join(Project)
        .filter(
            Project.organization_id == g.current_organization.id,
            QueryPattern.timestamp >= start_date,
        )
        .group_by(QueryPattern.query_fingerprint, QueryPattern.query_structure)
        .order_by(desc(func.avg(QueryPattern.execution_time_ms)))
        .limit(limit)
    )

    if connection_id:
        query = query.filter(QueryPattern.connection_id == connection_id)

    results = query.all()

    slow_queries = [
        {
            "query_fingerprint": r.query_fingerprint,
            "query_structure": r.query_structure[:200],
            "avg_execution_time_ms": float(r.avg_execution_time or 0),
            "max_execution_time_ms": float(r.max_execution_time or 0),
            "execution_count": r.execution_count,
        }
        for r in results
    ]

    return success_response({"slow_queries": slow_queries})
