"""
Modèles SQLAlchemy — schéma de la base de données.
"""

import uuid as _uuid_mod
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def gen_uuid() -> str:
    return str(_uuid_mod.uuid4())


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    bio = Column(Text, nullable=True)

    tier = Column(String(32), default="free", nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    stripe_customer_id = Column(String(128), nullable=True, unique=True)

    agents = relationship("Agent", back_populates="author", cascade="all, delete-orphan")
    runs = relationship("Run", back_populates="user", cascade="all, delete-orphan")


class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(128), unique=True, nullable=False, index=True)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    long_description = Column(Text, nullable=True)

    category = Column(String(64), nullable=False, index=True)
    tags = Column(JSON, default=list, nullable=False)

    runtime_type = Column(String(32), nullable=False)
    runtime_config = Column(JSON, default=dict, nullable=False)
    input_schema = Column(JSON, default=dict, nullable=False)
    output_schema = Column(JSON, default=dict, nullable=False)

    price_cents: int = Column(Integer, default=0, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)

    author_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    author = relationship("User", back_populates="agents")

    total_runs = Column(Integer, default=0, nullable=False)
    avg_rating = Column(Float, default=0.0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False, index=True)

    runs = relationship("Run", back_populates="agent", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_agents_category_published", "category", "is_published"),)


class Run(Base, TimestampMixin):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=False, index=True)

    input_data = Column(JSON, default=dict, nullable=False)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    status = Column(String(32), default="pending", nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)
    cost_cents = Column(Integer, default=0, nullable=False)

    stripe_payment_intent_id = Column(String(128), nullable=True)

    user = relationship("User", back_populates="runs")
    agent = relationship("Agent", back_populates="runs")

    __table_args__ = (Index("ix_runs_user_created", "user_id", "created_at"),)


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)