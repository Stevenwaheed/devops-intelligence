# DevGuard API Examples

This document provides practical examples for using the DevGuard API.

## Authentication

### Register a New User

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!",
    "organization_name": "Acme Corporation"
  }'
```

**Response:**
```json
{
  "data": {
    "user": {
      "id": 1,
      "email": "john@example.com",
      "role": "owner"
    },
    "organization": {
      "id": 1,
      "name": "Acme Corporation",
      "subscription_tier": "free"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "User registered successfully"
}
```

### Login

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

## Projects

### Create a Project

```bash
curl -X POST http://localhost:5000/api/v1/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "E-commerce Platform",
    "description": "Main e-commerce application",
    "tech_stack": {
      "languages": ["python", "javascript"],
      "frameworks": ["flask", "react"],
      "databases": ["postgresql", "redis"]
    },
    "repository_url": "https://github.com/acme/ecommerce"
  }'
```

### List Projects

```bash
# Basic list
curl -X GET http://localhost:5000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN"

# With pagination
curl -X GET "http://localhost:5000/api/v1/projects?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by active status
curl -X GET "http://localhost:5000/api/v1/projects?is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Gateway

### Add an API Provider

```bash
curl -X POST http://localhost:5000/api/v1/api-gateway/providers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "OpenAI Production",
    "provider_type": "openai",
    "credentials": "sk-...",
    "is_active": true,
    "priority_order": 1
  }'
```

### Log an API Request

```bash
curl -X POST http://localhost:5000/api/v1/api-gateway/requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project_id": 1,
    "provider_id": 1,
    "endpoint": "/v1/chat/completions",
    "method": "POST",
    "status_code": 200,
    "latency_ms": 1250.5,
    "cost_usd": 0.002,
    "tokens_used": {
      "prompt": 150,
      "completion": 75
    },
    "environment": "production"
  }'
```

### Get Cost Analytics

```bash
# Last 30 days
curl -X GET "http://localhost:5000/api/v1/api-gateway/analytics/cost?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"

# For specific project
curl -X GET "http://localhost:5000/api/v1/api-gateway/analytics/cost?project_id=1&days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "data": {
    "daily_analytics": [
      {
        "date": "2024-01-01",
        "total_cost": 15.50,
        "request_count": 1250
      }
    ],
    "summary": {
      "total_cost": 465.00,
      "total_requests": 37500,
      "average_cost_per_request": 0.0124,
      "period_days": 30
    }
  }
}
```

### Create a Budget

```bash
curl -X POST http://localhost:5000/api/v1/api-gateway/budgets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project_id": 1,
    "period_start": "2024-01-01T00:00:00Z",
    "period_end": "2024-01-31T23:59:59Z",
    "allocated_amount_usd": 500.00,
    "alert_thresholds": {
      "warning": 80,
      "critical": 95
    },
    "actions_on_exceed": {
      "throttle": true,
      "notify": true
    }
  }'
```

## Database Optimizer

### Add a Database Connection

```bash
curl -X POST http://localhost:5000/api/v1/database-optimizer/connections \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project_id": 1,
    "name": "Production PostgreSQL",
    "database_type": "postgresql",
    "connection_string": "postgresql://user:pass@localhost:5432/db",
    "is_active": true
  }'
```

### Log a Query Pattern

```bash
curl -X POST http://localhost:5000/api/v1/database-optimizer/query-patterns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "connection_id": 1,
    "query_fingerprint": "a1b2c3d4e5f6...",
    "query_structure": "SELECT * FROM users WHERE id = ?",
    "execution_time_ms": 245.8,
    "rows_examined": 10000,
    "rows_returned": 1,
    "index_usage": {
      "used_indexes": [],
      "suggested_indexes": ["idx_users_id"]
    },
    "explain_plan": {
      "plan_type": "Seq Scan",
      "cost": 1000.00
    }
  }'
```

### Get Slow Queries

```bash
curl -X GET "http://localhost:5000/api/v1/database-optimizer/analytics/slow-queries?limit=10&days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "data": {
    "slow_queries": [
      {
        "query_fingerprint": "a1b2c3...",
        "query_structure": "SELECT * FROM orders WHERE...",
        "avg_execution_time_ms": 1250.5,
        "max_execution_time_ms": 3500.0,
        "execution_count": 450
      }
    ]
  }
}
```

### List Optimizations

```bash
# Get all optimizations
curl -X GET http://localhost:5000/api/v1/database-optimizer/optimizations \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by connection and minimum improvement
curl -X GET "http://localhost:5000/api/v1/database-optimizer/optimizations?connection_id=1&min_improvement=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Apply an Optimization

```bash
curl -X POST http://localhost:5000/api/v1/database-optimizer/optimizations/5/apply \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Dependency Scanner

### Create a Dependency Scan

```bash
curl -X POST http://localhost:5000/api/v1/dependency-scanner/scans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project_id": 1,
    "ecosystem": "npm",
    "scan_trigger": "manual",
    "total_dependencies": 250,
    "total_vulnerabilities": 8,
    "overall_risk_score": 42.5,
    "scan_duration_ms": 5500
  }'
```

### Get Scan Details

```bash
curl -X GET http://localhost:5000/api/v1/dependency-scanner/scans/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Vulnerabilities

```bash
# All vulnerabilities
curl -X GET http://localhost:5000/api/v1/dependency-scanner/vulnerabilities \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by severity and project
curl -X GET "http://localhost:5000/api/v1/dependency-scanner/vulnerabilities?project_id=1&severity=critical" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Only exploitable vulnerabilities
curl -X GET "http://localhost:5000/api/v1/dependency-scanner/vulnerabilities?exploit_available=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Risk Summary

```bash
# All projects
curl -X GET http://localhost:5000/api/v1/dependency-scanner/analytics/risk-summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# Specific project
curl -X GET "http://localhost:5000/api/v1/dependency-scanner/analytics/risk-summary?project_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "data": {
    "projects": [
      {
        "project_id": 1,
        "project_name": "E-commerce Platform",
        "total_dependencies": 250,
        "total_vulnerabilities": 8,
        "overall_risk_score": 42.5,
        "last_scan": "2024-01-15T10:30:00Z"
      }
    ],
    "summary": {
      "total_dependencies": 250,
      "total_vulnerabilities": 8,
      "average_risk_score": 42.5,
      "projects_scanned": 1
    }
  }
}
```

## Insights

### List Insights

```bash
# All insights
curl -X GET http://localhost:5000/api/v1/insights \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by category and severity
curl -X GET "http://localhost:5000/api/v1/insights?category=cost&severity=critical" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Only unresolved insights
curl -X GET "http://localhost:5000/api/v1/insights?resolved=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Acknowledge an Insight

```bash
curl -X POST http://localhost:5000/api/v1/insights/1/acknowledge \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Resolve an Insight

```bash
curl -X POST http://localhost:5000/api/v1/insights/1/resolve \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Python SDK Example

```python
import requests

class DevGuardClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def create_project(self, name, description, tech_stack):
        response = requests.post(
            f"{self.base_url}/api/v1/projects",
            headers=self.headers,
            json={
                "name": name,
                "description": description,
                "tech_stack": tech_stack
            }
        )
        return response.json()
    
    def log_api_request(self, project_id, provider_id, endpoint, 
                       method, status_code, latency_ms, cost_usd):
        response = requests.post(
            f"{self.base_url}/api/v1/api-gateway/requests",
            headers=self.headers,
            json={
                "project_id": project_id,
                "provider_id": provider_id,
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd
            }
        )
        return response.json()
    
    def get_cost_analytics(self, project_id=None, days=30):
        params = {"days": days}
        if project_id:
            params["project_id"] = project_id
        
        response = requests.get(
            f"{self.base_url}/api/v1/api-gateway/analytics/cost",
            headers=self.headers,
            params=params
        )
        return response.json()

# Usage
client = DevGuardClient("http://localhost:5000", "your-token-here")

# Create a project
project = client.create_project(
    name="My API Project",
    description="API monitoring project",
    tech_stack={"languages": ["python"]}
)

# Log an API request
client.log_api_request(
    project_id=project["data"]["id"],
    provider_id=1,
    endpoint="/v1/chat/completions",
    method="POST",
    status_code=200,
    latency_ms=150.5,
    cost_usd=0.002
)

# Get analytics
analytics = client.get_cost_analytics(project_id=project["data"]["id"], days=7)
print(f"Total cost: ${analytics['data']['summary']['total_cost']}")
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "details": {
    "field": "Additional error details"
  }
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing or invalid token)
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
