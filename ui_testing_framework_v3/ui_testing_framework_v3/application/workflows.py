"""
Application workflows for complex test generation using LangGraph.

This module builds linear workflows as LangGraph StateGraphs and emits
events around each step for observability.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from langgraph.graph import END, START, StateGraph  # type: ignore[reportMissingTypeStubs]

from ui_testing_framework_v3.core.value_objects import URL

if TYPE_CHECKING:  # pragma: no cover - import typing-only
    from collections.abc import Awaitable, Callable

    from ui_testing_framework_v3.core.models import Element, TestCase
    from ui_testing_framework_v3.infrastructure.config import ConfigManager
    from ui_testing_framework_v3.infrastructure.events import EventBus
    from ui_testing_framework_v3.plugins.registry import PluginRegistry


class WorkflowState(TypedDict):
    """State passed through workflow steps."""

    url: str
    profile: str
    elements: list[Element]
    formatted: dict[str, Any]
    tests: list[TestCase]
    errors: list[str]
    metadata: dict[str, Any]


class WorkflowStep:
    """Individual workflow step container."""

    def __init__(self, name: str, handler: Callable[[WorkflowState], Awaitable[WorkflowState]]):
        self.name = name
        self.handler = handler


class SimpleWorkflow:
    """Linear workflow implemented with LangGraph."""

    def __init__(
        self,
        registry: PluginRegistry,
        config: ConfigManager | None = None,
        events: EventBus | None = None,
    ) -> None:
        self._registry = registry
        self._config = config
        self._events = events
        self._steps: list[WorkflowStep] = []

    def _wrap_handler(
        self, step_name: str, handler: Callable[[WorkflowState], Awaitable[WorkflowState]]
    ) -> Callable[[WorkflowState], Awaitable[WorkflowState]]:
        async def _wrapped(state: WorkflowState) -> WorkflowState:
            if self._events:
                self._events.emit("workflow.step.start", {"step": step_name})
            try:
                result = await handler(state)
            except Exception as e:  # pragma: no cover - defensive
                error_msg = f"Step '{step_name}' failed: {e}"
                state["errors"].append(error_msg)
                if self._events:
                    self._events.emit(
                        "workflow.step.error", {"step": step_name, "error": error_msg}
                    )
                return state
            else:
                if self._events:
                    self._events.emit("workflow.step.complete", {"step": step_name})
                return result

        return _wrapped

    def add_step(
        self, name: str, handler: Callable[[WorkflowState], Awaitable[WorkflowState]]
    ) -> None:
        """Add a step to the workflow."""
        self._steps.append(WorkflowStep(name, handler))

    async def run(self, initial_state: WorkflowState) -> WorkflowState:
        """Compile and execute the workflow graph for the provided state."""
        if self._events:
            self._events.emit(
                "workflow.start",
                {"steps": len(self._steps), "url": initial_state["url"]},
            )

        builder: Any = StateGraph(WorkflowState)

        # Add nodes
        for step in self._steps:
            builder.add_node(step.name, self._wrap_handler(step.name, step.handler))

        # Wire edges linearly: START -> step0 -> step1 -> ... -> END
        if self._steps:
            first = self._steps[0].name
            builder.add_edge(START, first)
            for prev, nxt in zip(self._steps, self._steps[1:], strict=True):
                builder.add_edge(prev.name, nxt.name)
            builder.add_edge(self._steps[-1].name, END)
        else:
            builder.add_edge(START, END)

        graph: Any = builder.compile()
        current_state: WorkflowState = await graph.ainvoke(initial_state)

        if self._events:
            self._events.emit(
                "workflow.complete",
                {"errors": len(current_state["errors"]), "tests": len(current_state["tests"])},
            )

        return current_state


class TestGenerationWorkflow(SimpleWorkflow):
    """Workflow for complete test generation."""

    def __init__(
        self,
        registry: PluginRegistry,
        config: ConfigManager | None = None,
        events: EventBus | None = None,
    ) -> None:
        super().__init__(registry, config, events)
        self.add_step("extract", self._extract_elements)
        self.add_step("format", self._format_elements)
        self.add_step("generate", self._generate_tests)
        self.add_step("validate", self._validate_tests)

    async def _extract_elements(self, state: WorkflowState) -> WorkflowState:
        """Extract elements using configured extractor."""
        try:
            extractor_name = state.get("profile", "stealth")
            extractor = self._registry.get("extractor", extractor_name)
            url = URL(state["url"])
            elements = await extractor.extract(url)
            state["elements"] = elements
            state["metadata"]["extraction_count"] = len(elements)
            if self._events:
                self._events.emit(
                    "workflow.extract.complete", {"count": len(elements), "url": state["url"]}
                )
        except Exception as e:  # pragma: no cover - defensive
            state["errors"].append(f"Extraction failed: {e}")
        return state

    async def _format_elements(self, state: WorkflowState) -> WorkflowState:
        """Format elements for test generation."""
        try:
            formatter_name = (
                self._config.get("formatter.default", "llm_test") if self._config else "llm_test"
            )
            formatter = self._registry.get("formatter", formatter_name)
            formatted = formatter.format(state["elements"])  # sync formatting
            state["formatted"] = formatted
            if self._events:
                self._events.emit(
                    "workflow.format.complete", {"formatted_keys": list(formatted.keys())}
                )
        except Exception as e:  # pragma: no cover - defensive
            state["errors"].append(f"Formatting failed: {e}")
        return state

    async def _generate_tests(self, state: WorkflowState) -> WorkflowState:
        """Generate test cases."""
        try:
            generator_name = (
                self._config.get("test_generator.default", "simple") if self._config else "simple"
            )
            generator = self._registry.get("test_generator", generator_name)
            tests = await generator.generate(state["formatted"])  # async generation
            state["tests"] = tests
            state["metadata"]["test_count"] = len(tests)
            if self._events:
                self._events.emit("workflow.generate.complete", {"count": len(tests)})
        except Exception as e:  # pragma: no cover - defensive
            state["errors"].append(f"Test generation failed: {e}")
        return state

    async def _validate_tests(self, state: WorkflowState) -> WorkflowState:
        """Validate generated tests and keep only valid ones."""
        valid_tests: list[TestCase] = []
        invalid_count = 0
        for test in state["tests"]:
            if test.validate():
                valid_tests.append(test)
            else:
                invalid_count += 1
        if invalid_count > 0:
            state["errors"].append(f"{invalid_count} invalid tests removed")
        state["tests"] = valid_tests
        state["metadata"]["valid_test_count"] = len(valid_tests)
        if self._events:
            self._events.emit(
                "workflow.validate.complete",
                {"valid": len(valid_tests), "invalid": invalid_count},
            )
        return state

    async def create_and_run(self, url: str, profile: str = "stealth") -> WorkflowState:
        """Create initial state and run workflow."""
        initial_state: WorkflowState = {
            "url": url,
            "profile": profile,
            "elements": [],
            "formatted": {},
            "tests": [],
            "errors": [],
            "metadata": {},
        }
        return await self.run(initial_state)


class QAWorkflow(TestGenerationWorkflow):
    """QA-focused workflow with enhanced validation and patterns."""

    def __init__(
        self,
        registry: PluginRegistry,
        config: ConfigManager | None = None,
        events: EventBus | None = None,
    ) -> None:
        super().__init__(registry, config, events)
        self.add_step("filter_qa", self._filter_qa_elements)
        self.add_step("enhance_tests", self._enhance_qa_tests)

    async def _filter_qa_elements(self, state: WorkflowState) -> WorkflowState:
        """Filter elements for QA testing by priority and interactivity."""
        qa_elements = [
            elem
            for elem in state["elements"]
            if elem.is_interactive and elem.test_priority in ["high", "critical"]
        ]
        state["metadata"]["original_count"] = len(state["elements"])
        state["elements"] = qa_elements
        if self._events:
            self._events.emit(
                "workflow.qa_filter.complete",
                {"original": state["metadata"]["original_count"], "filtered": len(qa_elements)},
            )
        return state

    async def _enhance_qa_tests(self, state: WorkflowState) -> WorkflowState:
        """Enhance tests with QA-specific assertions and tags."""
        enhanced_tests: list[TestCase] = []
        for test in state["tests"]:
            if any("aria-" in step for step in test.steps):
                test.assertions.append("Element should be accessible")
                test.tags.append("accessibility")
            if any("input" in step.lower() for step in test.steps):
                test.assertions.append("Input validation should work correctly")
                test.tags.append("validation")
            enhanced_tests.append(test)
        state["tests"] = enhanced_tests
        if self._events:
            self._events.emit("workflow.qa_enhance.complete", {"enhanced": len(enhanced_tests)})
        return state
