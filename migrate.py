"""Database migration script using Flask-Migrate."""
from flask import Flask
from flask_migrate import Migrate, init, migrate as create_migration, upgrade
from app import create_app
from app.extensions import db

# Create app
app = create_app()

# Initialize Flask-Migrate
migrate_obj = Migrate(app, db)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python migrate.py [init|migrate|upgrade]")
        sys.exit(1)

    command = sys.argv[1]

    with app.app_context():
        if command == "init":
            init()
            print("✅ Migration repository initialized")
        elif command == "migrate":
            message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
            create_migration(message=message)
            print(f"✅ Migration created: {message}")
        elif command == "upgrade":
            upgrade()
            print("✅ Database upgraded to latest migration")
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: init, migrate, upgrade")
