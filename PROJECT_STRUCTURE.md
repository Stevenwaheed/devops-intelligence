# DevGuard Project Structure

## 📁 Directory Structure

```
DevOps-Intelligence/
├── app/
│   ├── __init__.py              # Application factory
│   ├── extensions.py            # Flask extensions (SQLAlchemy, Redis, Celery)
│   ├── tasks.py                 # Celery background tasks
│   ├── api/
│   │   ├── __init__.py          # Blueprint registration
│   │   ├── utils.py             # API utilities (pagination, auth decorators)
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── organizations.py    # Organization management
│   │   ├── projects.py          # Project CRUD operations
│   │   ├── api_gateway.py       # API Gateway & Cost Optimizer
│   │   ├── database_optimizer.py # Database Query Optimizer
│   │   ├── dependency_scanner.py # Dependency Risk Scanner
│   │   └── insights.py          # AI-generated insights
│   └── models/
│       ├── __init__.py          # Model exports
│       ├── core.py              # Core models (Organization, User, Project)
│       ├── api_gateway.py       # API Gateway models
│       ├── database_optimizer.py # Database Optimizer models
│       ├── dependency_scanner.py # Dependency Scanner models
│       └── shared.py            # Shared models (Insights, Audit, Notifications)
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_auth.py             # Authentication tests
│   └── test_projects.py         # Project tests
├── init-scripts/
│   └── 01-timescaledb.sql       # TimescaleDB initialization
├── config.py                    # Configuration management
├── run.py                       # Application entry point
├── migrate.py                   # Database migration script
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Multi-container setup
├── nginx.conf                   # Nginx reverse proxy config
├── setup.sh                     # Automated setup script
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

## 🗄️ Database Schema Overview

### Core Tables
- **organizations**: Organization/tenant data
- **users**: User accounts with authentication
- **projects**: Projects within organizations

### API Gateway Component
- **api_providers**: API provider configurations (OpenAI, Anthropic, etc.)
- **api_configurations**: Project-specific API settings
- **api_requests**: Time-series request logs (TimescaleDB hypertable)
- **api_budgets**: Budget tracking and limits
- **api_alerts**: Cost and performance alerts

### Database Optimizer Component
- **database_connections**: Database connection configurations
- **query_patterns**: Time-series query execution logs (TimescaleDB hypertable)
- **query_optimizations**: Optimization recommendations
- **database_metrics**: Time-series database performance metrics (TimescaleDB hypertable)
- **database_indexes**: Index tracking and recommendations

### Dependency Scanner Component
- **dependency_scans**: Scan metadata and results
- **dependencies**: Package dependency tree
- **vulnerabilities**: CVE and security vulnerabilities
- **maintenance_metrics**: Package health metrics
- **dependency_alternatives**: Alternative package suggestions
- **dependency_updates**: Update recommendations

### Shared Tables
- **insights**: AI-generated insights across all components
- **audit_logs**: Complete audit trail
- **notifications**: User notifications
- **integration_webhooks**: External integrations

## 🔑 Key Features Implemented

### 1. **Optimized Database Design**
- ✅ SQLAlchemy 2.0 with type hints
- ✅ Proper foreign key relationships
- ✅ Comprehensive indexing for performance
- ✅ TimescaleDB hypertables for time-series data
- ✅ Continuous aggregates for analytics
- ✅ Automatic data retention policies

### 2. **High-Performance APIs**
- ✅ Pagination on all list endpoints
- ✅ Query parameter filtering
- ✅ Redis caching for frequently accessed data
- ✅ Rate limiting to prevent abuse
- ✅ JWT authentication
- ✅ Standardized response format

### 3. **Production-Ready Infrastructure**
- ✅ Docker multi-stage builds
- ✅ Docker Compose orchestration
- ✅ Nginx reverse proxy with rate limiting
- ✅ Celery for background tasks
- ✅ Health check endpoints
- ✅ Structured logging

### 4. **Security Best Practices**
- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Encrypted credentials storage
- ✅ CORS configuration
- ✅ Security headers
- ✅ Non-root Docker containers

### 5. **Developer Experience**
- ✅ Comprehensive API documentation
- ✅ Automated setup script
- ✅ Database migration system
- ✅ Unit tests with pytest
- ✅ Environment-based configuration
- ✅ Clear project structure

## 🚀 Quick Start Commands

### Using Docker Compose (Recommended)
```bash
# Setup everything automatically
chmod +x setup.sh
./setup.sh

