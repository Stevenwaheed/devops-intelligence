"""Dependency Scanner endpoints."""
from flask import Blueprint, request, g
from sqlalchemy import desc, func
from datetime import datetime, timedelta

from app.extensions import db, cache
from app.models import (
    DependencyScan,
    Dependency,
    Vulnerability,
    MaintenanceMetric,
    DependencyAlternative,
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

dependency_scanner_bp = Blueprint("dependency_scanner", __name__)


# Scans
@dependency_scanner_bp.route("/scans", methods=["GET"])
@token_required
@organization_required
def list_scans():
    """
    List dependency scans.

    Query Parameters:
        project_id: Filter by project
        ecosystem: Filter by ecosystem
        page: Page number
        per_page: Items per page
    """
    page, per_page = get_pagination_params()

    query = (
        DependencyScan.query.join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .order_by(desc(DependencyScan.scan_timestamp))
    )

    # Apply filters
    project_id = request.args.get("project_id", type=int)
    if project_id:
        query = query.filter(DependencyScan.project_id == project_id)

    ecosystem = request.args.get("ecosystem")
    if ecosystem:
        query = query.filter(DependencyScan.ecosystem == ecosystem)

    result = paginate_query(query, page, per_page)

    scans_data = [
        {
            "id": s.id,
            "project_id": s.project_id,
            "scan_timestamp": s.scan_timestamp.isoformat(),
            "scan_trigger": s.scan_trigger.value,
            "ecosystem": s.ecosystem.value,
            "total_dependencies": s.total_dependencies,
            "total_vulnerabilities": s.total_vulnerabilities,
            "overall_risk_score": s.overall_risk_score,
            "scan_duration_ms": s.scan_duration_ms,
        }
        for s in result["items"]
    ]

    return success_response(
        {
            "scans": scans_data,
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            },
        }
    )


@dependency_scanner_bp.route("/scans", methods=["POST"])
@token_required
@organization_required
@validate_json("project_id", "ecosystem", "scan_trigger")
def create_scan():
    """
    Create a new dependency scan.

    Request Body:
        {
            "project_id": 1,
            "ecosystem": "npm",
            "scan_trigger": "manual",
            "total_dependencies": 150,
            "total_vulnerabilities": 5,
            "overall_risk_score": 35.5,
            "scan_duration_ms": 2500
        }
    """
    data = request.get_json()

    # Verify project belongs to organization
    project = Project.query.filter_by(
        id=data["project_id"], organization_id=g.current_organization.id
    ).first()

    if not project:
        return error_response("Project not found", 404)

    scan = DependencyScan(
        project_id=data["project_id"],
        scan_trigger=data["scan_trigger"],
        ecosystem=data["ecosystem"],
        total_dependencies=data.get("total_dependencies", 0),
        total_vulnerabilities=data.get("total_vulnerabilities", 0),
        overall_risk_score=data.get("overall_risk_score", 0.0),
        scan_duration_ms=data.get("scan_duration_ms", 0),
        extra_metadata=data.get("extra_metadata", {}),
    )

    db.session.add(scan)
    db.session.commit()

    return success_response(
        {"id": scan.id, "scan_timestamp": scan.scan_timestamp.isoformat()},
        "Scan created successfully",
        201,
    )


@dependency_scanner_bp.route("/scans/<int:scan_id>", methods=["GET"])
@token_required
@organization_required
def get_scan(scan_id):
    """Get detailed scan information including dependencies."""
    scan = (
        DependencyScan.query.join(Project)
        .filter(
            DependencyScan.id == scan_id,
            Project.organization_id == g.current_organization.id,
        )
        .first()
    )

    if not scan:
        return error_response("Scan not found", 404)

    # Get dependencies for this scan
    dependencies = Dependency.query.filter_by(scan_id=scan_id, is_direct=True).all()

    dependencies_data = [
        {
            "id": d.id,
            "package_name": d.package_name,
            "version": d.version,
            "license": d.license,
            "size_bytes": d.size_bytes,
            "vulnerability_count": len(d.vulnerabilities),
        }
        for d in dependencies
    ]

    return success_response(
        {
            "id": scan.id,
            "project_id": scan.project_id,
            "scan_timestamp": scan.scan_timestamp.isoformat(),
            "scan_trigger": scan.scan_trigger.value,
            "ecosystem": scan.ecosystem.value,
            "total_dependencies": scan.total_dependencies,
            "total_vulnerabilities": scan.total_vulnerabilities,
            "overall_risk_score": scan.overall_risk_score,
            "scan_duration_ms": scan.scan_duration_ms,
            "dependencies": dependencies_data,
        }
    )


