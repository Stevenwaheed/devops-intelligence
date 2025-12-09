"""Celery tasks for background processing."""
from celery import Celery
from datetime import datetime, timedelta
from sqlalchemy import func

from app.extensions import db
from app.models import (
    APIRequest,
    APIBudget,
    APIAlert,
    QueryPattern,
    DependencyScan,
    Insight,
    Project,
)

celery = Celery("devguard")


@celery.task(name="tasks.check_api_budgets")
def check_api_budgets():
    """
    Check API budgets and create alerts if thresholds are exceeded.
    Runs every hour.
    """
    from app import create_app

    app = create_app()
    with app.app_context():
        # Get all active budgets
        now = datetime.utcnow()
        budgets = APIBudget.query.filter(
            APIBudget.period_start <= now, APIBudget.period_end >= now
        ).all()

        for budget in budgets:
            # Calculate current spending
            total_spent = (
                db.session.query(func.sum(APIRequest.cost_usd))
                .filter(
                    APIRequest.project_id == budget.project_id,
                    APIRequest.timestamp >= budget.period_start,
                    APIRequest.timestamp <= budget.period_end,
                )
                .scalar()
                or 0.0
            )

            # Update budget
            budget.spent_amount_usd = total_spent

            # Check thresholds
            utilization_pct = (
                (total_spent / budget.allocated_amount_usd * 100)
                if budget.allocated_amount_usd > 0
                else 0
            )

            thresholds = budget.alert_thresholds or {"warning": 80, "critical": 95}

            # Create alerts if needed
            if utilization_pct >= thresholds.get("critical", 95):
                _create_alert(
                    budget.project_id,
                    "budget",
                    "critical",
                    f"Budget critically exceeded: {utilization_pct:.1f}% used",
                )
            elif utilization_pct >= thresholds.get("warning", 80):
                _create_alert(
                    budget.project_id,
                    "budget",
                    "warning",
                    f"Budget warning: {utilization_pct:.1f}% used",
                )

        db.session.commit()


@celery.task(name="tasks.analyze_query_patterns")
def analyze_query_patterns():
    """
    Analyze query patterns and generate optimization recommendations.
    Runs every 6 hours.
    """
    from app import create_app

    app = create_app()
    with app.app_context():
        # Get slow queries from the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)

        slow_queries = (
            db.session.query(
                QueryPattern.query_fingerprint,
                QueryPattern.connection_id,
                func.avg(QueryPattern.execution_time_ms).label("avg_time"),
                func.count(QueryPattern.id).label("frequency"),
            )
            .filter(
                QueryPattern.timestamp >= yesterday,
                QueryPattern.execution_time_ms > 100,  # Queries slower than 100ms
            )
            .group_by(QueryPattern.query_fingerprint, QueryPattern.connection_id)
            .having(func.count(QueryPattern.id) > 10)  # Executed more than 10 times
            .all()
        )

        # TODO: Implement ML-based optimization recommendations
        # For now, just log the findings
        print(f"Found {len(slow_queries)} slow query patterns")


@celery.task(name="tasks.scan_dependencies")
def scan_dependencies(project_id: int, ecosystem: str):
    """
    Scan project dependencies for vulnerabilities and risks.
    Triggered manually or on schedule.
    """
    from app import create_app

    app = create_app()
    with app.app_context():
        # TODO: Implement actual dependency scanning logic
        # This would integrate with vulnerability databases and package registries

        scan = DependencyScan(
            project_id=project_id,
            scan_trigger="scheduled",
            ecosystem=ecosystem,
            total_dependencies=0,
            total_vulnerabilities=0,
            overall_risk_score=0.0,
            scan_duration_ms=0,
        )

        db.session.add(scan)
        db.session.commit()

        print(f"Completed dependency scan for project {project_id}")


@celery.task(name="tasks.generate_insights")
def generate_insights():
    """
    Generate AI-powered insights from collected data.
    Runs daily.
    """
    from app import create_app

    app = create_app()
    with app.app_context():
        # Get all active projects
        projects = Project.query.filter_by(is_active=True).all()

        for project in projects:
            # Analyze API costs
            _analyze_api_costs(project.id)

            # Analyze database performance
            _analyze_database_performance(project.id)

            # Analyze dependency risks
            _analyze_dependency_risks(project.id)

        db.session.commit()


def _create_alert(project_id: int, alert_type: str, severity: str, message: str):
    """Helper function to create an alert."""
    # Check if similar alert already exists (not resolved)
    existing_alert = APIAlert.query.filter_by(
        project_id=project_id,
        alert_type=alert_type,
        resolved_at=None,
    ).first()

    if not existing_alert:
        alert = APIAlert(
            project_id=project_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            extra_metadata={},
        )
        db.session.add(alert)


def _analyze_api_costs(project_id: int):
    """Analyze API costs and generate insights."""
    # Get costs for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    total_cost = (
        db.session.query(func.sum(APIRequest.cost_usd))
        .filter(
            APIRequest.project_id == project_id, APIRequest.timestamp >= thirty_days_ago
        )
        .scalar()
        or 0.0
    )

    if total_cost > 100:  # If spending more than $100/month
        insight = Insight(
            project_id=project_id,
            category="cost",
            severity="warning",
            title="High API Costs Detected",
            description=f"Your project has spent ${total_cost:.2f} on API calls in the last 30 days.",
            evidence={"total_cost": total_cost, "period_days": 30},
            recommended_actions={
                "actions": [
                    "Review API usage patterns",
                    "Consider implementing caching",
                    "Optimize request frequency",
                ]
            },
            estimated_impact={"potential_savings_pct": 20},
        )
        db.session.add(insight)


def _analyze_database_performance(project_id: int):
    """Analyze database performance and generate insights."""
    # TODO: Implement database performance analysis
    pass


def _analyze_dependency_risks(project_id: int):
    """Analyze dependency risks and generate insights."""
    # Get latest scan
    latest_scan = (
        DependencyScan.query.filter_by(project_id=project_id)
        .order_by(DependencyScan.scan_timestamp.desc())
        .first()
    )

    if latest_scan and latest_scan.total_vulnerabilities > 0:
        insight = Insight(
            project_id=project_id,
            category="security",
            severity="critical" if latest_scan.total_vulnerabilities > 5 else "warning",
            title=f"{latest_scan.total_vulnerabilities} Vulnerabilities Found",
            description=f"Your project has {latest_scan.total_vulnerabilities} known vulnerabilities in dependencies.",
            evidence={
                "scan_id": latest_scan.id,
                "vulnerability_count": latest_scan.total_vulnerabilities,
            },
            recommended_actions={
                "actions": [
                    "Update vulnerable dependencies",
                    "Review security advisories",
                    "Consider alternative packages",
                ]
            },
            estimated_impact={"risk_reduction_pct": 80},
        )
        db.session.add(insight)


# Celery Beat Schedule
celery.conf.beat_schedule = {
    "check-api-budgets": {
        "task": "tasks.check_api_budgets",
        "schedule": 3600.0,  # Every hour
    },
    "analyze-query-patterns": {
        "task": "tasks.analyze_query_patterns",
        "schedule": 21600.0,  # Every 6 hours
    },
    "generate-insights": {
        "task": "tasks.generate_insights",
        "schedule": 86400.0,  # Daily
    },
}
