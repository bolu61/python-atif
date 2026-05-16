from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Agent(BaseModel):
    """Agent system that produced the trajectory (ATIF `AgentSchema`)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str = Field(..., description="Name of the agent system, e.g. 'openhands'.")
    version: str = Field(..., description="Version identifier of the agent system.")
    model_name: str | None = Field(
        default=None,
        description="Default LLM model for this trajectory; step-level model_name overrides.",
    )
    tool_definitions: list[dict[str, Any]] | None = Field(
        default=None,
        description="OpenAI-style function/tool definitions available to the agent.",
    )
    extra: dict[str, Any] | None = Field(
        default=None,
        description="Custom agent configuration not covered by the core schema.",
    )
