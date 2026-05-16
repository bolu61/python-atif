from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FinalMetrics(BaseModel):
    """Aggregate metrics for a whole trajectory (ATIF `FinalMetricsSchema`)."""

    model_config = ConfigDict(extra="forbid")

    total_prompt_tokens: int | None = Field(
        default=None,
        description="Sum of all `prompt_tokens` across steps (cached + non-cached).",
    )
    total_completion_tokens: int | None = Field(
        default=None, description="Sum of all `completion_tokens` across steps."
    )
    total_cached_tokens: int | None = Field(
        default=None,
        description="Sum of all `cached_tokens` (subset of `total_prompt_tokens`).",
    )
    total_cost_usd: float | None = Field(
        default=None, description="Total monetary cost across the trajectory in USD."
    )
    total_steps: int | None = Field(
        default=None,
        description=(
            "Total step count. MAY diverge from `len(steps)` when explained in `notes`."
        ),
    )
    extra: dict[str, Any] | None = Field(
        default=None, description="Custom aggregate metrics."
    )
