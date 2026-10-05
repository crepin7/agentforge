"""
AgentForge Python SDK.

Permet de publier et d'exécuter des agents sur la marketplace AgentForge.

Usage:
    from agentforge import Agent, Client

    client = Client(api_key="https://your-instance.com", token="...")

    # Lister les agents populaires
    popular = client.agents.list(sort="popular", category="news")

    # Exécuter un agent
    run = client.runs.create(agent_slug="weather-reporter", inputs={"city": "Lomé"})
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx


@dataclass
class AgentDefinition:
    name: str
    description: str
    category: str
    runtime_type: str
    runtime_config: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    price_cents: int = 0
    long_description: Optional[str] = None
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "long_description": self.long_description,
            "category": self.category,
            "tags": self.tags,
            "price_cents": self.price_cents,
            "runtime_type": self.runtime_type,
            "runtime_config": self.runtime_config,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }


class AgentForgeError(Exception):
    pass


class _AgentsAPI:
    def __init__(self, client: "Client") -> None:
        self._c = client

    def create(self, definition: AgentDefinition) -> Dict[str, Any]:
        return self._c._post("/agents/", definition.to_payload())

    def list(self, category: Optional[str] = None, search: Optional[str] = None, sort: str = "popular",
             limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"sort": sort, "limit": limit, "offset": offset}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        return self._c._get("/agents/", params=params)

    def get(self, slug: str) -> Dict[str, Any]:
        return self._c._get(f"/agents/{slug}")

    def publish(self, slug: str) -> Dict[str, Any]:
        return self._c._patch(f"/agents/{slug}", {"is_published": True})


class _RunsAPI:
    def __init__(self, client: "Client") -> None:
        self._c = client

    def create(self, agent_slug: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._c._post(f"/runs/{agent_slug}", {"input_data": input_data})

    def get(self, run_id: str) -> Dict[str, Any]:
        return self._c._get(f"/runs/{run_id}")


class Client:
    """Client principal pour interagir avec l'API AgentForge."""

    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None,
                 timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._timeout = timeout
        self.agents = _AgentsAPI(self)
        self.runs = _RunsAPI(self)

    def _request(self, method: str, path: str, json_body: Optional[Dict[str, Any]] = None,
                 params: Optional[Dict[str, Any]] = None) -> Any:
        headers: Dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            with httpx.Client(base_url=self.base_url, timeout=self._timeout) as http:
                resp = http.request(method, path, json=json_body, params=params, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as e:
            raise AgentForgeError(f"HTTP {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            raise AgentForgeError(f"Request failed: {e}") from e

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    def _post(self, path: str, body: Dict[str, Any]) -> Any:
        return self._request("POST", path, json_body=body)

    def _patch(self, path: str, body: Dict[str, Any]) -> Any:
        return self._request("PATCH", path, json_body=body)


__all__ = ["Client", "AgentDefinition", "AgentForgeError"]