import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticker = Column(String(10), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False, default="quarterly_outlook")
    status = Column(String(30), nullable=False, default="pending", index=True)  # pending, running, completed, degraded, failed
    requested_by = Column(String(100), default="system")
    degraded_sources = Column(JSON, default=list)  # list of degraded source names
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    agent_runs = relationship("AgentRun", back_populates="job", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="job", uselist=False, cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="job", cascade="all, delete-orphan")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    agent_version = Column(String(20), nullable=False, default="1.0.0")
    status = Column(String(30), nullable=False, default="running")  # success, degraded, failed
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    input_hash = Column(String(64), nullable=True)
    output_ref = Column(String(255), nullable=True)

    job = relationship("AnalysisJob", back_populates="agent_runs")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    executive_summary = Column(Text, nullable=False)
    bull_case = Column(Text, nullable=False)
    bear_case = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    payload = Column(JSON, nullable=False)  # full ReportSchema serialized JSON
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    job = relationship("AnalysisJob", back_populates="report")


class MarketDataModel(Base):
    __tablename__ = "market_data"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticker = Column(String(10), nullable=False, index=True)
    as_of = Column(DateTime(timezone=True), nullable=False)
    payload = Column(JSON, nullable=False)  # MarketDataSchema
    source = Column(String(50), nullable=False, default="yfinance")
    version = Column(String(20), nullable=False, default="1.0.0")
    confidence = Column(Float, nullable=False, default=1.0)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class FinancialDataModel(Base):
    __tablename__ = "financial_data"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticker = Column(String(10), nullable=False, index=True)
    period = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)  # FinancialSchema
    source = Column(String(50), nullable=False, default="sec_edgar")
    version = Column(String(20), nullable=False, default="1.0.0")
    confidence = Column(Float, nullable=False, default=1.0)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class NewsDataModel(Base):
    __tablename__ = "news_data"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticker = Column(String(10), nullable=False, index=True)
    payload = Column(JSON, nullable=False)  # NewsSummarySchema
    source = Column(String(50), nullable=False, default="news_aggregator")
    version = Column(String(20), nullable=False, default="1.0.0")
    confidence = Column(Float, nullable=False, default=1.0)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class SentimentDataModel(Base):
    __tablename__ = "sentiment_data"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticker = Column(String(10), nullable=False, index=True)
    payload = Column(JSON, nullable=False)  # SentimentSchema
    source = Column(String(50), nullable=False, default="social_aggregator")
    version = Column(String(20), nullable=False, default="1.0.0")
    confidence = Column(Float, nullable=False, default=1.0)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class SectorDataModel(Base):
    __tablename__ = "sector_data"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticker = Column(String(10), nullable=False, index=True)
    payload = Column(JSON, nullable=False)  # SectorSchema
    source = Column(String(50), nullable=False, default="sector_peers")
    version = Column(String(20), nullable=False, default="1.0.0")
    confidence = Column(Float, nullable=False, default=1.0)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    horizon = Column(String(10), nullable=False)  # 3m, 6m, 1y
    bull_prob = Column(Float, nullable=False)
    bear_prob = Column(Float, nullable=False)
    neutral_prob = Column(Float, nullable=False)
    expected_vol = Column(Float, nullable=False)
    price_range_low = Column(Float, nullable=False)
    price_range_high = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    source = Column(String(50), nullable=False, default="forecast_agent")
    version = Column(String(20), nullable=False, default="1.0.0")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    job = relationship("AnalysisJob", back_populates="forecasts")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor = Column(String(100), nullable=False, default="system")
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False, index=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
