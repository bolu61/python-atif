from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .observation_result import ObservationResult


class Observation(BaseModel):
    """Environment/system feedback after a step (ATIF `ObservationSchema`)."""

    model_config = ConfigDict(extra="forbid")

    results: list[ObservationResult] = Field(
        ...,
        description="One entry per tool call, action, or system-event result.",
    )
