"""
Workers Celery pour l'exécution asynchrone longue des agents.
"""

import asyncio

from celery import shared_task

from app.db import async_session_factory
from app.models import Agent, Run
from app.services.sandbox import sandbox


@shared_task(name="agentforge.execute_run")
def execute_run_task(run_id: str) -> dict:
    return asyncio.run(_execute_run(run_id))


async def _execute_run(run_id: str) -> dict:
    async with async_session_factory() as session:
        run = await session.get(Run, run_id)
        if not run:
            return {"error": "Run not found"}
        agent = await session.get(Agent, run.agent_id)
        if not agent:
            return {"error": "Agent not found"}

        run.status = "running"
        await session.commit()

        result = await sandbox.execute(agent.runtime_type, agent.runtime_config or {}, run.input_data or {})

        run.output_data = result.output if result.success else None
        run.error_message = result.error if not result.success else None
        run.duration_ms = result.duration_ms
        run.cost_cents = result.cost_cents
        run.status = "completed" if result.success else "failed"

        if result.success:
            agent.total_runs = (agent.total_runs or 0) + 1

        await session.commit()
        return {"run_id": run_id, "status": run.status, "duration_ms": result.duration_ms}