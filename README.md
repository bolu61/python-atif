# atif

Pydantic models for the [Agent Trajectory Interchange Format (ATIF)][spec], a
standardized JSON schema for logging the complete interaction history of
autonomous LLM agents (user messages, agent responses, tool calls, observations,
metrics, and embedded subagent trajectories). Implements ATIF v1.7.

## Install

```bash
pip install atif
```

## Usage

```python
from atif import Trajectory

data = {
    "schema_version": "ATIF-v1.7",
    "agent": {"name": "my-agent", "version": "1.0.0", "model_name": "claude-sonnet-4-6"},
    "steps": [
        {"step_id": 1, "source": "user", "message": "What time is it?"},
        {
            "step_id": 2,
            "source": "agent",
            "message": "Let me check.",
            "tool_calls": [
                {"tool_call_id": "c1", "function_name": "now", "arguments": {}}
            ],
            "observation": {
                "results": [{"source_call_id": "c1", "content": "2026-05-16T12:00:00Z"}]
            },
            "metrics": {"prompt_tokens": 120, "completion_tokens": 18},
        },
    ],
}

trajectory = Trajectory.model_validate(data)
print(trajectory.steps[1].tool_calls[0].function_name)  # "now"
print(trajectory.to_json_dict(exclude_none=True))
```

Validation enforces the ATIF rules: sequential `step_id`s, ISO 8601 timestamps,
agent-only fields gated on `source == "agent"`, tool-call / observation
correlation, embedded-subagent `trajectory_id` uniqueness, and
`ContentPart` text/image XOR.

## Versioning

`atif`'s `MAJOR.MINOR` tracks the ATIF RFC version it implements
(`1.7.x` ⇔ ATIF v1.7); `PATCH` is reserved for library-only fixes. Because
the ATIF RFC occasionally introduces breaking changes on a MINOR bump
(e.g. v1.7's `SubagentTrajectoryRef` resolution change), a MINOR bump of
this library may be breaking too — pin to `atif~=1.7.0` if you need to
stay on a single ATIF version.

## AI disclosure

Parts of this project, including code, tests, and documentation, were
written with the assistance of AI tooling. Readers should be aware that
AI was involved in its production.

[spec]: https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md
