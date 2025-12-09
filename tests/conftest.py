"""Test configuration and fixtures."""
import pytest
from app import create_app
from app.extensions import db
from app.models import Organization, User, Project, SubscriptionTier, UserRole


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def organization(app):
    """Create test organization."""
    org = Organization(
        name="Test Organization",
        subscription_tier=SubscriptionTier.FREE,
        settings={}
    )
    db.session.add(org)
    db.session.commit()
    return org


@pytest.fixture
def user(app, organization):
    """Create test user."""
    user = User(
        email="test@example.com",
        organization_id=organization.id,
        role=UserRole.OWNER,
        is_active=True
    )
    user.set_password("testpassword123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers(client, user):
    """Get authentication headers."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = response.json["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def project(app, organization):
    """Create test project."""
    project = Project(
        organization_id=organization.id,
        name="Test Project",
        description="Test project description",
        tech_stack={"languages": ["python"]},
        is_active=True
    )
    db.session.add(project)
    db.session.commit()
    return project
