#!/bin/bash

# DevGuard Setup Script

echo "🚀 Setting up DevGuard - DevOps Intelligence Platform"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate random secret keys
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    
    # Update .env file
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    sed -i "s/your-jwt-secret-key-here/$JWT_SECRET_KEY/" .env
    
    echo "✅ .env file created with generated secret keys"
else
    echo "ℹ️  .env file already exists, skipping..."
fi

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose run --rm app flask db upgrade

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check health
echo "🏥 Checking service health..."
curl -f http://localhost:5000/health || echo "⚠️  Health check failed"

echo ""
echo "=================================================="
echo "✅ DevGuard setup complete!"
echo ""
echo "📍 API is running at: http://localhost:5000"
echo "📍 Health check: http://localhost:5000/health"
echo ""
echo "📚 Next steps:"
echo "  1. Register a user: POST /api/v1/auth/register"
echo "  2. Login: POST /api/v1/auth/login"
echo "  3. Create a project: POST /api/v1/projects"
echo ""
echo "📖 See README.md for full API documentation"
echo "=================================================="
