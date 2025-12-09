"""Models package initialization."""
# Import all models to ensure they are registered with SQLAlchemy
from app.models.core import Organization, User, Project, UserRole, SubscriptionTier
from app.models.api_gateway import (
    APIProvider,
    APIConfiguration,
    APIRequest,
    APIBudget,
    APIAlert,
    ProviderType,
    RoutingStrategy,
    AlertType,
)
from app.models.database_optimizer import (
    DatabaseConnection,
    QueryPattern,
    QueryOptimization,
    DatabaseMetric,
    DatabaseIndex,
    DatabaseType,
    OptimizationType,
)
from app.models.dependency_scanner import (
    DependencyScan,
    Dependency,
    Vulnerability,
    MaintenanceMetric,
    DependencyAlternative,
    DependencyUpdate,
    ScanTrigger,
    Ecosystem,
    VulnerabilitySeverity,
    UpdatePriority,
    MigrationDifficulty,
)
from app.models.shared import (
    Insight,
    AuditLog,
    Notification,
    IntegrationWebhook,
    InsightCategory,
    Severity,
)

__all__ = [
    # Core
    "Organization",
    "User",
    "Project",
    "UserRole",
    "SubscriptionTier",
    # API Gateway
    "APIProvider",
    "APIConfiguration",
    "APIRequest",
    "APIBudget",
    "APIAlert",
    "ProviderType",
    "RoutingStrategy",
    "AlertType",
    # Database Optimizer
    "DatabaseConnection",
    "QueryPattern",
    "QueryOptimization",
    "DatabaseMetric",
    "DatabaseIndex",
    "DatabaseType",
    "OptimizationType",
    # Dependency Scanner
    "DependencyScan",
    "Dependency",
    "Vulnerability",
    "MaintenanceMetric",
    "DependencyAlternative",
    "DependencyUpdate",
    "ScanTrigger",
    "Ecosystem",
    "VulnerabilitySeverity",
    "UpdatePriority",
    "MigrationDifficulty",
    # Shared
    "Insight",
    "AuditLog",
    "Notification",
    "IntegrationWebhook",
    "InsightCategory",
    "Severity",
]
