from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolCall(BaseModel):
    """A single function/tool invocation in an agent step (ATIF `ToolCallSchema`)."""

    model_config = ConfigDict(extra="forbid")

    tool_call_id: str = Field(
        ...,
        description="Unique identifier; correlated with `ObservationResult.source_call_id`.",
    )
    function_name: str = Field(..., description="Name of the function/tool invoked.")
    arguments: dict[str, Any] = Field(
        ...,
        description="JSON object of arguments; MAY be empty (`{}`) when no args are needed.",
    )
    extra: dict[str, Any] | None = Field(
        default=None,
        description="Custom tool-call metadata (e.g. timeout, retry count, tool version).",
    )
