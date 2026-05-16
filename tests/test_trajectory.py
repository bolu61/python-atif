from __future__ import annotations

import pytest
from pydantic import ValidationError

from atif import (
    Agent,
    ContentPart,
    ImageSource,
    Step,
    SubagentTrajectoryRef,
    Trajectory,
)


CANONICAL_EXAMPLE: dict = {
    "schema_version": "ATIF-v1.5",
    "session_id": "025B810F-B3A2-4C67-93C0-FE7A142A947A",
    "agent": {
        "name": "harbor-agent",
        "version": "1.0.0",
        "model_name": "gemini-2.5-flash",
        "tool_definitions": [
            {"type": "function", "function": {"name": "financial_search"}}
        ],
    },
    "notes": "Initial test trajectory.",
    "final_metrics": {
        "total_prompt_tokens": 1120,
        "total_completion_tokens": 124,
        "total_cached_tokens": 200,
        "total_cost_usd": 0.00078,
        "total_steps": 3,
    },
    "steps": [
        {
            "step_id": 1,
            "timestamp": "2025-10-11T10:30:00Z",
            "source": "user",
            "message": "What is the current trading price of GOOGL?",
        },
        {
            "step_id": 2,
            "timestamp": "2025-10-11T10:30:02Z",
            "source": "agent",
            "model_name": "gemini-2.5-flash",
            "reasoning_effort": "medium",
            "message": "I will look up the price and volume.",
            "reasoning_content": "Two parallel tool calls.",
            "tool_calls": [
                {
                    "tool_call_id": "call_price_1",
                    "function_name": "financial_search",
                    "arguments": {"ticker": "GOOGL", "metric": "price"},
                },
                {
                    "tool_call_id": "call_volume_2",
                    "function_name": "financial_search",
                    "arguments": {"ticker": "GOOGL", "metric": "volume"},
                },
            ],
            "observation": {
                "results": [
                    {"source_call_id": "call_price_1", "content": "GOOGL: $185.35"},
                    {"source_call_id": "call_volume_2", "content": "Volume: 1.5M"},
                ]
            },
            "metrics": {
                "prompt_tokens": 520,
                "completion_tokens": 80,
                "cached_tokens": 200,
                "cost_usd": 0.00045,
            },
        },
        {
            "step_id": 3,
            "timestamp": "2025-10-11T10:30:05Z",
            "source": "agent",
            "model_name": "gemini-2.5-flash",
            "message": "GOOGL trades at $185.35 with 1.5M volume.",
            "metrics": {"prompt_tokens": 600, "completion_tokens": 44, "cost_usd": 0.00033},
        },
    ],
}


def _minimal_agent() -> Agent:
    return Agent(name="t", version="1")


def test_canonical_example_parses_and_round_trips():
    trajectory = Trajectory.model_validate(CANONICAL_EXAMPLE)
    assert trajectory.schema_version == "ATIF-v1.5"
    assert len(trajectory.steps) == 3
    assert trajectory.steps[1].tool_calls is not None
    assert trajectory.steps[1].tool_calls[0].function_name == "financial_search"

    dumped = trajectory.to_json_dict(exclude_none=True)
    assert "session_id" in dumped
    # round-trip must re-validate
    assert Trajectory.model_validate(dumped) == trajectory


def test_step_id_must_be_sequential():
    with pytest.raises(ValidationError, match="not sequential"):
        Trajectory(
            schema_version="ATIF-v1.7",
            agent=_minimal_agent(),
            steps=[Step(step_id=2, source="user", message="hi")],
        )


def test_agent_only_fields_rejected_on_user_step():
    with pytest.raises(ValidationError, match="only valid on `source='agent'`"):
        Step(
            step_id=1,
            source="user",
            message="hi",
            reasoning_content="not allowed here",
        )


