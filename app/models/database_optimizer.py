"""Database Optimizer component models."""
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
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.extensions import db


class DatabaseType(enum.Enum):
    """Database type enumeration."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    MARIADB = "mariadb"


class OptimizationType(enum.Enum):
    """Optimization type enumeration."""

    INDEX = "index"
    QUERY_REWRITE = "query_rewrite"
    SCHEMA_CHANGE = "schema_change"
    CACHING = "caching"
    PARTITIONING = "partitioning"


class DatabaseConnection(db.Model):
    """Database Connection model."""

    __tablename__ = "database_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    database_type: Mapped[DatabaseType] = mapped_column(
        SQLEnum(DatabaseType), nullable=False
    )
    connection_string_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", back_populates="database_connections"
    )
    query_patterns: Mapped[list["QueryPattern"]] = relationship(
        "QueryPattern", back_populates="connection", cascade="all, delete-orphan"
    )
    database_metrics: Mapped[list["DatabaseMetric"]] = relationship(
        "DatabaseMetric", back_populates="connection", cascade="all, delete-orphan"
    )
    indexes: Mapped[list["DatabaseIndex"]] = relationship(
        "DatabaseIndex", back_populates="connection", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_db_connections_project", "project_id", "is_active"),
    )

    def __repr__(self):
        return f"<DatabaseConnection {self.name} ({self.database_type.value})>"


class QueryPattern(db.Model):
    """Query Pattern model - TimescaleDB hypertable."""

    __tablename__ = "query_patterns"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    connection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("database_connections.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    query_fingerprint: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    query_structure: Mapped[str] = mapped_column(Text, nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    rows_examined: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_returned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    index_usage: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    explain_plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    frequency_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    connection: Mapped["DatabaseConnection"] = relationship(
        "DatabaseConnection", back_populates="query_patterns"
    )
    optimizations: Mapped[list["QueryOptimization"]] = relationship(
        "QueryOptimization", back_populates="pattern", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_query_patterns_timestamp", "timestamp"),
        Index("idx_query_patterns_connection_timestamp", "connection_id", "timestamp"),
        Index("idx_query_patterns_fingerprint", "query_fingerprint"),
    )

    def __repr__(self):
        return f"<QueryPattern {self.query_fingerprint[:8]}... {self.execution_time_ms}ms>"


class QueryOptimization(db.Model):
    """Query Optimization model."""

    __tablename__ = "query_optimizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pattern_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("query_patterns.id"), nullable=False
    )
    optimization_type: Mapped[OptimizationType] = mapped_column(
        SQLEnum(OptimizationType), nullable=False
    )
    current_performance_score: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_improvement_pct: Mapped[float] = mapped_column(Float, nullable=False)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    migration_script: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    complexity_score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_improvement_pct: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    pattern: Mapped["QueryPattern"] = relationship(
        "QueryPattern", back_populates="optimizations"
    )

    __table_args__ = (
        Index("idx_query_optimizations_pattern", "pattern_id", "is_applied"),
    )

    def __repr__(self):
        return f"<QueryOptimization {self.optimization_type.value} +{self.estimated_improvement_pct}%>"


class DatabaseMetric(db.Model):
    """Database Metric model - TimescaleDB hypertable."""

    __tablename__ = "database_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    connection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("database_connections.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    cpu_usage_pct: Mapped[float] = mapped_column(Float, nullable=False)
    memory_usage_pct: Mapped[float] = mapped_column(Float, nullable=False)
    connection_count: Mapped[int] = mapped_column(Integer, nullable=False)
    slow_query_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cache_hit_rate: Mapped[float] = mapped_column(Float, nullable=False)
    disk_io_ops: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    connection: Mapped["DatabaseConnection"] = relationship(
        "DatabaseConnection", back_populates="database_metrics"
    )

    __table_args__ = (
        Index("idx_db_metrics_timestamp", "timestamp"),
        Index("idx_db_metrics_connection_timestamp", "connection_id", "timestamp"),
    )

    def __repr__(self):
        return f"<DatabaseMetric CPU:{self.cpu_usage_pct}% MEM:{self.memory_usage_pct}%>"


class DatabaseIndex(db.Model):
    """Database Index model."""

    __tablename__ = "database_indexes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    connection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("database_connections.id"), nullable=False
    )
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    index_name: Mapped[str] = mapped_column(String(255), nullable=False)
    columns: Mapped[dict] = mapped_column(JSON, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    recommendation_source: Mapped[str] = mapped_column(
        String(50), default="manual", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    connection: Mapped["DatabaseConnection"] = relationship(
        "DatabaseConnection", back_populates="indexes"
    )

    __table_args__ = (
        Index("idx_db_indexes_connection", "connection_id"),
        Index("idx_db_indexes_table", "table_name"),
    )

    def __repr__(self):
        return f"<DatabaseIndex {self.table_name}.{self.index_name}>"
