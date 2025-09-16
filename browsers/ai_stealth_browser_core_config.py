"""Runtime configuration utilities for AI Stealth Browser.

Lightweight Pydantic-based config that can be extended without
breaking existing usage. Values are loaded from environment with
reasonable defaults for alpha.
"""

from __future__ import annotations

import os
from pydantic import BaseModel, Field
from typing import Tuple


class RuntimeConfig(BaseModel):
    navigation_max_steps: int = Field(5, ge=1, description="Maximum navigation steps to execute")
    enable_human_sim: bool = Field(
        True, description="Whether to run human simulation after each navigation"
    )
    enable_stealth_verification: bool = Field(
        True, description="Run post-navigation stealth checks"
    )
    human_pause_range_ms: Tuple[int, int] = Field(
        (150, 400), description="Inclusive min/max pause jitter between steps (ms)"
    )

    @classmethod
    def load(cls) -> "RuntimeConfig":
        def _bool(name: str, default: bool) -> bool:
            v = os.getenv(name)
            if v is None:
                return default
            return v.lower() in {"1", "true", "yes", "on"}

        def _int(name: str, default: int) -> int:
            try:
                return int(os.getenv(name, str(default)))
            except ValueError:
                return default

        max_steps = _int("AI_STEALTH_NAV_MAX_STEPS", 5)
        enable_human = _bool("AI_STEALTH_HUMAN_SIM", True)
        enable_ver = _bool("AI_STEALTH_VERIFY", True)
        pause_min = _int("AI_STEALTH_HUMAN_PAUSE_MIN_MS", 150)
        pause_max = _int("AI_STEALTH_HUMAN_PAUSE_MAX_MS", 400)
        if pause_max < pause_min:
            pause_max = pause_min
        return cls(
            navigation_max_steps=max_steps,
            enable_human_sim=enable_human,
            enable_stealth_verification=enable_ver,
            human_pause_range_ms=(pause_min, pause_max),
        )

    def describe(self) -> dict:
        """Return a plain dict of config values plus source env variables.

        Helpful for diagnostics & preflight reporting without exposing
        unrelated environment details.
        """
        return {
            "navigation_max_steps": self.navigation_max_steps,
            "enable_human_sim": self.enable_human_sim,
            "enable_stealth_verification": self.enable_stealth_verification,
            "human_pause_range_ms": list(self.human_pause_range_ms),
            "env": {
                k: os.getenv(k)
                for k in [
                    "AI_STEALTH_NAV_MAX_STEPS",
                    "AI_STEALTH_HUMAN_SIM",
                    "AI_STEALTH_VERIFY",
                    "AI_STEALTH_HUMAN_PAUSE_MIN_MS",
                    "AI_STEALTH_HUMAN_PAUSE_MAX_MS",
                ]
                if os.getenv(k) is not None
            },
        }


__all__ = ["RuntimeConfig"]
