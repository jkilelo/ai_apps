#!/usr/bin/env python3
"""
Proof of Concept: V3 Hexagonal Plugin Architecture
Demonstrates the power of lean, extensible, modular design
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from typing import Any, Protocol, runtime_checkable

# ==============================================================================
# LAYER 1: DOMAIN CORE (Zero Dependencies)
# ==============================================================================


@dataclass(frozen=True)
class Element:
    """Pure domain model - immutable"""

    selector: str
    tag_name: str
    attributes: dict[str, Any] = field(default_factory=dict)

    @cached_property
    def is_interactive(self) -> bool:
        """Business rule: what makes an element interactive"""
        return self.tag_name in ["button", "input", "a", "select", "textarea"]

    @cached_property
    def interaction_score(self) -> float:
        """Business logic for scoring"""
        score = 0.0
        if self.is_interactive:
            score += 0.5
        if self.attributes.get("aria-label"):
            score += 0.3
        if self.attributes.get("id"):
            score += 0.2
        return min(score, 1.0)


@dataclass
class TestCase:
    """Domain model for test cases"""

    name: str
    steps: list[str]
    expected: list[str]

    def validate(self) -> bool:
        """Business rule: valid test must have steps and expectations"""
        return len(self.steps) > 0 and len(self.expected) > 0


# ==============================================================================
# LAYER 2: PORTS (Contracts/Interfaces)
# ==============================================================================


@runtime_checkable
class IExtractor(Protocol):
    """Port for element extraction"""

    def extract(self, url: str) -> list[Element]:
        """Extract elements from URL"""
        ...

    @property
    def name(self) -> str:
        """Get extractor name"""
        ...


@runtime_checkable
class IFormatter(Protocol):
    """Port for formatting elements"""

    def format(self, elements: list[Element]) -> dict[str, Any]:
        """Format elements for specific purpose"""
        ...

    @property
    def format_type(self) -> str:
        """Get format type"""
        ...


@runtime_checkable
class ITestGenerator(Protocol):
    """Port for test generation"""

    def generate(self, formatted_data: dict[str, Any]) -> list[TestCase]:
        """Generate test cases from formatted data"""
        ...


# ==============================================================================
# LAYER 3: ADAPTERS (Port Implementations)
# ==============================================================================


class SimpleExtractor:
    """Simple adapter implementing IExtractor"""

    def __init__(self):
        self._cache = {}
        self._history = deque(maxlen=10)

    @property
    def name(self) -> str:
        return "simple"

    @lru_cache(maxsize=32)
    def extract(self, url: str) -> list[Element]:
        """Extract with caching"""
        # Simulate extraction
        elements = [
            Element(
                selector="#search",
                tag_name="input",
                attributes={"id": "search", "type": "text", "aria-label": "Search"},
            ),
            Element(
                selector=".submit-btn",
                tag_name="button",
                attributes={"class": "submit-btn", "aria-label": "Submit"},
            ),
            Element(selector="#logo", tag_name="img", attributes={"id": "logo", "alt": "Logo"}),
        ]

        self._history.append(url)
        return elements


class QAExtractor:
    """QA-focused extractor adapter"""

    @property
    def name(self) -> str:
        return "qa"

    def extract(self, url: str) -> list[Element]:
        """Extract only QA-relevant elements"""
        # Get all elements
        all_elements = SimpleExtractor().extract(url)

        # Filter for QA (only interactive with high score)
        qa_elements = [e for e in all_elements if e.interaction_score > 0.5]

        return qa_elements


class LLMTestFormatter:
    """Formatter for LLM test generation"""

    @property
    def format_type(self) -> str:
        return "llm_test"

    def format(self, elements: list[Element]) -> dict[str, Any]:
        """Format elements for LLM consumption"""

        # Group by type
        grouped = defaultdict(list)
        for elem in elements:
            grouped[elem.tag_name].append(
                {
                    "selector": elem.selector,
                    "attributes": elem.attributes,
                    "score": elem.interaction_score,
                }
            )

        return {
            "total_elements": len(elements),
            "interactive_elements": len([e for e in elements if e.is_interactive]),
            "elements_by_type": dict(grouped),
            "test_hints": self._generate_hints(elements),
        }

    def _generate_hints(self, elements: list[Element]) -> list[str]:
        """Generate test hints based on elements"""
        hints = []

        if any(e.tag_name == "input" for e in elements):
            hints.append("Test input validation")

        if any(e.tag_name == "button" for e in elements):
            hints.append("Test button interactions")

        if any(e.attributes.get("aria-label") for e in elements):
            hints.append("Verify accessibility")

        return hints


class SimpleTestGenerator:
    """Simple test generator adapter"""

    def generate(self, formatted_data: dict[str, Any]) -> list[TestCase]:
        """Generate basic test cases"""
        tests = []

        # Generate test for each element type
        for element_type, elements in formatted_data.get("elements_by_type", {}).items():
            for elem in elements:
                test = TestCase(
                    name=f"Test {element_type} - {elem['selector']}",
                    steps=[
                        "Navigate to page",
                        f"Locate element {elem['selector']}",
                        f"Interact with {element_type}",
                        "Verify response",
                    ],
                    expected=[
                        f"{element_type} is visible",
                        f"{element_type} is interactive",
                        "Action completes successfully",
                    ],
                )
                tests.append(test)

        return tests


# ==============================================================================
# LAYER 4: PLUGIN REGISTRY
# ==============================================================================


class PluginRegistry:
    """Central plugin registry - the heart of extensibility"""

    def __init__(self):
        self._registry: dict[str, dict[str, Any]] = defaultdict(dict)
        self._instances: dict[str, Any] = {}

    def register(self, port: str, adapter: Any, name: str = None):
        """Register adapter for a port"""
        adapter_name = name or adapter.__name__
        self._registry[port][adapter_name] = adapter
        print(f"[Registry] Registered {adapter_name} for port {port}")

    def get(self, port: str, name: str = None) -> Any:
        """Get adapter instance (singleton pattern)"""
        # Use default if no name specified
        if not name:
            adapters = self._registry.get(port, {})
            if adapters:
                name = list(adapters.keys())[0]

        cache_key = f"{port}:{name}"

        # Return cached instance
        if cache_key in self._instances:
            return self._instances[cache_key]

        # Create new instance
        adapter_class = self._registry.get(port, {}).get(name)
        if not adapter_class:
            raise ValueError(f"No adapter '{name}' registered for port '{port}'")

        instance = adapter_class()
        self._instances[cache_key] = instance
        return instance

    def list_adapters(self, port: str) -> list[str]:
        """List all adapters for a port"""
        return list(self._registry.get(port, {}).keys())


# ==============================================================================
# LAYER 5: WORKFLOW ORCHESTRATION
# ==============================================================================


class Pipeline:
    """Simple workflow pipeline (simpler than LangGraph for demo)"""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.steps = []

    def add_step(self, name: str, port: str, adapter: str = None):
        """Add step to pipeline"""
        self.steps.append((name, port, adapter))
        return self

    def run(self, initial_data: dict[str, Any]) -> dict[str, Any]:
        """Run pipeline"""
        data = initial_data.copy()

        for step_name, port, adapter in self.steps:
            print(f"\n[Pipeline] Running step: {step_name}")

            # Get adapter from registry
            adapter_instance = self.registry.get(port, adapter)

            # Execute step based on port type
            if port == "extractor":
                data["elements"] = adapter_instance.extract(data["url"])
                print(f"  Extracted {len(data['elements'])} elements")

            elif port == "formatter":
                data["formatted"] = adapter_instance.format(data["elements"])
                print(f"  Formatted for {adapter_instance.format_type}")

            elif port == "generator":
                data["tests"] = adapter_instance.generate(data["formatted"])
                print(f"  Generated {len(data['tests'])} test cases")

        return data


# ==============================================================================
# DEMONSTRATION
# ==============================================================================


def main():
    """Demonstrate the V3 architecture"""

    print("=" * 70)
    print("UI Testing Framework V3 - Hexagonal Plugin Architecture")
    print("=" * 70)

    # 1. Initialize Registry
    print("\n1. INITIALIZING PLUGIN REGISTRY")
    registry = PluginRegistry()

    # 2. Register Adapters (in real app, auto-discovered)
    print("\n2. REGISTERING ADAPTERS")
    registry.register("extractor", SimpleExtractor, "simple")
    registry.register("extractor", QAExtractor, "qa")
    registry.register("formatter", LLMTestFormatter, "llm_test")
    registry.register("generator", SimpleTestGenerator, "simple")

    # 3. Show Available Adapters
    print("\n3. AVAILABLE ADAPTERS")
    for port in ["extractor", "formatter", "generator"]:
        adapters = registry.list_adapters(port)
        print(f"  {port}: {', '.join(adapters)}")

    # 4. Create Pipeline
    print("\n4. CREATING PIPELINE")
    pipeline = Pipeline(registry)
    pipeline.add_step("Extract", "extractor", "qa").add_step(
        "Format", "formatter", "llm_test"
    ).add_step("Generate", "generator", "simple")

    # 5. Run Pipeline
    print("\n5. RUNNING PIPELINE")
    result = pipeline.run({"url": "https://example.com"})

    # 6. Display Results
    print("\n6. RESULTS")
    print(f"\nExtracted Elements ({len(result['elements'])}):")
    for elem in result["elements"]:
        print(f"  - {elem.tag_name}: {elem.selector} (score: {elem.interaction_score:.2f})")

    print("\nFormatted Data:")
    formatted = result["formatted"]
    print(f"  Total elements: {formatted['total_elements']}")
    print(f"  Interactive: {formatted['interactive_elements']}")
    print(f"  Test hints: {', '.join(formatted['test_hints'])}")

    print(f"\nGenerated Tests ({len(result['tests'])}):")
    for test in result["tests"]:
        if test.validate():
            print(f"  [OK] {test.name}")
            print(f"    Steps: {len(test.steps)}")
            print(f"    Expected: {len(test.expected)}")

    # 7. Demonstrate Plugin Switching
    print("\n7. PLUGIN HOT-SWAPPING")
    print("Switching to 'simple' extractor...")

    pipeline2 = Pipeline(registry)
    pipeline2.add_step("Extract", "extractor", "simple").add_step(
        "Format", "formatter", "llm_test"
    ).add_step("Generate", "generator", "simple")

    result2 = pipeline2.run({"url": "https://example.com"})
    print(f"  With simple extractor: {len(result2['elements'])} elements")
    print(f"  With QA extractor: {len(result['elements'])} elements")

    # 8. Key Benefits Demonstrated
    print("\n" + "=" * 70)
    print("KEY BENEFITS DEMONSTRATED:")
    print("=" * 70)
    print("[OK] Zero external dependencies in core domain")
    print("[OK] Plugins can be swapped without changing code")
    print("[OK] Each layer has single responsibility")
    print("[OK] Built-in Python modules for optimization")
    print("[OK] Clean separation of concerns")
    print("[OK] Easy to test (mock at port level)")
    print("[OK] Extensible without modifying core")

    print("\n" + "=" * 70)
    print("This architecture scales to production with:")
    print("- Async/await for performance")
    print("- LangGraph for complex workflows")
    print("- Pydantic for validation")
    print("- TOML configuration")
    print("- Auto-discovery of plugins")
    print("- Event-driven communication")
    print("=" * 70)


if __name__ == "__main__":
    main()
