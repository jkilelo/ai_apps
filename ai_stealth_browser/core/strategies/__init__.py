"""Strategy interfaces for pluggable behaviors (human simulation, detection mitigation)."""

from .base import StrategyContext, Strategy
from .human import HumanSimulationStrategy
from .detection import DetectionMitigationStrategy

__all__ = [
    "StrategyContext",
    "Strategy",
    "HumanSimulationStrategy",
    "DetectionMitigationStrategy",
]
