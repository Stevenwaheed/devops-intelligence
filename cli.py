"""Flask CLI commands for database management."""
import click
from flask import Flask
from app import create_app
from app.extensions import db
from app.models import (
    Organization,
    User,
    Project,
    SubscriptionTier,
    UserRole,
)


@click.group()
def cli():
    """Database management commands."""
    pass


@cli.command()
def init_db():
    """Initialize the database with tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        click.echo("✅ Database tables created successfully!")


@cli.command()
def drop_db():
    """Drop all database tables."""
    app = create_app()
    with app.app_context():
        if click.confirm("Are you sure you want to drop all tables?"):
            db.drop_all()
            click.echo("✅ Database tables dropped successfully!")


@cli.command()
def seed_db():
    """Seed the database with sample data."""
    app = create_app()
    with app.app_context():
        # Create sample organization
        org = Organization(
            name="Demo Organization",
            subscription_tier=SubscriptionTier.PRO,
            settings={"timezone": "UTC", "notifications_enabled": True},
        )
        db.session.add(org)
        db.session.flush()

        # Create sample user
        user = User(
            email="demo@devguard.io",
            organization_id=org.id,
            role=UserRole.OWNER,
            is_active=True,
        )
        user.set_password("demo123")
        db.session.add(user)
        db.session.flush()

        # Create sample project
        project = Project(
            organization_id=org.id,
            name="Demo Project",
            description="A sample project for demonstration",
            tech_stack={
                "languages": ["python", "javascript"],
                "frameworks": ["flask", "react"],
                "databases": ["postgresql", "redis"],
            },
            repository_url="https://github.com/demo/project",
            is_active=True,
        )
        db.session.add(project)

        db.session.commit()

        click.echo("✅ Database seeded successfully!")
        click.echo("\n📧 Demo credentials:")
        click.echo("   Email: demo@devguard.io")
        click.echo("   Password: demo123")


@cli.command()
@click.option("--email", prompt=True, help="User email")
@click.option("--password", prompt=True, hide_input=True, help="User password")
@click.option("--org-name", prompt=True, help="Organization name")
def create_user(email, password, org_name):
    """Create a new user and organization."""
    app = create_app()
    with app.app_context():
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo(f"❌ User with email {email} already exists!")
            return

        # Create organization
        org = Organization(
            name=org_name, subscription_tier=SubscriptionTier.FREE, settings={}
        )
        db.session.add(org)
        db.session.flush()

        # Create user
        user = User(
            email=email, organization_id=org.id, role=UserRole.OWNER, is_active=True
        )
        user.set_password(password)
        db.session.add(user)

        db.session.commit()

        click.echo(f"✅ User created successfully!")
        click.echo(f"   Email: {email}")
        click.echo(f"   Organization: {org_name}")


if __name__ == "__main__":
    cli()
