"""API Gateway component models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    DateTime,
    Boolean,
    Integer,
    Float,
    JSON,
    Enum as SQLEnum,
    Index,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.extensions import db


class ProviderType(enum.Enum):
    """API Provider type enumeration."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AWS_BEDROCK = "aws_bedrock"
    GOOGLE_VERTEX = "google_vertex"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"


class RoutingStrategy(enum.Enum):
    """Routing strategy enumeration."""

    COST = "cost"
    LATENCY = "latency"
    QUALITY = "quality"
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"


class AlertType(enum.Enum):
    """Alert type enumeration."""

    BUDGET = "budget"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    RATE_LIMIT = "rate_limit"


class Severity(enum.Enum):
    """Severity enumeration."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class APIProvider(db.Model):
    """API Provider model."""

    __tablename__ = "api_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id"), nullable=False
    )
    provider_type: Mapped[ProviderType] = mapped_column(
        SQLEnum(ProviderType), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    credentials_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="api_providers"
    )
    configurations: Mapped[list["APIConfiguration"]] = relationship(
        "APIConfiguration", back_populates="provider", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_api_providers_org_active", "organization_id", "is_active"),
    )

    def __repr__(self):
        return f"<APIProvider {self.name} ({self.provider_type.value})>"


class APIConfiguration(db.Model):
    """API Configuration model."""

    __tablename__ = "api_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    provider_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_providers.id"), nullable=False
    )
    endpoint_pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    rate_limit_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    budget_limits: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    routing_strategy: Mapped[RoutingStrategy] = mapped_column(
        SQLEnum(RoutingStrategy), default=RoutingStrategy.COST, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", back_populates="api_configurations"
    )
    provider: Mapped["APIProvider"] = relationship(
        "APIProvider", back_populates="configurations"
    )

    __table_args__ = (Index("idx_api_configs_project", "project_id", "is_active"),)

    def __repr__(self):
        return f"<APIConfiguration {self.endpoint_pattern}>"


class APIRequest(db.Model):
    """API Request model - TimescaleDB hypertable."""

    __tablename__ = "api_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    provider_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_providers.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tokens_used: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    user_identifier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    environment: Mapped[str] = mapped_column(
        String(50), default="production", nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_api_requests_timestamp", "timestamp"),
        Index("idx_api_requests_project_timestamp", "project_id", "timestamp"),
        Index("idx_api_requests_provider_timestamp", "provider_id", "timestamp"),
    )

    def __repr__(self):
        return f"<APIRequest {self.method} {self.endpoint} at {self.timestamp}>"


class APIBudget(db.Model):
    """API Budget model."""

    __tablename__ = "api_budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    allocated_amount_usd: Mapped[float] = mapped_column(Float, nullable=False)
    spent_amount_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    alert_thresholds: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    actions_on_exceed: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="api_budgets")

    __table_args__ = (
        Index("idx_api_budgets_project_period", "project_id", "period_start"),
    )

    def __repr__(self):
        return f"<APIBudget {self.project_id} ${self.allocated_amount_usd}>"


class APIAlert(db.Model):
    """API Alert model."""

    __tablename__ = "api_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    alert_type: Mapped[AlertType] = mapped_column(SQLEnum(AlertType), nullable=False)
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="api_alerts")

    __table_args__ = (
        Index("idx_api_alerts_project_triggered", "project_id", "triggered_at"),
        Index("idx_api_alerts_resolved", "resolved_at"),
    )

    def __repr__(self):
        return f"<APIAlert {self.alert_type.value} - {self.severity.value}>"
