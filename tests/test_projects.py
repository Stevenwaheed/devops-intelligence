"""Test projects endpoints."""
import pytest


def test_list_projects(client, auth_headers, project):
    """Test listing projects."""
    response = client.get(
        "/api/v1/projects",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "data" in response.json
    assert "projects" in response.json["data"]
    assert len(response.json["data"]["projects"]) > 0


def test_create_project(client, auth_headers):
    """Test creating a new project."""
    response = client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={
            "name": "New Project",
            "description": "A new test project",
            "tech_stack": {"languages": ["javascript", "python"]},
            "repository_url": "https://github.com/test/repo"
        }
    )
    
    assert response.status_code == 201
    assert "data" in response.json
    assert response.json["data"]["name"] == "New Project"


def test_get_project(client, auth_headers, project):
    """Test getting a specific project."""
    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "data" in response.json
    assert response.json["data"]["id"] == project.id


def test_update_project(client, auth_headers, project):
    """Test updating a project."""
    response = client.put(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers,
        json={
            "name": "Updated Project Name",
            "description": "Updated description"
        }
    )
    
    assert response.status_code == 200
    assert "data" in response.json
    assert response.json["data"]["name"] == "Updated Project Name"


def test_delete_project(client, auth_headers, project):
    """Test deleting a project."""
    response = client.delete(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify project is deleted
    get_response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404
