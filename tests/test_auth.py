"""Test authentication endpoints."""
import pytest


def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "organization_name": "New Organization"
        }
    )
    
    assert response.status_code == 201
    assert "data" in response.json
    assert "token" in response.json["data"]
    assert response.json["data"]["user"]["email"] == "newuser@example.com"


def test_register_duplicate_email(client, user):
    """Test registration with duplicate email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "organization_name": "Another Org"
        }
    )
    
    assert response.status_code == 409
    assert "error" in response.json


def test_login_success(client, user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    assert "data" in response.json
    assert "token" in response.json["data"]


def test_login_invalid_credentials(client, user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "error" in response.json


def test_get_current_user(client, auth_headers):
    """Test getting current user information."""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "data" in response.json
    assert response.json["data"]["email"] == "test@example.com"


def test_get_current_user_no_auth(client):
    """Test getting current user without authentication."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401
    assert "error" in response.json
