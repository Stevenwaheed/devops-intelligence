# DevGuard CLI Development Guide

A comprehensive guide to building a Command-Line Interface (CLI) for the DevGuard DevOps Intelligence Platform.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [Implementation Guide](#implementation-guide)
7. [Command Reference](#command-reference)
8. [Best Practices](#best-practices)
9. [Testing](#testing)
10. [Distribution](#distribution)

---

## Overview

The DevGuard CLI is a command-line tool that provides developers with a seamless interface to interact with the DevGuard platform. It enables users to manage projects, monitor API costs, optimize database queries, scan dependencies, and view AI-generated insights directly from their terminal.

### Key Features

- **Authentication Management**: Login, logout, and token management
- **Project Management**: Create, list, update, and delete projects
- **API Gateway**: Monitor API costs, view analytics, manage providers
- **Database Optimizer**: Analyze queries, view optimizations, track performance
- **Dependency Scanner**: Scan dependencies, view vulnerabilities, check risk scores
- **Insights**: View and manage AI-generated insights
- **Interactive Mode**: Rich interactive prompts for better UX
- **Output Formats**: Support for JSON, table, and human-readable formats
- **Configuration**: Store API endpoint and credentials locally

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DevGuard CLI                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Commands   │  │   Services   │  │    Config    │     │
│  │              │  │              │  │              │     │
│  │ - auth       │  │ - HTTP       │  │ - Settings   │     │
│  │ - projects   │  │ - Auth       │  │ - Tokens     │     │
│  │ - api        │  │ - API Client │  │ - Profiles   │     │
│  │ - database   │  │ - Formatters │  │              │     │
│  │ - deps       │  │              │  │              │     │
│  │ - insights   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Utilities & Helpers                     │  │
│  │  - Output Formatting  - Error Handling              │  │
│  │  - Pagination         - Validation                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              DevGuard API Server (Flask)                    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → CLI parses commands and arguments
2. **Authentication** → CLI retrieves stored token or prompts for login
3. **API Request** → CLI constructs and sends HTTP request to API
4. **Response Processing** → CLI receives and validates response
5. **Output Formatting** → CLI formats data based on user preference
6. **Display** → CLI presents formatted output to user

---

## Technology Stack

### Recommended Technologies

#### Python (Recommended)

```python
# Core Libraries
click==8.1.7           # Command-line interface creation
requests==2.31.0       # HTTP client
rich==13.7.0           # Rich terminal output
pydantic==2.5.0        # Data validation
python-dotenv==1.0.0   # Environment management
keyring==24.3.0        # Secure credential storage
tabulate==0.9.0        # Table formatting
```

#### Alternative: Node.js/TypeScript

```json
{
  "dependencies": {
    "commander": "^11.1.0",      // CLI framework
    "axios": "^1.6.2",           // HTTP client
    "chalk": "^5.3.0",           // Terminal styling
    "inquirer": "^9.2.12",       // Interactive prompts
    "conf": "^12.0.0",           // Config management
    "ora": "^7.0.1",             // Spinners
    "cli-table3": "^0.6.3"       // Tables
  }
}
```

#### Alternative: Go

```go
// Core Libraries
github.com/spf13/cobra        // CLI framework
github.com/spf13/viper        // Configuration
github.com/go-resty/resty/v2  // HTTP client
github.com/olekukonko/tablewriter  // Tables
github.com/fatih/color        // Colors
```

---

## Project Structure

### Python CLI Structure

```
devguard-cli/
├── devguard/
│   ├── __init__.py
│   ├── __main__.py              # Entry point
│   ├── cli.py                   # Main CLI setup
│   │
│   ├── commands/                # Command modules
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication commands
│   │   ├── projects.py          # Project management
│   │   ├── api_gateway.py       # API gateway commands
│   │   ├── database.py          # Database optimizer
│   │   ├── dependencies.py      # Dependency scanner
│   │   └── insights.py          # Insights commands
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── api_client.py        # API communication
│   │   ├── auth_service.py      # Authentication logic
│   │   └── config_service.py    # Configuration management
│   │
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── api_request.py
│   │   └── insight.py
│   │
│   ├── utils/                   # Utilities
│   │   ├── __init__.py
│   │   ├── formatters.py        # Output formatting
│   │   ├── validators.py        # Input validation
│   │   ├── errors.py            # Error handling
│   │   └── helpers.py           # Helper functions
│   │
│   └── config/                  # Configuration
│       ├── __init__.py
│       ├── settings.py          # Default settings
│       └── constants.py         # Constants
│
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_projects.py
│   └── test_api_client.py
│
├── docs/                        # Documentation
│   ├── commands.md
│   └── examples.md
│
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── requirements-dev.txt         # Dev dependencies
├── README.md                    # Main documentation
├── LICENSE                      # License file
└── .gitignore                   # Git ignore rules
```

---

## Core Components

### 1. Configuration Management

Store user configuration, API endpoints, and authentication tokens.

**Location**: `~/.devguard/config.json`

```json
{
  "api_url": "https://api.devguard.io/api/v1",
  "current_profile": "default",
  "profiles": {
    "default": {
      "api_url": "https://api.devguard.io/api/v1",
      "token": "encrypted_token_here",
      "organization_id": 1,
      "user_email": "user@example.com"
    },
    "staging": {
      "api_url": "https://staging.devguard.io/api/v1",
      "token": "encrypted_token_here"
    }
  },
  "preferences": {
    "output_format": "table",
    "color": true,
    "pagination": true,
    "items_per_page": 20
  }
}
```

### 2. Authentication Service

Handle login, logout, token storage, and token refresh.

```python
# services/auth_service.py
import keyring
from typing import Optional
from .api_client import APIClient

class AuthService:
    SERVICE_NAME = "devguard-cli"
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
    
    def login(self, email: str, password: str) -> dict:
        """Authenticate user and store token."""
        response = self.api_client.post('/auth/login', {
            'email': email,
            'password': password
        })
        
        if response.get('data'):
            token = response['data']['token']
            self.store_token(email, token)
            return response['data']
        
        raise AuthenticationError("Login failed")
    
    def store_token(self, email: str, token: str):
        """Securely store authentication token."""
        keyring.set_password(self.SERVICE_NAME, email, token)
    
    def get_token(self, email: str) -> Optional[str]:
        """Retrieve stored authentication token."""
        return keyring.get_password(self.SERVICE_NAME, email)
    
    def logout(self, email: str):
        """Remove stored authentication token."""
        keyring.delete_password(self.SERVICE_NAME, email)
    
    def refresh_token(self) -> str:
        """Refresh the authentication token."""
        response = self.api_client.post('/auth/refresh')
        return response['data']['token']
```

### 3. API Client

Handle all HTTP communication with the DevGuard API.

```python
# services/api_client.py
import requests
from typing import Optional, Dict, Any
from .config_service import ConfigService
from ..utils.errors import APIError, AuthenticationError

class APIClient:
    def __init__(self, config_service: ConfigService):
        self.config = config_service
        self.base_url = config_service.get_api_url()
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DevGuard-CLI/1.0.0'
        }
        
        token = self.config.get_token()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed. Please login again.")
        
        if response.status_code == 404:
            raise APIError("Resource not found", status_code=404)
        
        if response.status_code >= 400:
            error_data = response.json() if response.text else {}
            raise APIError(
                error_data.get('error', 'Unknown error'),
                status_code=response.status_code,
                details=error_data.get('details')
            )
        
        return response.json()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, headers=self._get_headers(), json=data)
        return self._handle_response(response)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, headers=self._get_headers(), json=data)
        return self._handle_response(response)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url, headers=self._get_headers())
        return self._handle_response(response)
```

### 4. Output Formatters

Format output in different styles (table, JSON, YAML).

```python
# utils/formatters.py
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich import box
import json

class OutputFormatter:
    def __init__(self, format_type: str = 'table'):
        self.format_type = format_type
        self.console = Console()
    
    def format(self, data: Any, columns: List[str] = None):
        """Format data based on specified format type."""
        if self.format_type == 'json':
            return self._format_json(data)
        elif self.format_type == 'table':
            return self._format_table(data, columns)
        else:
            return self._format_human(data)
    
    def _format_json(self, data: Any) -> str:
        """Format as JSON."""
        return json.dumps(data, indent=2)
    
    def _format_table(self, data: List[Dict], columns: List[str]) -> None:
        """Format as rich table."""
        if not data:
            self.console.print("[yellow]No data to display[/yellow]")
            return
        
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        
        # Add columns
        for col in columns:
            table.add_column(col.replace('_', ' ').title())
        
        # Add rows
        for item in data:
            row = [str(item.get(col, '')) for col in columns]
            table.add_row(*row)
        
        self.console.print(table)
    
    def _format_human(self, data: Any) -> None:
        """Format in human-readable format."""
        if isinstance(data, dict):
            for key, value in data.items():
                self.console.print(f"[cyan]{key}:[/cyan] {value}")
        elif isinstance(data, list):
            for item in data:
                self.console.print(f"• {item}")
        else:
            self.console.print(data)
    
    def success(self, message: str):
        """Display success message."""
        self.console.print(f"[green]✓[/green] {message}")
    
    def error(self, message: str):
        """Display error message."""
        self.console.print(f"[red]✗[/red] {message}")
    
    def warning(self, message: str):
        """Display warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
    
    def info(self, message: str):
        """Display info message."""
        self.console.print(f"[blue]ℹ[/blue] {message}")
```

---

## Implementation Guide

### Step 1: Setup Project

```bash
# Create project directory
mkdir devguard-cli
cd devguard-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install click requests rich pydantic python-dotenv keyring tabulate

# Create project structure
mkdir -p devguard/{commands,services,models,utils,config}
touch devguard/__init__.py
touch devguard/__main__.py
touch devguard/cli.py
```

### Step 2: Create Main CLI Entry Point

```python
# devguard/cli.py
import click
from rich.console import Console
from .commands import auth, projects, api_gateway, database, dependencies, insights
from .services.config_service import ConfigService

console = Console()

@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    """DevGuard CLI - DevOps Intelligence Platform"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = ConfigService()

# Register command groups
cli.add_command(auth.auth)
cli.add_command(projects.projects)
cli.add_command(api_gateway.api)
cli.add_command(database.database)
cli.add_command(dependencies.deps)
cli.add_command(insights.insights)

if __name__ == '__main__':
    cli()
```

### Step 3: Implement Authentication Commands

```python
# devguard/commands/auth.py
import click
from rich.console import Console
from ..services.auth_service import AuthService
from ..services.api_client import APIClient
from ..utils.errors import AuthenticationError

console = Console()

@click.group()
def auth():
    """Authentication commands"""
    pass

@auth.command()
@click.option('--email', prompt=True, help='Your email address')
@click.option('--password', prompt=True, hide_input=True, help='Your password')
@click.pass_context
def login(ctx, email, password):
    """Login to DevGuard"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        auth_service = AuthService(api_client)
        
        with console.status("[bold green]Logging in..."):
            result = auth_service.login(email, password)
        
        console.print(f"[green]✓[/green] Successfully logged in as {email}")
        console.print(f"Organization: {result['user']['organization_id']}")
        console.print(f"Role: {result['user']['role']}")
        
    except AuthenticationError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()

@auth.command()
@click.pass_context
def logout(ctx):
    """Logout from DevGuard"""
    try:
        config = ctx.obj['config']
        email = config.get_current_user_email()
        
        if not email:
            console.print("[yellow]⚠[/yellow] Not logged in")
            return
        
        auth_service = AuthService(APIClient(config))
        auth_service.logout(email)
        
        console.print(f"[green]✓[/green] Successfully logged out")
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()

@auth.command()
@click.pass_context
def whoami(ctx):
    """Show current user information"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        
        response = api_client.get('/auth/me')
        user = response['data']
        
        console.print(f"[cyan]Email:[/cyan] {user['email']}")
        console.print(f"[cyan]Role:[/cyan] {user['role']}")
        console.print(f"[cyan]Organization ID:[/cyan] {user['organization_id']}")
        console.print(f"[cyan]Created:[/cyan] {user['created_at']}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
```

### Step 4: Implement Project Commands

```python
# devguard/commands/projects.py
import click
from rich.console import Console
from ..services.api_client import APIClient
from ..utils.formatters import OutputFormatter

console = Console()

@click.group()
def projects():
    """Project management commands"""
    pass

@projects.command('list')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.option('--active/--all', default=True, help='Show only active projects')
@click.pass_context
def list_projects(ctx, format, active):
    """List all projects"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        formatter = OutputFormatter(format)
        
        params = {}
        if active:
            params['is_active'] = 'true'
        
        response = api_client.get('/projects', params=params)
        projects_data = response['data']['projects']
        
        if format == 'json':
            console.print(formatter.format(projects_data))
        else:
            columns = ['id', 'name', 'description', 'is_active', 'created_at']
            formatter.format(projects_data, columns)
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()

@projects.command('create')
@click.option('--name', prompt=True, help='Project name')
@click.option('--description', help='Project description')
@click.option('--repo-url', help='Repository URL')
@click.pass_context
def create_project(ctx, name, description, repo_url):
    """Create a new project"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        
        data = {'name': name}
        if description:
            data['description'] = description
        if repo_url:
            data['repository_url'] = repo_url
        
        with console.status("[bold green]Creating project..."):
            response = api_client.post('/projects', data)
        
        project = response['data']
        console.print(f"[green]✓[/green] Project created successfully")
        console.print(f"ID: {project['id']}")
        console.print(f"Name: {project['name']}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()

@projects.command('get')
@click.argument('project_id', type=int)
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
def get_project(ctx, project_id, format):
    """Get project details"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        formatter = OutputFormatter(format)
        
        response = api_client.get(f'/projects/{project_id}')
        project = response['data']
        
        if format == 'json':
            console.print(formatter.format(project))
        else:
            console.print(f"[cyan]ID:[/cyan] {project['id']}")
            console.print(f"[cyan]Name:[/cyan] {project['name']}")
            console.print(f"[cyan]Description:[/cyan] {project.get('description', 'N/A')}")
            console.print(f"[cyan]Repository:[/cyan] {project.get('repository_url', 'N/A')}")
            console.print(f"[cyan]Active:[/cyan] {project['is_active']}")
            console.print(f"[cyan]Created:[/cyan] {project['created_at']}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()

@projects.command('delete')
@click.argument('project_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this project?')
@click.pass_context
def delete_project(ctx, project_id):
    """Delete a project"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        
        with console.status("[bold red]Deleting project..."):
            api_client.delete(f'/projects/{project_id}')
        
        console.print(f"[green]✓[/green] Project deleted successfully")
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
```

### Step 5: Implement API Gateway Commands

```python
# devguard/commands/api_gateway.py
import click
from rich.console import Console
from ..services.api_client import APIClient
from ..utils.formatters import OutputFormatter

console = Console()

@click.group()
def api():
    """API Gateway commands"""
    pass

@api.group()
def providers():
    """Manage API providers"""
    pass

@providers.command('list')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
def list_providers(ctx, format):
    """List all API providers"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        formatter = OutputFormatter(format)
        
        response = api_client.get('/api-gateway/providers')
        providers_data = response['data']['providers']
        
        if format == 'json':
            console.print(formatter.format(providers_data))
        else:
            columns = ['id', 'name', 'provider_type', 'is_active', 'priority_order']
            formatter.format(providers_data, columns)
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()

@api.group()
def analytics():
    """View API analytics"""
    pass

@analytics.command('cost')
@click.option('--project-id', type=int, help='Filter by project')
@click.option('--days', type=int, default=30, help='Number of days to analyze')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
def cost_analytics(ctx, project_id, days, format):
    """Get cost analytics"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        formatter = OutputFormatter(format)
        
        params = {'days': days}
        if project_id:
            params['project_id'] = project_id
        
        response = api_client.get('/api-gateway/analytics/cost', params=params)
        data = response['data']
        
        if format == 'json':
            console.print(formatter.format(data))
        else:
            summary = data['summary']
            console.print(f"[cyan]Total Cost:[/cyan] ${summary['total_cost']:.2f}")
            console.print(f"[cyan]Total Requests:[/cyan] {summary['total_requests']:,}")
            console.print(f"[cyan]Avg Cost/Request:[/cyan] ${summary['average_cost_per_request']:.4f}")
            console.print(f"[cyan]Period:[/cyan] {summary['period_days']} days")
            
            console.print("\n[bold]Daily Breakdown:[/bold]")
            columns = ['date', 'total_cost', 'request_count']
            formatter.format(data['daily_analytics'], columns)
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()

@analytics.command('latency')
@click.option('--project-id', type=int, help='Filter by project')
@click.option('--days', type=int, default=7, help='Number of days to analyze')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_context
def latency_analytics(ctx, project_id, days, format):
    """Get latency analytics"""
    try:
        config = ctx.obj['config']
        api_client = APIClient(config)
        formatter = OutputFormatter(format)
        
        params = {'days': days}
        if project_id:
            params['project_id'] = project_id
        
        response = api_client.get('/api-gateway/analytics/latency', params=params)
        data = response['data']['latency_by_provider']
        
        if format == 'json':
            console.print(formatter.format(data))
        else:
            columns = ['provider', 'avg_latency_ms', 'min_latency_ms', 'max_latency_ms', 'request_count']
            formatter.format(data, columns)
        
    except Exception as e:
        console.print(f"[red]✗[/red] {str(e)}")
        raise click.Abort()
```

### Step 6: Create Setup File

```python
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="devguard-cli",
    version="1.0.0",
    author="DevGuard Team",
    author_email="support@devguard.io",
    description="Command-line interface for DevGuard DevOps Intelligence Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devguard/devguard-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.7",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "keyring>=24.3.0",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "devguard=devguard.cli:cli",
        ],
    },
)
```

---

## Command Reference

### Complete Command Structure

```
devguard
├── auth
│   ├── login              # Login to DevGuard
│   ├── logout             # Logout from DevGuard
│   ├── whoami             # Show current user
│   └── refresh            # Refresh authentication token
│
├── projects
│   ├── list               # List all projects
│   ├── create             # Create new project
│   ├── get <id>           # Get project details
│   ├── update <id>        # Update project
│   └── delete <id>        # Delete project
│
├── api
│   ├── providers
│   │   ├── list           # List API providers
│   │   ├── create         # Add new provider
│   │   └── delete <id>    # Remove provider
│   │
│   ├── requests
│   │   ├── list           # List API requests
│   │   └── log            # Log new request
│   │
│   ├── analytics
│   │   ├── cost           # Cost analytics
│   │   └── latency        # Latency analytics
│   │
│   └── budgets
│       ├── list           # List budgets
│       ├── create         # Create budget
│       └── delete <id>    # Delete budget
│
├── database
│   ├── connections
│   │   ├── list           # List database connections
│   │   ├── create         # Add connection
│   │   └── delete <id>    # Remove connection
│   │
│   ├── queries
│   │   ├── list           # List query patterns
│   │   └── slow           # Show slow queries
│   │
│   ├── optimizations
│   │   ├── list           # List optimizations
│   │   └── apply <id>     # Apply optimization
│   │
│   └── analytics
│       └── performance    # Performance analytics
│
├── deps
│   ├── scans
│   │   ├── list           # List scans
│   │   ├── create         # Create new scan
│   │   └── get <id>       # Get scan details
│   │
│   ├── vulnerabilities
│   │   └── list           # List vulnerabilities
│   │
│   └── analytics
│       └── risk           # Risk summary
│
└── insights
    ├── list               # List insights
    ├── acknowledge <id>   # Acknowledge insight
    └── resolve <id>       # Resolve insight
```

### Usage Examples

```bash
# Authentication
devguard auth login --email user@example.com
devguard auth whoami
devguard auth logout

# Projects
devguard projects list --format table
devguard projects create --name "My Project" --description "Description"
devguard projects get 1
devguard projects delete 1

# API Gateway
devguard api providers list
devguard api analytics cost --days 30 --format json
devguard api analytics latency --project-id 1

# Database Optimizer
devguard database queries slow --limit 10
devguard database optimizations list --min-improvement 50
devguard database optimizations apply 5

# Dependency Scanner
devguard deps scans create --project-id 1 --ecosystem npm
devguard deps vulnerabilities list --severity critical
devguard deps analytics risk

# Insights
devguard insights list --category cost --severity critical
devguard insights acknowledge 1
devguard insights resolve 1
```

---

## Best Practices

### 1. Error Handling

```python
# Always handle errors gracefully
try:
    response = api_client.get('/projects')
except AuthenticationError:
    console.print("[red]Authentication failed. Please login.[/red]")
    raise click.Abort()
except APIError as e:
    console.print(f"[red]API Error: {e.message}[/red]")
    if e.details:
        console.print(f"Details: {e.details}")
    raise click.Abort()
except Exception as e:
    console.print(f"[red]Unexpected error: {str(e)}[/red]")
    raise click.Abort()
```

### 2. Progress Indicators

```python
# Use spinners for long operations
with console.status("[bold green]Fetching data..."):
    response = api_client.get('/projects')

# Use progress bars for batch operations
from rich.progress import track

for item in track(items, description="Processing..."):
    process_item(item)
```

### 3. Input Validation

```python
# Validate inputs before making API calls
def validate_email(ctx, param, value):
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise click.BadParameter("Invalid email format")
    return value

@click.option('--email', callback=validate_email)
def command(email):
    pass
```

### 4. Configuration Management

```python
# Support multiple profiles
devguard config set-profile production
devguard config set-profile staging

# Allow environment variable overrides
export DEVGUARD_API_URL=https://custom.api.com
export DEVGUARD_TOKEN=your_token_here
```

### 5. Pagination

```python
# Implement pagination for large datasets
@click.option('--page', type=int, default=1)
@click.option('--per-page', type=int, default=20)
def list_command(page, per_page):
    params = {'page': page, 'per_page': per_page}
    response = api_client.get('/endpoint', params=params)
    
    # Show pagination info
    pagination = response['data']['pagination']
    console.print(f"Page {pagination['page']} of {pagination['pages']}")
```

### 6. Caching

```python
# Cache frequently accessed data
import functools
from datetime import datetime, timedelta

def cache_for(minutes=5):
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                result, timestamp = cache[key]
                if datetime.now() - timestamp < timedelta(minutes=minutes):
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, datetime.now())
            return result
        
        return wrapper
    return decorator

@cache_for(minutes=5)
def get_projects():
    return api_client.get('/projects')
```

---

## Testing

### Unit Tests

```python
# tests/test_auth.py
import pytest
from devguard.services.auth_service import AuthService
from devguard.utils.errors import AuthenticationError

def test_login_success(mock_api_client):
    auth_service = AuthService(mock_api_client)
    
    mock_api_client.post.return_value = {
        'data': {
            'token': 'test_token',
            'user': {'email': 'test@example.com'}
        }
    }
    
    result = auth_service.login('test@example.com', 'password')
    assert result['token'] == 'test_token'

def test_login_failure(mock_api_client):
    auth_service = AuthService(mock_api_client)
    
    mock_api_client.post.side_effect = AuthenticationError("Invalid credentials")
    
    with pytest.raises(AuthenticationError):
        auth_service.login('test@example.com', 'wrong_password')
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from click.testing import CliRunner
from devguard.cli import cli

def test_login_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['auth', 'login'], 
                          input='test@example.com\npassword\n')
    
    assert result.exit_code == 0
    assert 'Successfully logged in' in result.output

def test_list_projects():
    runner = CliRunner()
    result = runner.invoke(cli, ['projects', 'list'])
    
    assert result.exit_code == 0
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest

# Run with coverage
pytest --cov=devguard --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

---

## Distribution

### 1. PyPI Distribution

```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI
pip install twine
twine upload dist/*

# Install from PyPI
pip install devguard-cli
```

### 2. Homebrew (macOS/Linux)

```ruby
# devguard.rb
class Devguard < Formula
  desc "DevGuard CLI - DevOps Intelligence Platform"
  homepage "https://devguard.io"
  url "https://github.com/devguard/devguard-cli/archive/v1.0.0.tar.gz"
  sha256 "..."
  
  depends_on "python@3.11"
  
  def install
    virtualenv_install_with_resources
  end
  
  test do
    system "#{bin}/devguard", "--version"
  end
end
```

### 3. Standalone Executables

```bash
# Using PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --name devguard devguard/cli.py

# Executable will be in dist/devguard
```

### 4. Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

ENTRYPOINT ["devguard"]
```

```bash
# Build and run
docker build -t devguard-cli .
docker run -it devguard-cli auth login
```

---

## Additional Resources

### Documentation

- API Collection: `api_collection.json`
- API Examples: `API_EXAMPLES.md`
- Project Structure: `PROJECT_STRUCTURE.md`

### Libraries & Tools

- **Click**: https://click.palletsprojects.com/
- **Rich**: https://rich.readthedocs.io/
- **Requests**: https://requests.readthedocs.io/
- **Pydantic**: https://docs.pydantic.dev/

### Example CLIs for Reference

- **AWS CLI**: https://github.com/aws/aws-cli
- **Heroku CLI**: https://github.com/heroku/cli
- **GitHub CLI**: https://github.com/cli/cli
- **Stripe CLI**: https://github.com/stripe/stripe-cli

---

## Conclusion

This guide provides a comprehensive foundation for building a production-ready CLI for the DevGuard platform. The architecture is modular, extensible, and follows best practices for CLI development.

Key takeaways:
- Use a robust CLI framework (Click, Commander, Cobra)
- Implement proper authentication and token management
- Provide multiple output formats for flexibility
- Handle errors gracefully with helpful messages
- Include comprehensive tests
- Document all commands and options
- Support configuration profiles
- Implement caching for better performance

For questions or contributions, please refer to the main project repository.
