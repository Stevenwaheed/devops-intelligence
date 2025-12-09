"""Shared models for cross-cutting concerns."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    DateTime,
    Boolean,
    Integer,
    JSON,
    Enum as SQLEnum,
    Index,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.extensions import db


class InsightCategory(enum.Enum):
    """Insight category enumeration."""

    COST = "cost"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTENANCE = "maintenance"


class Severity(enum.Enum):
    """Severity enumeration."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Insight(db.Model):
    """AI-Generated Insight model."""

    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    category: Mapped[InsightCategory] = mapped_column(
        SQLEnum(InsightCategory), nullable=False
    )
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recommended_actions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    estimated_impact: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="insights")

    __table_args__ = (
        Index("idx_insights_project_created", "project_id", "created_at"),
        Index("idx_insights_category_severity", "category", "severity"),
    )

    def __repr__(self):
        return f"<Insight {self.category.value} - {self.title[:30]}>"


class AuditLog(db.Model):
    """Audit Log model."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id"), nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="audit_logs"
    )
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_logs_org_timestamp", "organization_id", "timestamp"),
        Index("idx_audit_logs_user", "user_id"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action_type} on {self.resource_type}>"


class Notification(db.Model):
    """Notification model."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    notification_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_entity: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("idx_notifications_user_created", "user_id", "created_at"),
        Index("idx_notifications_is_read", "is_read"),
    )

    def __repr__(self):
        return f"<Notification {self.title[:30]}>"


class IntegrationWebhook(db.Model):
    """Integration Webhook model."""

    __tablename__ = "integration_webhooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    webhook_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    event_types: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    secret_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="webhooks")

    __table_args__ = (Index("idx_webhooks_project", "project_id", "is_active"),)

    def __repr__(self):
        return f"<IntegrationWebhook {self.webhook_url[:50]}>"
