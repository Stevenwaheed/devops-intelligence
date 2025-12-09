# DevGuard - DevOps Intelligence Platform

A comprehensive platform combining API cost optimization, database performance monitoring, and dependency risk management into a unified developer operations intelligence suite.

## 🚀 Features

### 1. API Gateway & Cost Optimizer
- **Multi-provider support**: OpenAI, Anthropic, AWS Bedrock, Google Vertex AI, Azure OpenAI
- **Smart routing**: Route by cost, latency, or quality
- **Real-time cost tracking**: Monitor API spending across all providers
- **Budget management**: Set budgets and get alerts before overspending
- **Predictive analytics**: Forecast future API costs

### 2. Database Query Optimizer
- **Query analysis**: Identify slow queries, N+1 problems, and missing indexes
- **Performance insights**: Get actionable recommendations to improve database performance
- **Multi-database support**: PostgreSQL, MySQL, MongoDB
- **Automatic optimizations**: One-click index creation and query rewrites
- **Historical tracking**: Monitor performance trends over time

### 3. Dependency Risk Scanner
- **Security scanning**: Detect vulnerabilities across npm, pip, Maven, Go, and more
- **Abandonment prediction**: AI-powered detection of at-risk dependencies
- **License compliance**: Identify license conflicts and compatibility issues
- **Alternative suggestions**: Get recommendations for safer, better-maintained packages
- **Automated updates**: Generate PRs for low-risk dependency updates

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ with TimescaleDB extension
- Redis 7+

## 🛠️ Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DevOps-Intelligence
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env and set your secret keys
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec app flask db upgrade
   ```

5. **Access the API**
   - API: http://localhost:5000
   - Health check: http://localhost:5000/health

### Local Development

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up -d postgres redis
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   flask run
   ```

## 📚 API Documentation

### Authentication

All API endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.

**Register a new user:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "organization_name": "My Organization"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

**Use the token in subsequent requests:**
```bash
curl -H "Authorization: Bearer <your-token>" \
  http://localhost:5000/api/v1/projects
```

### Core Endpoints

#### Projects
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create a new project
- `GET /api/v1/projects/<id>` - Get project details
- `PUT /api/v1/projects/<id>` - Update project
- `DELETE /api/v1/projects/<id>` - Delete project

#### API Gateway
- `GET /api/v1/api-gateway/providers` - List API providers
- `POST /api/v1/api-gateway/providers` - Add new provider
- `GET /api/v1/api-gateway/requests` - List API requests
- `POST /api/v1/api-gateway/requests` - Log API request
- `GET /api/v1/api-gateway/analytics/cost` - Get cost analytics
- `GET /api/v1/api-gateway/analytics/latency` - Get latency analytics
- `GET /api/v1/api-gateway/budgets` - List budgets
- `POST /api/v1/api-gateway/budgets` - Create budget

#### Database Optimizer
- `GET /api/v1/database-optimizer/connections` - List database connections
- `POST /api/v1/database-optimizer/connections` - Add connection
- `GET /api/v1/database-optimizer/query-patterns` - List query patterns
- `POST /api/v1/database-optimizer/query-patterns` - Log query pattern
- `GET /api/v1/database-optimizer/optimizations` - List optimizations
- `POST /api/v1/database-optimizer/optimizations/<id>/apply` - Apply optimization
- `GET /api/v1/database-optimizer/analytics/performance` - Performance analytics
- `GET /api/v1/database-optimizer/analytics/slow-queries` - Top slow queries

#### Dependency Scanner
- `GET /api/v1/dependency-scanner/scans` - List scans
- `POST /api/v1/dependency-scanner/scans` - Create scan
- `GET /api/v1/dependency-scanner/scans/<id>` - Get scan details
- `GET /api/v1/dependency-scanner/dependencies/<id>` - Get dependency details
- `GET /api/v1/dependency-scanner/vulnerabilities` - List vulnerabilities
- `GET /api/v1/dependency-scanner/analytics/risk-summary` - Risk summary

#### Insights
- `GET /api/v1/insights` - List AI-generated insights
- `POST /api/v1/insights/<id>/acknowledge` - Acknowledge insight
- `POST /api/v1/insights/<id>/resolve` - Resolve insight

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask 3.0, SQLAlchemy 2.0
- **Database**: PostgreSQL 15 with TimescaleDB extension
- **Cache**: Redis 7
- **Task Queue**: Celery with Redis broker
- **Web Server**: Gunicorn with gevent workers
- **Reverse Proxy**: Nginx
- **Containerization**: Docker & Docker Compose

### Database Schema
The platform uses a comprehensive database schema with:
- **Core tables**: Organizations, Users, Projects
- **API Gateway**: Providers, Configurations, Requests (time-series), Budgets, Alerts
- **Database Optimizer**: Connections, Query Patterns (time-series), Optimizations, Metrics, Indexes
- **Dependency Scanner**: Scans, Dependencies, Vulnerabilities, Maintenance Metrics, Alternatives
- **Shared**: Insights, Audit Logs, Notifications, Webhooks

### Performance Optimizations
- **Pagination**: All list endpoints support pagination
- **Caching**: Redis caching for frequently accessed data
- **Indexing**: Comprehensive database indexes for fast queries
- **Time-series optimization**: TimescaleDB hypertables and continuous aggregates
- **Connection pooling**: SQLAlchemy connection pool with pre-ping
- **Rate limiting**: API rate limiting to prevent abuse

## 🔒 Security

- **Password hashing**: bcrypt with configurable rounds
- **JWT authentication**: Secure token-based authentication
- **Encrypted credentials**: All API keys and connection strings are encrypted
- **Rate limiting**: Prevents brute force and DDoS attacks
- **CORS configuration**: Configurable CORS policies
- **Security headers**: X-Frame-Options, X-Content-Type-Options, etc.

## 📊 Monitoring & Observability

- **Health checks**: `/health` endpoint for container health monitoring
- **Prometheus metrics**: Optional metrics export
- **Structured logging**: JSON logging for easy parsing
- **Audit logs**: Complete audit trail of all actions

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## 📦 Deployment

### Production Checklist

1. **Environment Variables**
   - Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
   - Configure production database URL
   - Set up email configuration for alerts
   - Configure external service API keys

2. **Database**
   - Run migrations: `flask db upgrade`
   - Set up automated backups
   - Configure retention policies

3. **Security**
   - Enable HTTPS with valid SSL certificates
   - Configure firewall rules
   - Set up monitoring and alerting
   - Enable audit logging

4. **Scaling**
   - Increase Gunicorn workers based on CPU cores
   - Scale Celery workers based on workload
   - Configure database connection pool
   - Set up load balancer if needed

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- TimescaleDB for time-series database capabilities
- Flask and SQLAlchemy communities
- All open-source contributors

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for developers who care about cost, performance, and security.**
