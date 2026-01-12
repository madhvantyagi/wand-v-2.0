"""
SQLAlchemy database models.
Supports both SQLite (JSON) and PostgreSQL (JSONB).
"""

import os
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

try:
    from .database import Base
except ImportError:
    from database import Base

# Use JSONB for PostgreSQL, JSON for SQLite
_db_url = os.getenv("DATABASE_URL", "")
JsonColumn = JSONB if _db_url.startswith("postgresql") else JSON


def get_uuid():
    return str(uuid.uuid4())


class User(Base):
    """User account."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for migration
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profiles = relationship("Profile", back_populates="user")
    jobs = relationship("Job", back_populates="user")
    gap_analyses = relationship("GapAnalysis", back_populates="user")
    cover_letters = relationship("CoverLetter", back_populates="user")
    applications = relationship("Application", back_populates="user")
    resume_optimizations = relationship("ResumeOptimization", back_populates="user")
    discrepancy_reports = relationship("DiscrepancyReport", back_populates="user")


class Profile(Base):
    """Parsed user profile (resume, LinkedIn, portfolio)."""
    __tablename__ = "profiles"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    source_type = Column(String(50))  # 'resume', 'linkedin', 'portfolio'
    file_name = Column(String(255))
    file_content = Column(LargeBinary)  # Raw file bytes for preview
    parsed_data = Column(JsonColumn)  # JSONB for PostgreSQL, JSON for SQLite
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="profiles")


class Job(Base):
    """Analyzed job posting."""
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    job_title = Column(String(255))
    company_name = Column(String(255))
    job_text = Column(Text)
    parsed_data = Column(JsonColumn)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="jobs")
    gap_analyses = relationship("GapAnalysis", back_populates="job", cascade="all, delete-orphan")
    cover_letters = relationship("CoverLetter", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    resume_optimizations = relationship("ResumeOptimization", back_populates="job", cascade="all, delete-orphan")


class Company(Base):
    """Cached company intelligence."""
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    name = Column(String(255), unique=True)
    website = Column(String(255))
    intelligence = Column(JsonColumn)  # jobs + website + news data
    updated_at = Column(DateTime, default=datetime.utcnow)


class GapAnalysis(Base):
    """Gap analysis between profile(s) and job."""
    __tablename__ = "gap_analyses"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    profile_ids = Column(JsonColumn)  # List of profile IDs used
    match_score = Column(Integer)
    analysis_data = Column(JsonColumn)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="gap_analyses")
    job = relationship("Job", back_populates="gap_analyses")


class CoverLetter(Base):
    """Generated cover letter."""
    __tablename__ = "cover_letters"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    gap_analysis_id = Column(String(36), ForeignKey("gap_analyses.id"))
    style = Column(String(50))  # 'professional', 'enthusiastic', 'concise'
    letter = Column(Text)
    letter_metadata = Column(JsonColumn)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="cover_letters")
    job = relationship("Job", back_populates="cover_letters")


class Application(Base):
    """Job application tracking."""
    __tablename__ = "applications"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    cover_letter_id = Column(String(36), ForeignKey("cover_letters.id"))
    status = Column(String(50), default="saved")  # saved, applied, interviewing, rejected, offer
    notes = Column(Text)
    applied_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class ResumeOptimization(Base):
    """Resume optimization suggestions."""
    __tablename__ = "resume_optimizations"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(String(36), ForeignKey("profiles.id"), nullable=False)
    optimization_data = Column(JsonColumn)  # List of optimizations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="resume_optimizations")
    job = relationship("Job", back_populates="resume_optimizations")
    resume = relationship("Profile")


class DiscrepancyReport(Base):
    """Saved discrepancy analysis reports."""
    __tablename__ = "discrepancy_reports"
    
    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    profile_ids = Column(JsonColumn)  # List of profile IDs compared
    consistency_score = Column(Integer)
    report_data = Column(JsonColumn)  # Full analysis result
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="discrepancy_reports")