def test_tool_call_must_correlate_with_observation():
    with pytest.raises(ValidationError, match="does not match any tool_call"):
        Step.model_validate(
            {
                "step_id": 1,
                "source": "agent",
                "message": "x",
                "tool_calls": [
                    {"tool_call_id": "real", "function_name": "f", "arguments": {}}
                ],
                "observation": {
                    "results": [{"source_call_id": "wrong", "content": "y"}]
                },
            }
        )


def test_iso8601_timestamp_validation():
    with pytest.raises(ValidationError, match="ISO 8601"):
        Step(step_id=1, source="user", message="hi", timestamp="not-a-date")


def test_llm_call_count_zero_forbids_metrics_and_reasoning():
    with pytest.raises(ValidationError, match="`metrics` MUST be absent"):
        Step.model_validate(
            {
                "step_id": 1,
                "source": "agent",
                "message": "dispatch",
                "llm_call_count": 0,
                "metrics": {"prompt_tokens": 1},
            }
        )


def test_subagent_ref_requires_id_or_path():
    with pytest.raises(ValidationError, match="at least one of"):
        SubagentTrajectoryRef()


def test_subagent_ref_accepts_path_only():
    SubagentTrajectoryRef(trajectory_path="s3://bucket/sub.json")


def test_embedded_subagent_requires_trajectory_id():
    with pytest.raises(ValidationError, match="must set `trajectory_id`"):
        Trajectory.model_validate(
            {
                "schema_version": "ATIF-v1.7",
                "agent": {"name": "a", "version": "1"},
                "steps": [{"step_id": 1, "source": "user", "message": "hi"}],
                "subagent_trajectories": [
                    {
                        "schema_version": "ATIF-v1.7",
                        "agent": {"name": "b", "version": "1"},
                        "steps": [{"step_id": 1, "source": "user", "message": "x"}],
                    }
                ],
            }
        )


def test_embedded_subagent_ids_must_be_unique():
    with pytest.raises(ValidationError, match="Duplicate trajectory_id"):
        Trajectory.model_validate(
            {
                "schema_version": "ATIF-v1.7",
                "agent": {"name": "a", "version": "1"},
                "steps": [{"step_id": 1, "source": "user", "message": "hi"}],
                "subagent_trajectories": [
                    {
                        "schema_version": "ATIF-v1.7",
                        "trajectory_id": "dup",
                        "agent": {"name": "b", "version": "1"},
                        "steps": [{"step_id": 1, "source": "user", "message": "x"}],
                    },
                    {
                        "schema_version": "ATIF-v1.7",
                        "trajectory_id": "dup",
                        "agent": {"name": "c", "version": "1"},
                        "steps": [{"step_id": 1, "source": "user", "message": "y"}],
                    },
                ],
            }
        )


def test_content_part_text_image_xor():
    with pytest.raises(ValidationError, match="must omit `source`"):
        ContentPart(type="text", text="hi", source=ImageSource(media_type="image/png", path="x"))
    with pytest.raises(ValidationError, match="must omit `text`"):
        ContentPart(type="image", text="hi", source=ImageSource(media_type="image/png", path="x"))
    with pytest.raises(ValidationError, match="requires `source`"):
        ContentPart(type="image")
    with pytest.raises(ValidationError, match="requires `text`"):
        ContentPart(type="text")


def test_has_multimodal_content():
    trajectory = Trajectory.model_validate(
        {
            "schema_version": "ATIF-v1.7",
            "agent": {"name": "a", "version": "1"},
            "steps": [
                {
                    "step_id": 1,
                    "source": "user",
                    "message": [
                        {"type": "text", "text": "What is this?"},
                        {
                            "type": "image",
                            "source": {"media_type": "image/png", "path": "x.png"},
                        },
                    ],
                }
            ],
        }
    )
    assert trajectory.has_multimodal_content() is True


def test_unknown_fields_rejected():
    with pytest.raises(ValidationError):
        Trajectory.model_validate(
            {
                "schema_version": "ATIF-v1.7",
                "agent": {"name": "a", "version": "1"},
                "steps": [{"step_id": 1, "source": "user", "message": "x"}],
                "made_up_field": True,
            }
        )
