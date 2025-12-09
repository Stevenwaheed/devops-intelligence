"""Projects API endpoints."""
from flask import Blueprint, request, g
from sqlalchemy import desc

from app.extensions import db, cache
from app.models import Project
from app.api.utils import (
    token_required,
    organization_required,
    validate_json,
    success_response,
    error_response,
    paginate_query,
    get_pagination_params,
)

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("", methods=["GET"])
@token_required
@organization_required
@cache.cached(timeout=60, query_string=True)
def list_projects():
    """
    List all projects for the current organization.

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        is_active: Filter by active status (true/false)

    Returns:
        200: List of projects with pagination
    """
    page, per_page = get_pagination_params()

    query = Project.query.filter_by(organization_id=g.current_organization.id).order_by(
        desc(Project.created_at)
    )

    # Apply filters
    is_active = request.args.get("is_active")
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == "true")

    result = paginate_query(query, page, per_page)

    # Serialize projects
    projects_data = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "tech_stack": p.tech_stack,
            "repository_url": p.repository_url,
            "is_active": p.is_active,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat(),
        }
        for p in result["items"]
    ]

    return success_response(
        {
            "projects": projects_data,
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
            },
        }
    )


@projects_bp.route("", methods=["POST"])
@token_required
@organization_required
@validate_json("name")
def create_project():
    """
    Create a new project.

    Request Body:
        {
            "name": "My Project",
            "description": "Project description",
            "tech_stack": {"languages": ["python", "javascript"]},
            "repository_url": "https://github.com/user/repo"
        }

    Returns:
        201: Project created
        400: Validation error
    """
    data = request.get_json()

    project = Project(
        organization_id=g.current_organization.id,
        name=data["name"],
        description=data.get("description"),
        tech_stack=data.get("tech_stack", {}),
        repository_url=data.get("repository_url"),
        settings={},
        is_active=True,
    )

    db.session.add(project)
    db.session.commit()

    # Clear cache
    cache.delete_memoized(list_projects)

    return success_response(
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "tech_stack": project.tech_stack,
            "repository_url": project.repository_url,
            "is_active": project.is_active,
            "created_at": project.created_at.isoformat(),
        },
        "Project created successfully",
        201,
    )


@projects_bp.route("/<int:project_id>", methods=["GET"])
@token_required
@organization_required
def get_project(project_id):
    """
    Get a specific project by ID.

    Returns:
        200: Project details
        404: Project not found
    """
    project = Project.query.filter_by(
        id=project_id, organization_id=g.current_organization.id
    ).first()

    if not project:
        return error_response("Project not found", 404)

    return success_response(
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "tech_stack": project.tech_stack,
            "repository_url": project.repository_url,
            "settings": project.settings,
            "is_active": project.is_active,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }
    )


@projects_bp.route("/<int:project_id>", methods=["PUT"])
@token_required
@organization_required
def update_project(project_id):
    """
    Update a project.

    Request Body:
        {
            "name": "Updated Name",
            "description": "Updated description",
            "tech_stack": {...},
            "repository_url": "...",
            "is_active": true
        }

    Returns:
        200: Project updated
        404: Project not found
    """
    project = Project.query.filter_by(
        id=project_id, organization_id=g.current_organization.id
    ).first()

    if not project:
        return error_response("Project not found", 404)

    data = request.get_json()

    # Update fields
    if "name" in data:
        project.name = data["name"]
    if "description" in data:
        project.description = data["description"]
    if "tech_stack" in data:
        project.tech_stack = data["tech_stack"]
    if "repository_url" in data:
        project.repository_url = data["repository_url"]
    if "is_active" in data:
        project.is_active = data["is_active"]

    db.session.commit()

    # Clear cache
    cache.delete_memoized(list_projects)

    return success_response(
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "tech_stack": project.tech_stack,
            "repository_url": project.repository_url,
            "is_active": project.is_active,
            "updated_at": project.updated_at.isoformat(),
        },
        "Project updated successfully",
    )


@projects_bp.route("/<int:project_id>", methods=["DELETE"])
@token_required
@organization_required
def delete_project(project_id):
    """
    Delete a project.

    Returns:
        200: Project deleted
        404: Project not found
    """
    project = Project.query.filter_by(
        id=project_id, organization_id=g.current_organization.id
    ).first()

    if not project:
        return error_response("Project not found", 404)

    db.session.delete(project)
    db.session.commit()

    # Clear cache
    cache.delete_memoized(list_projects)

    return success_response(message="Project deleted successfully")
