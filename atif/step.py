from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .content import ContentPart
from .metrics import Metrics
from .observation import Observation
from .tool_call import ToolCall

StepSource = Literal["system", "user", "agent"]
ReasoningEffort = str | float


class Step(BaseModel):
    """A single turn in a trajectory (ATIF `StepObject`).

    Represents a system prompt, a user message, or one complete agent turn
    (LLM inference, action execution, observation receipt).
    """

    model_config = ConfigDict(extra="forbid")

    step_id: int = Field(..., ge=1, description="Ordinal index of the turn (starting at 1).")
    timestamp: str | None = Field(
        default=None,
        description="ISO 8601 timestamp, e.g. '2025-10-16T14:30:00Z'.",
    )
    source: StepSource = Field(..., description="Originator of this step.")
    model_name: str | None = Field(
        default=None,
        description="Specific LLM used. Agent-only; falls back to `Trajectory.agent.model_name`.",
    )
    reasoning_effort: ReasoningEffort | None = Field(
        default=None,
        description="Qualitative/quantitative effort score. Agent-only.",
    )
    message: str | list[ContentPart] = Field(
        ...,
        description=(
            "Dialogue message. String for text, or `ContentPart` array for multimodal (v1.6+)."
        ),
    )
    reasoning_content: str | None = Field(
        default=None,
        description="Explicit internal reasoning. Agent-only.",
    )
    tool_calls: list[ToolCall] | None = Field(
        default=None,
        description="Structured actions for this turn. Agent-only.",
    )
    observation: Observation | None = Field(
        default=None,
        description=(
            "Environment / system feedback. For agent steps, results from tool calls or "
            "non-tool actions. For system steps, results from infrastructure events."
        ),
    )
    metrics: Metrics | None = Field(
        default=None, description="LLM operational/confidence data. Agent-only."
    )
    extra: dict[str, Any] | None = Field(
        default=None, description="Custom step-level metadata."
    )
    llm_call_count: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Number of LLM inferences for this step. `0` on an agent step signals a "
            "deterministic (non-LLM) dispatch (metrics and reasoning_content MUST be absent). "
            "`>1` means metrics are aggregated."
        ),
    )
    is_copied_context: bool | None = Field(
        default=None,
        description=(
            "True if this step was copied from a prior trajectory for context. "
            "Consumers MUST filter such steps out of SFT training data."
        ),
    )

    @field_validator("timestamp")
    @classmethod
    def _validate_timestamp(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"timestamp must be ISO 8601, got {v!r}") from exc
        return v

    @model_validator(mode="after")
    def _check_source_constraints(self) -> "Step":
        agent_only = {
            "model_name": self.model_name,
            "reasoning_effort": self.reasoning_effort,
            "reasoning_content": self.reasoning_content,
            "tool_calls": self.tool_calls,
            "metrics": self.metrics,
        }
        if self.source != "agent":
            for name, value in agent_only.items():
                if value is not None:
                    raise ValueError(
                        f"Field `{name}` is only valid on `source='agent'` steps "
                        f"(this step has source={self.source!r})."
                    )

        if self.source == "agent" and self.llm_call_count == 0:
            if self.metrics is not None:
                raise ValueError(
                    "When `llm_call_count == 0` on an agent step, `metrics` MUST be absent."
                )
            if self.reasoning_content is not None:
                raise ValueError(
                    "When `llm_call_count == 0` on an agent step, "
                    "`reasoning_content` MUST be absent."
                )

        if self.observation is not None and self.tool_calls is not None:
            tool_call_ids = {tc.tool_call_id for tc in self.tool_calls}
            for result in self.observation.results:
                if (
                    result.source_call_id is not None
                    and result.source_call_id not in tool_call_ids
                ):
                    raise ValueError(
                        f"observation.results[*].source_call_id={result.source_call_id!r} "
                        f"does not match any tool_call in step {self.step_id}."
                    )
        return self
