"""Dependency Scanner component models."""
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


class ScanTrigger(enum.Enum):
    """Scan trigger enumeration."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    GIT_HOOK = "git_hook"
    CI_CD = "ci_cd"


class Ecosystem(enum.Enum):
    """Package ecosystem enumeration."""

    NPM = "npm"
    PIP = "pip"
    MAVEN = "maven"
    GO = "go"
    RUBYGEMS = "rubygems"
    CARGO = "cargo"
    NUGET = "nuget"


class VulnerabilitySeverity(enum.Enum):
    """Vulnerability severity enumeration."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class UpdatePriority(enum.Enum):
    """Update priority enumeration."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MigrationDifficulty(enum.Enum):
    """Migration difficulty enumeration."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DependencyScan(db.Model):
    """Dependency Scan model."""

    __tablename__ = "dependency_scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    scan_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    scan_trigger: Mapped[ScanTrigger] = mapped_column(
        SQLEnum(ScanTrigger), nullable=False
    )
    ecosystem: Mapped[Ecosystem] = mapped_column(SQLEnum(Ecosystem), nullable=False)
    total_dependencies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_vulnerabilities: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    overall_risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    scan_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", back_populates="dependency_scans"
    )
    dependencies: Mapped[list["Dependency"]] = relationship(
        "Dependency", back_populates="scan", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_dependency_scans_project_timestamp", "project_id", "scan_timestamp"),
    )

    def __repr__(self):
        return f"<DependencyScan {self.ecosystem.value} - {self.scan_timestamp}>"


class Dependency(db.Model):
    """Dependency model."""

    __tablename__ = "dependencies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    scan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dependency_scans.id"), nullable=False
    )
    package_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    is_direct: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    parent_dependency_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("dependencies.id"), nullable=True
    )
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    last_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    scan: Mapped["DependencyScan"] = relationship(
        "DependencyScan", back_populates="dependencies"
    )
    vulnerabilities: Mapped[list["Vulnerability"]] = relationship(
        "Vulnerability", back_populates="dependency", cascade="all, delete-orphan"
    )
    maintenance_metrics: Mapped[list["MaintenanceMetric"]] = relationship(
        "MaintenanceMetric", back_populates="dependency", cascade="all, delete-orphan"
    )
    alternatives: Mapped[list["DependencyAlternative"]] = relationship(
        "DependencyAlternative",
        back_populates="dependency",
        cascade="all, delete-orphan",
    )
    updates: Mapped[list["DependencyUpdate"]] = relationship(
        "DependencyUpdate", back_populates="dependency", cascade="all, delete-orphan"
    )

    # Self-referential relationship for dependency tree
    children: Mapped[list["Dependency"]] = relationship(
        "Dependency", backref="parent", remote_side=[id]
    )

    __table_args__ = (
        Index("idx_dependencies_scan", "scan_id"),
        Index("idx_dependencies_package", "package_name", "version"),
    )

    def __repr__(self):
        return f"<Dependency {self.package_name}@{self.version}>"


class Vulnerability(db.Model):
    """Vulnerability model."""

    __tablename__ = "vulnerabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dependency_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dependencies.id"), nullable=False
    )
    cve_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[VulnerabilitySeverity] = mapped_column(
        SQLEnum(VulnerabilitySeverity), nullable=False
    )
    cvss_score: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    patched_versions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    exploit_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    dependency: Mapped["Dependency"] = relationship(
        "Dependency", back_populates="vulnerabilities"
    )

    __table_args__ = (
        Index("idx_vulnerabilities_dependency", "dependency_id"),
        Index("idx_vulnerabilities_cve", "cve_id"),
        Index("idx_vulnerabilities_severity", "severity"),
    )

    def __repr__(self):
        return f"<Vulnerability {self.cve_id} - {self.severity.value}>"


class MaintenanceMetric(db.Model):
    """Maintenance Metric model."""

    __tablename__ = "maintenance_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dependency_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dependencies.id"), nullable=False
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    commit_frequency_30d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contributor_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    issue_response_time_avg_hours: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    download_trend_30d: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_commit_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    bus_factor: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    abandonment_risk_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )

    # Relationships
    dependency: Mapped["Dependency"] = relationship(
        "Dependency", back_populates="maintenance_metrics"
    )

    __table_args__ = (
        Index("idx_maintenance_metrics_dependency", "dependency_id"),
        Index("idx_maintenance_metrics_risk", "abandonment_risk_score"),
    )

    def __repr__(self):
        return f"<MaintenanceMetric risk:{self.abandonment_risk_score}>"


class DependencyAlternative(db.Model):
    """Dependency Alternative model."""

    __tablename__ = "dependency_alternatives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dependency_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dependencies.id"), nullable=False
    )
    alternative_package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    migration_difficulty: Mapped[MigrationDifficulty] = mapped_column(
        SQLEnum(MigrationDifficulty), nullable=False
    )
    performance_comparison: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    license_compatibility: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    recommendation_reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    dependency: Mapped["Dependency"] = relationship(
        "Dependency", back_populates="alternatives"
    )

    __table_args__ = (Index("idx_dependency_alternatives_dependency", "dependency_id"),)

    def __repr__(self):
        return f"<DependencyAlternative {self.alternative_package_name}>"


class DependencyUpdate(db.Model):
    """Dependency Update model."""

    __tablename__ = "dependency_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dependency_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dependencies.id"), nullable=False
    )
    current_version: Mapped[str] = mapped_column(String(50), nullable=False)
    target_version: Mapped[str] = mapped_column(String(50), nullable=False)
    breaking_changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    update_priority: Mapped[UpdatePriority] = mapped_column(
        SQLEnum(UpdatePriority), nullable=False
    )
    auto_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    dependency: Mapped["Dependency"] = relationship(
        "Dependency", back_populates="updates"
    )

    __table_args__ = (
        Index("idx_dependency_updates_dependency", "dependency_id"),
        Index("idx_dependency_updates_priority", "update_priority"),
    )

    def __repr__(self):
        return f"<DependencyUpdate {self.current_version} → {self.target_version}>"