# Or manually:
docker-compose up -d
docker-compose exec app flask db upgrade
```

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python migrate.py init
python migrate.py migrate "Initial migration"
python migrate.py upgrade

# Run application
python run.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 📊 API Endpoints Summary

### Authentication (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token
- `GET /me` - Get current user
- `POST /refresh` - Refresh JWT token
- `POST /change-password` - Change password

### Projects (`/api/v1/projects`)
- `GET /` - List projects (paginated)
- `POST /` - Create project
- `GET /<id>` - Get project details
- `PUT /<id>` - Update project
- `DELETE /<id>` - Delete project

### API Gateway (`/api/v1/api-gateway`)
- `GET /providers` - List API providers
- `POST /providers` - Add provider
- `GET /requests` - List API requests (paginated, filtered)
- `POST /requests` - Log API request
- `GET /analytics/cost` - Cost analytics
- `GET /analytics/latency` - Latency analytics
- `GET /budgets` - List budgets
- `POST /budgets` - Create budget

### Database Optimizer (`/api/v1/database-optimizer`)
- `GET /connections` - List database connections
- `POST /connections` - Add connection
- `GET /query-patterns` - List query patterns (paginated, filtered)
- `POST /query-patterns` - Log query pattern
- `GET /optimizations` - List optimizations
- `POST /optimizations/<id>/apply` - Apply optimization
- `GET /analytics/performance` - Performance analytics
- `GET /analytics/slow-queries` - Top slow queries

### Dependency Scanner (`/api/v1/dependency-scanner`)
- `GET /scans` - List scans (paginated, filtered)
- `POST /scans` - Create scan
- `GET /scans/<id>` - Get scan details
- `GET /dependencies/<id>` - Get dependency details
- `GET /vulnerabilities` - List vulnerabilities (paginated, filtered)
- `GET /analytics/risk-summary` - Risk summary

### Insights (`/api/v1/insights`)
- `GET /` - List insights (paginated, filtered)
- `POST /<id>/acknowledge` - Acknowledge insight
- `POST /<id>/resolve` - Resolve insight

## 🔧 Configuration

### Environment Variables
All configuration is managed through environment variables. See `.env.example` for all available options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `CELERY_BROKER_URL` - Celery broker URL
- `CELERY_RESULT_BACKEND` - Celery result backend URL

### Database Configuration
- Connection pooling: 10 connections, max overflow 20
- Pool recycle: 3600 seconds
- Pre-ping enabled for connection health checks

### Caching Strategy
- Redis caching for analytics endpoints (5 minutes TTL)
- Query result caching for list endpoints (1 minute TTL)
- Cache invalidation on data mutations

### Rate Limiting
- Default: 200 requests/day, 50 requests/hour per IP
- Auth endpoints: 5 requests/minute
- Configurable per endpoint

## 📈 Performance Optimizations

### Database Level
1. **Indexes**: Comprehensive indexing on foreign keys and query filters
2. **TimescaleDB**: Hypertables for time-series data with automatic partitioning
3. **Continuous Aggregates**: Pre-computed hourly/daily aggregates
4. **Retention Policies**: Automatic data cleanup after 90 days

### Application Level
1. **Pagination**: All list endpoints paginated (default 20, max 100)
2. **Caching**: Redis caching for expensive queries
3. **Connection Pooling**: Reuse database connections
4. **Async Tasks**: Background processing with Celery

### Infrastructure Level
1. **Nginx**: Reverse proxy with rate limiting and compression
2. **Gunicorn**: Multi-worker WSGI server with gevent
3. **Docker**: Multi-stage builds for smaller images
4. **Health Checks**: Container health monitoring

## 🧪 Testing Strategy

### Unit Tests
- Authentication flows
- CRUD operations
- API validation
- Error handling

### Integration Tests
- End-to-end API workflows
- Database transactions
- Celery task execution

### Performance Tests
- Load testing with locust
- Database query performance
- API response times

## 🔐 Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Password Storage**: bcrypt hashing with configurable rounds
3. **Credentials**: Encrypted storage for API keys and connection strings
4. **Rate Limiting**: Prevent brute force and DDoS
5. **CORS**: Configurable allowed origins
6. **Headers**: Security headers (X-Frame-Options, etc.)
7. **Validation**: Input validation on all endpoints
8. **Audit Logs**: Complete audit trail of all actions

## 📝 Next Steps

### Immediate
1. Run setup script: `./setup.sh`
2. Create first user via `/api/v1/auth/register`
3. Create a project via `/api/v1/projects`
4. Start logging data to the platform

### Short Term
1. Implement actual ML models for predictions
2. Add more database types (MongoDB, MariaDB)
3. Integrate with vulnerability databases
4. Build CLI tool for developers
5. Create web dashboard

### Long Term
1. Multi-region deployment
2. Advanced analytics and reporting
3. Custom ML model training
4. Marketplace for integrations
5. Enterprise features (SSO, RBAC)

## 🤝 Contributing

See README.md for contribution guidelines.

## 📄 License

MIT License - See LICENSE file for details.
