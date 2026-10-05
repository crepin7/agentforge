"""
Routes d'exécution d'agents.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_factory, get_session
from app.models import Agent, Run, User
from app.schemas import RunCreate, RunPublic
from app.services.billing import calculate_marketplace_split, create_checkout_session
from app.services.sandbox import sandbox

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/{agent_slug}", response_model=RunPublic, status_code=201)
async def create_run(
    agent_slug: str,
    payload: RunCreate,
    current_user_id: str,
    session: AsyncSession = Depends(get_session),
) -> RunPublic:
    user = await session.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await session.execute(select(Agent).where(Agent.slug == agent_slug))
    agent = result.scalar_one_or_none()
    if not agent or not agent.is_published:
        raise HTTPException(status_code=404, detail="Agent not found")

    run = Run(
        user_id=user.id,
        agent_id=agent.id,
        input_data=payload.input_data,
        status="pending",
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)

    if agent.price_cents and agent.price_cents > 0:
        checkout = await create_checkout_session(
            amount_cents=agent.price_cents,
            currency="usd",
            success_url=f"/runs/{run.id}/success",
            cancel_url=f"/runs/{run.id}/cancel",
            customer_email=user.email,
            metadata={"run_id": run.id, "agent_id": agent.id},
        )
        return RunPublic.model_validate({
            **run.__dict__,
            "output_data": {"checkout_url": checkout["checkout_url"]},
        })

    result = await sandbox.execute(agent.runtime_type, agent.runtime_config or {}, run.input_data or {})
    run.output_data = result.output if result.success else None
    run.error_message = result.error if not result.success else None
    run.duration_ms = result.duration_ms
    run.cost_cents = result.cost_cents
    run.status = "completed" if result.success else "failed"
    await session.commit()
    await session.refresh(run)
    return RunPublic.model_validate(run)


@router.get("/{run_id}", response_model=RunPublic)
async def get_run(run_id: str, current_user_id: str, session: AsyncSession = Depends(get_session)) -> RunPublic:
    run = await session.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return RunPublic.model_validate(run)


@router.get("/_stats/marketplace", response_model=dict)
async def marketplace_stats(agent_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    agent = await session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "agent_id": agent_id,
        "total_runs": agent.total_runs or 0,
        "estimated_revenue_cents": (agent.total_runs or 0) * agent.price_cents,
        "platform_fee_split": calculate_marketplace_split(agent.price_cents or 100),
    }