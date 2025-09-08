"""Perception Layer - DOM Processing and Visual Annotation"""

from .dom_processor import DOMProcessor
from .visual_annotator import VisualAnnotator
from .state_observer import StateObserver
from .models import WebPageState, InteractiveElement, AnnotatedElement

__all__ = [
    "DOMProcessor",
    "VisualAnnotator", 
    "StateObserver",
    "WebPageState",
    "InteractiveElement",
    "AnnotatedElement"
]