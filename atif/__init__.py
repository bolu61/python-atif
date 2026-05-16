"""Pydantic models for the Agent Trajectory Interchange Format (ATIF v1.7).

Reference: https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md
"""

try:
    from ._version import __version__, __version_tuple__
except ImportError:
    __version__ = "0.0.0+unknown"
    __version_tuple__ = (0, 0, 0, "unknown")

from .agent import Agent
from .content import ContentPart, ContentPartType, ImageMediaType, ImageSource
from .final_metrics import FinalMetrics
from .metrics import Metrics
from .observation import Observation
from .observation_result import ObservationResult
from .step import ReasoningEffort, Step, StepSource
from .subagent_trajectory_ref import SubagentTrajectoryRef
from .tool_call import ToolCall
from .trajectory import Trajectory

__all__ = [
    "__version__",
    "Agent",
    "ContentPart",
    "ContentPartType",
    "FinalMetrics",
    "ImageMediaType",
    "ImageSource",
    "Metrics",
    "Observation",
    "ObservationResult",
    "ReasoningEffort",
    "Step",
    "StepSource",
    "SubagentTrajectoryRef",
    "ToolCall",
    "Trajectory",
]
