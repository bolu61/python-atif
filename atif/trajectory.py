from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .agent import Agent
from .content import ContentPart
from .final_metrics import FinalMetrics
from .step import Step


class Trajectory(BaseModel):
    """Root ATIF trajectory document (ATIF `Trajectory`).

    A trajectory is a sequence of interactions between a user and an agent,
    including the agent's internal reasoning, actions, and observations.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(
        ...,
        description="ATIF compatibility tag, e.g. 'ATIF-v1.7'.",
    )
    session_id: str | None = Field(
        default=None,
        description=(
            "Run-scoped identifier. MAY be shared across siblings or continuation segments. "
            "Not a valid resolution key for subagent refs."
        ),
    )
    trajectory_id: str | None = Field(
        default=None,
        description=(
            "Per-document identifier (v1.7+). REQUIRED on embedded subagents and unique "
            "within a parent's `subagent_trajectories`."
        ),
    )
    agent: Agent = Field(..., description="Agent system configuration.")
    steps: list[Step] = Field(
        ..., description="Complete interaction history in turn order."
    )
    notes: str | None = Field(
        default=None,
        description="Developer notes / explanations for format discrepancies.",
    )
    final_metrics: FinalMetrics | None = Field(
        default=None, description="Aggregate metrics for the whole trajectory."
    )
    continued_trajectory_ref: str | None = Field(
        default=None,
        description="Pointer to a continuation trajectory file (e.g. post-summarization).",
    )
    extra: dict[str, Any] | None = Field(
        default=None, description="Custom root-level metadata."
    )
    subagent_trajectories: list["Trajectory"] | None = Field(
        default=None,
        description=(
            "Embedded subagent trajectories (v1.7+). Each entry MUST set `trajectory_id` "
            "and ids MUST be unique within this array."
        ),
    )

    @model_validator(mode="after")
    def _validate_steps_and_subagents(self) -> "Trajectory":
        for index, step in enumerate(self.steps, start=1):
            if step.step_id != index:
                raise ValueError(
                    f"steps[{index - 1}].step_id={step.step_id} is not sequential; "
                    f"expected {index}."
                )

        if self.subagent_trajectories:
            seen: set[str] = set()
            for i, sub in enumerate(self.subagent_trajectories):
                if sub.trajectory_id is None:
                    raise ValueError(
                        f"subagent_trajectories[{i}] must set `trajectory_id` "
                        "when embedded in a parent trajectory."
                    )
                if sub.trajectory_id in seen:
                    raise ValueError(
                        f"Duplicate trajectory_id={sub.trajectory_id!r} in "
                        "`subagent_trajectories`."
                    )
                seen.add(sub.trajectory_id)
        return self

    def has_multimodal_content(self) -> bool:
        """True if any step message or observation content uses `ContentPart` arrays."""
        for step in self.steps:
            if isinstance(step.message, list):
                return True
            if step.observation is not None:
                for result in step.observation.results:
                    if isinstance(result.content, list):
                        return True
        if self.subagent_trajectories:
            return any(s.has_multimodal_content() for s in self.subagent_trajectories)
        return False

    def to_json_dict(self, exclude_none: bool = True) -> dict[str, Any]:
        """Dump to a JSON-serialisable dict, dropping unset fields by default."""
        return self.model_dump(mode="json", exclude_none=exclude_none)


Trajectory.model_rebuild()
# Re-export so callers can `from atif.trajectory import ContentPart` if they want.
__all__ = ["Trajectory", "ContentPart"]
