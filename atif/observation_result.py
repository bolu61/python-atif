from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .content import ContentPart
from .subagent_trajectory_ref import SubagentTrajectoryRef


class ObservationResult(BaseModel):
    """Single observation result (ATIF `ObservationResultSchema`).

    `content` MAY be omitted when `subagent_trajectory_ref` is present.
    """

    model_config = ConfigDict(extra="forbid")

    source_call_id: str | None = Field(
        default=None,
        description=(
            "The `ToolCall.tool_call_id` this result corresponds to. "
            "If null/omitted the result comes from a non-tool action or system event."
        ),
    )
    content: str | list[ContentPart] | None = Field(
        default=None,
        description="Tool/action output; string or multimodal `ContentPart` array (v1.6+).",
    )
    subagent_trajectory_ref: list[SubagentTrajectoryRef] | None = Field(
        default=None,
        description="Refs to delegated subagent trajectories; use a singleton array for one.",
    )
    extra: dict[str, Any] | None = Field(
        default=None,
        description="Custom result-level metadata (e.g. retrieval_score, source_doc_id).",
    )
