from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SubagentTrajectoryRef(BaseModel):
    """Reference to a delegated subagent trajectory (ATIF `SubagentTrajectoryRefSchema`).

    Two resolution mechanisms (at least one MUST be set):
    - Embedded: `trajectory_id` matches an entry in the parent's `subagent_trajectories`.
    - File-ref: `trajectory_path` points at an external trajectory file.

    `session_id` is run-scoped and **informational only** — not a valid resolution key.
    """

    model_config = ConfigDict(extra="forbid")

    trajectory_id: str | None = Field(
        default=None,
        description="Canonical id for embedded refs; matches `Trajectory.trajectory_id`.",
    )
    trajectory_path: str | None = Field(
        default=None,
        description="External location of the subagent trajectory (path, URL, DB ref).",
    )
    session_id: str | None = Field(
        default=None,
        description="Informational run identity; NOT a valid resolution key.",
    )
    extra: dict[str, Any] | None = Field(
        default=None,
        description="Custom metadata about the subagent execution.",
    )

    @model_validator(mode="after")
    def _require_resolvable(self) -> "SubagentTrajectoryRef":
        if self.trajectory_id is None and self.trajectory_path is None:
            raise ValueError(
                "SubagentTrajectoryRef must set at least one of "
                "`trajectory_id` (embedded) or `trajectory_path` (file-ref)."
            )
        return self
