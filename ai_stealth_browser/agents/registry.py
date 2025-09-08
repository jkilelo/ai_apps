"""Central pydantic-ai agent registry.

All agents use structured outputs to enforce determinism and enable rigorous
TDD. Test harnesses override model with TestModel.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, TYPE_CHECKING
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import os
from pathlib import Path


# Dependency bundle -----------------------------------------------------------------
@dataclass
class CoreDeps:
    event_bus: "EventBus"  # type: ignore[name-defined]
    config: Dict[str, str] | None = None


if TYPE_CHECKING:  # pragma: no cover
    from core.events import EventBus


# Output models ---------------------------------------------------------------------
class StealthAdvisory(BaseModel):
    risk_level: str = Field(pattern=r"^(low|medium|high)$")
    actions: List[str]
    justification: str


class NavigationPlan(BaseModel):
    steps: List[str] = Field(min_length=1)
    target_url: Optional[str] = None


class SecurityFinding(BaseModel):
    id: str
    severity: str
    description: str
    recommendation: str


class SecuritySummary(BaseModel):
    risk_level: str
    findings: List[SecurityFinding]


class PerfBottleneck(BaseModel):
    area: str
    metric: str
    baseline: float
    observed: float
    suggestion: str


class PerfAnalysis(BaseModel):
    bottlenecks: List[PerfBottleneck] = Field(default_factory=list)
    quick_wins: List[str] = Field(default_factory=list)


class LearningAdjustment(BaseModel):
    area: str
    change: str
    expected_effect: str


class LearningUpdate(BaseModel):
    new_hypotheses: List[str]
    strategy_adjustments: List[LearningAdjustment]
    metrics_to_watch: List[str]


class ArchitecturePlan(BaseModel):
    tasks: List[str]
    risks: List[str]
    validation: List[str]


# Agent Definitions -----------------------------------------------------------------
def _load_env():  # minimal .env loader (avoids extra dependency)
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    root = Path(__file__).resolve().parent.parent  # project root
    env_path = root / ".env"
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if k and k not in os.environ:
                os.environ[k] = v.strip().strip('"').strip("'")
    except Exception:  # pragma: no cover - non critical
        pass


_load_env()

MODEL = "anthropic:claude-sonnet-4-20250514"

# Hard HALT policy: this is an AI-first framework; without a live LLM key we abort immediately.
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit(
        "HALT: Missing ANTHROPIC_API_KEY. AI-first framework will not start without a live LLM key."
    )

_model_arg = MODEL  # Always use real model; tests inject TestModel via override stacks

stealth_agent = Agent(
    _model_arg,
    output_type=StealthAdvisory,
    name="stealth",
    system_prompt=(
        "You are the StealthAgent. Assess detection signals and recommend minimal, reversible countermeasures."
    ),
)

navigation_agent = Agent(
    _model_arg,
    output_type=NavigationPlan,
    name="navigation",
    system_prompt="Produce a concise, deterministic navigation step list. Never browse yourself.",
)

security_agent = Agent(
    _model_arg,
    output_type=SecuritySummary,
    name="security",
    system_prompt="Identify concrete security & stealth-surface risks with actionable mitigations only.",
)

performance_agent = Agent(
    _model_arg,
    output_type=PerfAnalysis,
    name="performance",
    system_prompt="Highlight top performance bottlenecks with data-first justifications.",
)

learning_agent = Agent(
    _model_arg,
    output_type=LearningUpdate,
    name="learning",
    system_prompt="Infer adaptive heuristics from recent trace summaries.",
)

architect_agent = Agent(
    _model_arg,
    output_type=ArchitecturePlan,
    name="architect",
    system_prompt="Decompose feature request into ordered tasks, risks, validation steps.",
)


ALL_AGENTS = {
    "stealth": stealth_agent,
    "navigation": navigation_agent,
    "security": security_agent,
    "performance": performance_agent,
    "learning": learning_agent,
    "architect": architect_agent,
}

__all__ = [
    "CoreDeps",
    "StealthAdvisory",
    "NavigationPlan",
    "SecurityFinding",
    "SecuritySummary",
    "PerfBottleneck",
    "PerfAnalysis",
    "LearningAdjustment",
    "LearningUpdate",
    "ArchitecturePlan",
    "ALL_AGENTS",
]