# Dependencies
@dependency_scanner_bp.route("/dependencies/<int:dependency_id>", methods=["GET"])
@token_required
@organization_required
def get_dependency(dependency_id):
    """Get detailed dependency information."""
    dependency = (
        Dependency.query.join(DependencyScan)
        .join(Project)
        .filter(
            Dependency.id == dependency_id,
            Project.organization_id == g.current_organization.id,
        )
        .first()
    )

    if not dependency:
        return error_response("Dependency not found", 404)

    # Get vulnerabilities
    vulnerabilities_data = [
        {
            "id": v.id,
            "cve_id": v.cve_id,
            "severity": v.severity.value,
            "cvss_score": v.cvss_score,
            "description": v.description,
            "patched_versions": v.patched_versions,
            "exploit_available": v.exploit_available,
        }
        for v in dependency.vulnerabilities
    ]

    # Get maintenance metrics
    latest_metric = (
        MaintenanceMetric.query.filter_by(dependency_id=dependency_id)
        .order_by(desc(MaintenanceMetric.measured_at))
        .first()
    )

    maintenance_data = None
    if latest_metric:
        maintenance_data = {
            "commit_frequency_30d": latest_metric.commit_frequency_30d,
            "contributor_count": latest_metric.contributor_count,
            "issue_response_time_avg_hours": latest_metric.issue_response_time_avg_hours,
            "download_trend_30d": latest_metric.download_trend_30d,
            "last_commit_date": (
                latest_metric.last_commit_date.isoformat()
                if latest_metric.last_commit_date
                else None
            ),
            "bus_factor": latest_metric.bus_factor,
            "abandonment_risk_score": latest_metric.abandonment_risk_score,
        }

    # Get alternatives
    alternatives_data = [
        {
            "id": a.id,
            "alternative_package_name": a.alternative_package_name,
            "similarity_score": a.similarity_score,
            "migration_difficulty": a.migration_difficulty.value,
            "license_compatibility": a.license_compatibility,
            "recommendation_reason": a.recommendation_reason,
        }
        for a in dependency.alternatives
    ]

    return success_response(
        {
            "id": dependency.id,
            "package_name": dependency.package_name,
            "version": dependency.version,
            "is_direct": dependency.is_direct,
            "license": dependency.license,
            "size_bytes": dependency.size_bytes,
            "last_updated_at": (
                dependency.last_updated_at.isoformat()
                if dependency.last_updated_at
                else None
            ),
            "vulnerabilities": vulnerabilities_data,
            "maintenance": maintenance_data,
            "alternatives": alternatives_data,
        }
    )


# Vulnerabilities
@dependency_scanner_bp.route("/vulnerabilities", methods=["GET"])
@token_required
@organization_required
def list_vulnerabilities():
    """
    List vulnerabilities across all projects.

    Query Parameters:
        project_id: Filter by project
        severity: Filter by severity
        exploit_available: Filter by exploit availability
    """
    page, per_page = get_pagination_params()

    query = (
        Vulnerability.query.join(Dependency)
        .join(DependencyScan)
        .join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .order_by(desc(Vulnerability.cvss_score))
    )

    # Apply filters
    project_id = request.args.get("project_id", type=int)
    if project_id:
        query = query.filter(DependencyScan.project_id == project_id)

    severity = request.args.get("severity")
    if severity:
        query = query.filter(Vulnerability.severity == severity)

    exploit_available = request.args.get("exploit_available")
    if exploit_available is not None:
        query = query.filter(
            Vulnerability.exploit_available == (exploit_available.lower() == "true")
        )

    result = paginate_query(query, page, per_page)

    vulnerabilities_data = [
        {
            "id": v.id,
            "dependency_id": v.dependency_id,
            "cve_id": v.cve_id,
            "severity": v.severity.value,
            "cvss_score": v.cvss_score,
            "description": v.description[:200],  # Truncate for list view
            "exploit_available": v.exploit_available,
            "discovered_at": v.discovered_at.isoformat(),
        }
        for v in result["items"]
    ]

    return success_response(
        {
            "vulnerabilities": vulnerabilities_data,
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            },
        }
    )


# Analytics
@dependency_scanner_bp.route("/analytics/risk-summary", methods=["GET"])
@token_required
@organization_required
@cache.cached(timeout=300, query_string=True)
def get_risk_summary():
    """
    Get risk summary across all projects.

    Query Parameters:
        project_id: Filter by project
    """
    project_id = request.args.get("project_id", type=int)

    # Get latest scan for each project
    subquery = (
        db.session.query(
            DependencyScan.project_id,
            func.max(DependencyScan.scan_timestamp).label("latest_scan"),
        )
        .join(Project)
        .filter(Project.organization_id == g.current_organization.id)
        .group_by(DependencyScan.project_id)
    )

    if project_id:
        subquery = subquery.filter(DependencyScan.project_id == project_id)

    subquery = subquery.subquery()

    # Get scan details
    scans = (
        DependencyScan.query.join(
            subquery,
            (DependencyScan.project_id == subquery.c.project_id)
            & (DependencyScan.scan_timestamp == subquery.c.latest_scan),
        )
        .join(Project)
        .all()
    )

    summary_data = [
        {
            "project_id": s.project_id,
            "project_name": s.project.name,
            "total_dependencies": s.total_dependencies,
            "total_vulnerabilities": s.total_vulnerabilities,
            "overall_risk_score": s.overall_risk_score,
            "last_scan": s.scan_timestamp.isoformat(),
        }
        for s in scans
    ]

    # Calculate totals
    total_dependencies = sum(s["total_dependencies"] for s in summary_data)
    total_vulnerabilities = sum(s["total_vulnerabilities"] for s in summary_data)
    avg_risk_score = (
        sum(s["overall_risk_score"] for s in summary_data) / len(summary_data)
        if summary_data
        else 0
    )

    return success_response(
        {
            "projects": summary_data,
            "summary": {
                "total_dependencies": total_dependencies,
                "total_vulnerabilities": total_vulnerabilities,
                "average_risk_score": avg_risk_score,
                "projects_scanned": len(summary_data),
            },
        }
    )
