"""
Schémas Pydantic — DTOs de l'API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    tier: str
    is_verified: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class AgentBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=128)
    description: str = Field(..., min_length=10, max_length=500)
    long_description: Optional[str] = None
    category: str
    tags: List[str] = []
    price_cents: int = Field(default=0, ge=0)


class AgentCreate(AgentBase):
    runtime_type: str = Field(..., pattern=r"^(webhook|python|llm_prompt|docker)$")
    runtime_config: Dict[str, Any] = {}
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}


class AgentUpdate(BaseModel):
    description: Optional[str] = None
    long_description: Optional[str] = None
    tags: Optional[List[str]] = None
    price_cents: Optional[int] = Field(default=None, ge=0)
    is_published: Optional[bool] = None


class AgentPublic(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    author_id: str
    is_premium: bool
    total_runs: int
    avg_rating: float
    rating_count: int
    is_published: bool
    created_at: datetime
    updated_at: datetime


class RunCreate(BaseModel):
    input_data: Dict[str, Any] = {}


class RunPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    agent_id: str
    user_id: str
    status: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    cost_cents: int
    created_at: datetime


class CheckoutSessionRequest(BaseModel):
    agent_id: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class PlatformStats(BaseModel):
    total_agents: int
    total_runs: int
    total_users: int
    total_revenue_cents: int


Token.model_rebuild()