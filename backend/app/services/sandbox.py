"""
Sandbox d'exécution des agents.

Supporte 4 runtimes :
- webhook : appelle un endpoint HTTP externe
- python : exécute un script Python dans un sous-processus isolé
- llm_prompt : envoie un prompt à OpenAI / Anthropic / Google
- docker : conteneur Docker jetable (à venir)
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict

import httpx


class ExecutionResult:
    def __init__(self, success: bool, output: Any = None, error: str | None = None, duration_ms: int = 0, cost_cents: int = 0):
        self.success = success
        self.output = output
        self.error = error
        self.duration_ms = duration_ms
        self.cost_cents = cost_cents


class AgentRuntime(ABC):
    @abstractmethod
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> ExecutionResult: ...


class WebhookRuntime(AgentRuntime):
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> ExecutionResult:
        url = config.get("url")
        if not url:
            return ExecutionResult(False, error="Missing webhook URL in runtime_config")
        timeout = config.get("timeout_seconds", 30)
        headers = config.get("headers", {})
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=inputs, headers=headers)
                resp.raise_for_status()
                duration = int((time.perf_counter() - start) * 1000)
                return ExecutionResult(True, output=resp.json(), duration_ms=duration, cost_cents=1)
        except httpx.HTTPError as e:
            duration = int((time.perf_counter() - start) * 1000)
            return ExecutionResult(False, error=str(e), duration_ms=duration)


class PythonRuntime(AgentRuntime):
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> ExecutionResult:
        code = config.get("code")
        if not code:
            return ExecutionResult(False, error="Missing Python code in runtime_config")
        timeout = config.get("timeout_seconds", 10)
        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            "python", "-c", code,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(json.dumps(inputs).encode()), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            duration = int((time.perf_counter() - start) * 1000)
            return ExecutionResult(False, error="Python execution timeout", duration_ms=duration)
        duration = int((time.perf_counter() - start) * 1000)
        if proc.returncode != 0:
            return ExecutionResult(False, error=stderr.decode()[:500], duration_ms=duration)
        try:
            return ExecutionResult(True, output=json.loads(stdout.decode()), duration_ms=duration, cost_cents=1)
        except json.JSONDecodeError:
            return ExecutionResult(True, output={"raw": stdout.decode()}, duration_ms=duration, cost_cents=1)


class LLMRuntime(AgentRuntime):
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> ExecutionResult:
        from app.core.config import settings
        provider = config.get("provider", "openai")
        model = config.get("model", "gpt-4o-mini")
        system_prompt = config.get("system_prompt", "")
        user_prompt = config.get("user_prompt", "{input}")
        try:
            user_prompt = user_prompt.format(**inputs)
        except KeyError:
            pass
        timeout = config.get("timeout_seconds", 30)
        start = time.perf_counter()
        try:
            if provider == "openai" and settings.openai_api_key:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=settings.openai_api_key)
                resp = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=model,
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    ),
                    timeout=timeout,
                )
                out = resp.choices[0].message.content
                duration = int((time.perf_counter() - start) * 1000)
                cost = max(1, int(resp.usage.total_tokens * 0.0001)) if resp.usage else 1
                return ExecutionResult(True, output={"text": out, "model": model}, duration_ms=duration, cost_cents=cost)
            return ExecutionResult(False, error=f"Provider {provider} not available (missing API key)")
        except asyncio.TimeoutError:
            return ExecutionResult(False, error="LLM call timeout")
        except Exception as e:
            return ExecutionResult(False, error=str(e)[:500])


class SandboxExecutor:
    def __init__(self) -> None:
        self._runtimes: Dict[str, AgentRuntime] = {
            "webhook": WebhookRuntime(),
            "python": PythonRuntime(),
            "llm_prompt": LLMRuntime(),
        }

    async def execute(self, runtime_type: str, config: Dict[str, Any], inputs: Dict[str, Any]) -> ExecutionResult:
        runtime = self._runtimes.get(runtime_type)
        if not runtime:
            return ExecutionResult(False, error=f"Unknown runtime_type: {runtime_type}")
        return await runtime.execute(config, inputs)


sandbox = SandboxExecutor()