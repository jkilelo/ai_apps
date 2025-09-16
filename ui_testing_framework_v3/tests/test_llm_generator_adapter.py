import asyncio
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from ui_testing_framework_v3.adapters.generators.llm_based import LLMTestGenerator


def _fake_llm_module() -> SimpleNamespace:
    class Message:  # minimal match to llm.Message
        def __init__(self, role: str, content: str) -> None:
            self.role = role
            self.content = content

    def call_default_llm(*_args: Any, **_kwargs: Any) -> Any:
        # Return object with .content containing JSON tests
        payload: dict[str, Any] = {
            "tests": [
                {
                    "name": "Smoke - button present",
                    "description": "Check buttons",
                    "steps": ["Open page", "Count buttons"],
                    "assertions": ["At least 1 button"],
                    "priority": "high",
                    "tags": ["smoke"],
                }
            ]
        }
        return SimpleNamespace(content=str(payload).replace("'", '"'))

    return SimpleNamespace(Message=Message, call_default_llm=call_default_llm)


def test_llm_generator_parses_output() -> None:
    gen = LLMTestGenerator({"provider": "openai", "model": "gpt-4.1"})

    # Patch module-level llm_mod symbol used by adapter
    with patch("ui_testing_framework_v3.adapters.generators.llm_based.llm_mod", _fake_llm_module()):
        formatted: dict[str, Any] = {"counts": {"button": 3}}

        async def run() -> Any:
            return await gen.generate(formatted)

        tests = asyncio.run(run())

        assert tests
        assert tests[0].validate() is True
