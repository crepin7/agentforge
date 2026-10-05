"""
Routes agents — CRUD, publication, recherche.
"""

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Agent, User
from app.schemas import AgentCreate, AgentPublic, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:96]


@router.post("/", response_model=AgentPublic, status_code=201)
async def create_agent(
    payload: AgentCreate,
    current_user_id: str,
    session: AsyncSession = Depends(get_session),
) -> AgentPublic:
    user = await session.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    slug = _slugify(payload.name)
    existing = await session.execute(select(Agent).where(Agent.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Agent name already exists")

    agent = Agent(
        name=payload.name,
        slug=slug,
        description=payload.description,
        long_description=payload.long_description,
        category=payload.category,
        tags=payload.tags,
        price_cents=payload.price_cents,
        runtime_type=payload.runtime_type,
        runtime_config=payload.runtime_config,
        input_schema=payload.input_schema,
        output_schema=payload.output_schema,
        is_published=False,
        author_id=user.id,
    )
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return AgentPublic.model_validate(agent)


@router.get("/", response_model=list[AgentPublic])
async def list_agents(
    category: Optional[str] = None,
    search: Optional[str] = Query(None, max_length=128),
    sort: str = Query("popular", pattern=r"^(popular|newest|top_rated)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[AgentPublic]:
    stmt = select(Agent).where(Agent.is_published.is_(True))
    if category:
        stmt = stmt.where(Agent.category == category)
    if search:
        stmt = stmt.where(or_(Agent.name.ilike(f"%{search}%"), Agent.description.ilike(f"%{search}%")))

    if sort == "popular":
        stmt = stmt.order_by(Agent.total_runs.desc())
    elif sort == "newest":
        stmt = stmt.order_by(Agent.created_at.desc())
    elif sort == "top_rated":
        stmt = stmt.order_by(Agent.avg_rating.desc())

    stmt = stmt.limit(limit).offset(offset)
    result = await session.execute(stmt)
    agents = list(result.scalars().all())
    return [AgentPublic.model_validate(a) for a in agents]


@router.get("/{slug}", response_model=AgentPublic)
async def get_agent(slug: str, session: AsyncSession = Depends(get_session)) -> AgentPublic:
    result = await session.execute(select(Agent).where(Agent.slug == slug))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentPublic.model_validate(agent)


@router.patch("/{slug}", response_model=AgentPublic)
async def update_agent(
    slug: str,
    payload: AgentUpdate,
    current_user_id: str,
    session: AsyncSession = Depends(get_session),
) -> AgentPublic:
    result = await session.execute(select(Agent).where(Agent.slug == slug))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    await session.commit()
    await session.refresh(agent)
    return AgentPublic.model_validate(agent)


@router.delete("/{slug}", status_code=204)
async def delete_agent(
    slug: str,
    current_user_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    result = await session.execute(select(Agent).where(Agent.slug == slug))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await session.delete(agent)
    await session.commit()