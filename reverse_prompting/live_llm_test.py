"""
Live LLM Test for Reverse Prompting Engine

This script integrates the existing _llm.py interface to test the reverse prompting
system with real LLM providers (OpenAI, Gemini, Claude).
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path to import _llm.py
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

try:
    # Import from the actual location
    llm_path = parent_dir / "_llm.py"
    if llm_path.exists():
        import importlib.util

        spec = importlib.util.spec_from_file_location("_llm", llm_path)
        _llm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_llm_module)
        query_llm = _llm_module.query_llm
        print(f"✅ Successfully imported _llm.py from {llm_path}")
    else:
        raise ImportError(f"_llm.py not found at {llm_path}")
except ImportError as e:
    print(f"Error: Could not import _llm.py: {e}")
    print(f"Looking for _llm.py in: {parent_dir}")
    print("Available files:", list(parent_dir.glob("*.py")))
    sys.exit(1)

# Import reverse prompting components
from core.models import CodeArtifact, CodeLanguage, EngineConfig
from utils.llm_interface import BaseLLMProvider, LLMResponse
from engines.reverse_engine import ReversePromptingEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LiveLLMProvider(BaseLLMProvider):
    """
    Live LLM provider that uses the existing _llm.py interface.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = config.get("provider", "openai")
        self.model_name = config.get("model", "gpt-4")

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test if the LLM provider is accessible."""
        try:
            test_messages = [
                {"role": "user", "content": "Hello, respond with just 'OK'"}
            ]
            response = query_llm(self.provider_name, self.model_name, test_messages)
            self.logger.info(
                f"Successfully connected to {self.provider_name} with model {self.model_name}"
            )
        except Exception as e:
            self.logger.warning(f"Connection test failed for {self.provider_name}: {e}")

    async def generate_code(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        language: CodeLanguage = CodeLanguage.PYTHON,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate code using the live LLM interface."""
        import time

        start_time = time.time()

        try:
            # Prepare messages
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                default_system = f"""You are an expert programmer. {self._get_language_instructions(language)}

Generate only the code requested. Do not include explanations unless specifically asked.
Ensure the code is functional, efficient, and follows best practices.
Wrap your code in triple backticks with the language specified."""
                messages.append({"role": "system", "content": default_system})

            messages.append({"role": "user", "content": prompt})

            # Make API call using _llm.py
            response = query_llm(self.provider_name, self.model_name, messages)

            generation_time = time.time() - start_time

            # Extract code from response
            content = response.choices[0].message.content
            code = self._extract_code_block(content)

            return LLMResponse(
                code=code,
                model=self.model_name,
                provider=self.provider_name,
                generation_time=generation_time,
                tokens_used=response.usage.total_tokens if response.usage else None,
                success=True,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": (
                        response.usage.prompt_tokens if response.usage else None
                    ),
                    "completion_tokens": (
                        response.usage.completion_tokens if response.usage else None
                    ),
                },
            )

        except Exception as e:
            generation_time = time.time() - start_time
            self.logger.error(f"{self.provider_name} generation failed: {e}")

            return LLMResponse(
                code="",
                model=self.model_name,
                provider=self.provider_name,
                generation_time=generation_time,
                success=False,
                error=str(e),
            )

    def _extract_code_block(self, content: str) -> str:
        """Extract code from markdown code blocks."""
        if "```" in content:
            # Find the first code block
            lines = content.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                if line.strip().startswith("```") and not in_code_block:
                    in_code_block = True
                    continue
                elif line.strip().startswith("```") and in_code_block:
                    break
                elif in_code_block:
                    code_lines.append(line)

            if code_lines:
                return "\n".join(code_lines)

        # If no code block found, return the entire content
        return content.strip()


class LiveLLMInterface:
    """Custom LLM interface using the live _llm.py providers."""

    def __init__(self):
        self.providers = {}
        self.logger = logging.getLogger(__name__)

        # Initialize available providers
        self._init_providers()

    def _init_providers(self):
        """Initialize available LLM providers."""
        provider_configs = [
            {"provider": "openai", "model": "gpt-4"},
            {"provider": "gemini", "model": "gemini-2.0-flash-exp"},
            {"provider": "claude", "model": "claude-3-5-sonnet-20241022"},
        ]

        for config in provider_configs:
            try:
                provider = LiveLLMProvider(config)
                self.providers[config["provider"]] = provider
                self.logger.info(f"Initialized {config['provider']} provider")
            except Exception as e:
                self.logger.warning(f"Failed to initialize {config['provider']}: {e}")

    async def generate_code(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        language: CodeLanguage = CodeLanguage.PYTHON,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        provider: Optional[str] = None,
        retry_attempts: int = 3,
    ) -> Optional[Dict[str, Any]]:
        """Generate code using the specified or best available provider."""

        # Select provider
        if provider and provider in self.providers:
            selected_provider = self.providers[provider]
        else:
            # Use the first available provider
            if not self.providers:
                self.logger.error("No LLM providers available")
                return None

            selected_provider = next(iter(self.providers.values()))

        # Try generation with retries
        for attempt in range(retry_attempts):
            try:
                response = await selected_provider.generate_code(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    language=language,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                if response.success and response.code.strip():
                    return {
                        "code": response.code,
                        "model": response.model,
                        "provider": response.provider,
                        "generation_time": response.generation_time,
                        "tokens_used": response.tokens_used,
                        "metadata": response.metadata,
                    }
                else:
                    self.logger.warning(
                        f"Generation failed on attempt {attempt + 1}: {response.error}"
                    )

                    # Add delay before retry
                    if attempt < retry_attempts - 1:
                        await asyncio.sleep(2**attempt)  # Exponential backoff

            except Exception as e:
                self.logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(2**attempt)

        return None

    def get_available_providers(self):
        """Get list of available providers."""
        return list(self.providers.keys())


async def test_live_reverse_prompting():
    """Test the reverse prompting system with live LLMs."""
    print("🚀 Starting Live Reverse Prompting Test")
    print("=" * 60)

    # Create a simple code example to reverse prompt
    target_code = CodeArtifact(
        name="fibonacci_example",
        language=CodeLanguage.PYTHON,
        content="""def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number using recursion.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Example usage
if __name__ == "__main__":
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")""",
        description="Recursive Fibonacci implementation with example usage",
    )

    print(f"📝 Target Code ({target_code.language.value}):")
    print("-" * 40)
    print(target_code.content)
    print("-" * 40)

    # Create custom LLM interface
    llm_interface = LiveLLMInterface()
    available_providers = llm_interface.get_available_providers()

    print(f"🔗 Available LLM Providers: {available_providers}")

    if not available_providers:
        print("❌ No LLM providers available. Please check your API keys.")
        return

    # Configure engine with custom LLM interface
    config = EngineConfig(
        max_iterations=3,  # Keep it small for testing
        parallel_strategies=1,
        success_threshold=0.7,
        enable_evolution=False,  # Disable for quicker test
        enable_monitoring=True,
        enable_caching=True,
        storage_backend="sqlite",
        storage_path="./test_data",
    )

    # Create engine with custom LLM interface
    engine = ReversePromptingEngine(config=config, llm_interface=llm_interface)

    try:
        print(
            f"\n🔄 Running Reverse Prompting with {len(available_providers)} provider(s)..."
        )
        print("This may take a few minutes...")

        # Run reverse prompting
        session = await engine.run_reverse_prompting(
            target_code=target_code,
            session_name="live_fibonacci_test",
            target_description="Generate a function that calculates Fibonacci numbers",
        )

        # Display results
        print("\n" + "=" * 60)
        print("✅ REVERSE PROMPTING COMPLETED!")
        print("=" * 60)

        print(f"Session ID: {session.id}")
        print(f"📊 Results Summary:")
        print(f"  • Total prompts generated: {len(session.generated_prompts)}")
        print(f"  • Total artifacts generated: {len(session.generated_artifacts)}")
        print(f"  • Total evaluations: {len(session.evaluations)}")
        print(f"  • Success rate: {session.get_success_rate():.2%}")

        if session.best_result:
            print(f"  • Best score: {session.best_result.overall_score:.3f}")

            # Find the best prompt
            best_prompt = None
            for prompt in session.generated_prompts:
                if str(prompt.id) == session.best_result.prompt_id:
                    best_prompt = prompt
                    break

            if best_prompt:
                print(f"\n🏆 Best Performing Prompt:")
                print(f"Strategy: {best_prompt.strategy.value}")
                print("-" * 40)
                print(
                    best_prompt.content[:500] + "..."
                    if len(best_prompt.content) > 500
                    else best_prompt.content
                )
                print("-" * 40)

            # Find the best generated code
            best_artifact = None
            for artifact in session.generated_artifacts:
                if str(artifact.id) == session.best_result.generated_artifact_id:
                    best_artifact = artifact
                    break

            if best_artifact:
                print(f"\n💎 Best Generated Code:")
                print("-" * 40)
                print(
                    best_artifact.content[:800] + "..."
                    if len(best_artifact.content) > 800
                    else best_artifact.content
                )
                print("-" * 40)

        # Show detailed evaluation metrics
        if session.evaluations:
            print(f"\n📈 Evaluation Details:")
            for i, eval_result in enumerate(session.evaluations[:3]):  # Show top 3
                print(f"  Evaluation #{i+1}:")
                print(f"    • Overall Score: {eval_result.overall_score:.3f}")
                print(f"    • Exact Match: {eval_result.exact_match}")
                print(
                    f"    • Semantic Similarity: {eval_result.semantic_similarity:.3f}"
                )
                print(
                    f"    • Structural Similarity: {eval_result.structural_similarity:.3f}"
                )
                print(
                    f"    • Functional Equivalence: {eval_result.functional_equivalence}"
                )
                if eval_result.notes:
                    print(f"    • Notes: {eval_result.notes[:100]}...")
                print()

        print("🎉 Live test completed successfully!")

    except Exception as e:
        print(f"❌ Error during reverse prompting: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        await engine.cleanup()


async def test_individual_llm_providers():
    """Test each LLM provider individually."""
    print("\n🧪 Testing Individual LLM Providers")
    print("=" * 60)

    llm_interface = LiveLLMInterface()

    test_prompt = """Create a Python function that calculates the factorial of a number using recursion. 
The function should:
1. Take an integer parameter n
2. Return the factorial of n
3. Handle the base case when n is 0 or 1
4. Include proper docstring documentation

Generate only the function code."""

    for provider_name in llm_interface.get_available_providers():
        print(f"\n🔍 Testing {provider_name.upper()}...")
        try:
            result = await llm_interface.generate_code(
                prompt=test_prompt, language=CodeLanguage.PYTHON, provider=provider_name
            )

            if result and result.get("code"):
                print(f"✅ {provider_name} - Success!")
                print(f"   Model: {result.get('model')}")
                print(f"   Generation time: {result.get('generation_time', 0):.2f}s")
                print(f"   Tokens used: {result.get('tokens_used', 'Unknown')}")
                print(f"   Code preview: {result['code'][:150]}...")
            else:
                print(f"❌ {provider_name} - Failed to generate code")

        except Exception as e:
            print(f"❌ {provider_name} - Error: {e}")


async def main():
    """Main test function."""
    print("🚀 LIVE LLM REVERSE PROMPTING TEST")
    print("=" * 80)

    # Check if API keys are available
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Google": os.getenv("GOOGLE_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
    }

    print("🔑 API Key Status:")
    for provider, key in api_keys.items():
        status = "✅ Available" if key else "❌ Missing"
        print(f"  {provider}: {status}")

    if not any(api_keys.values()):
        print("\n⚠️  No API keys found. Please set at least one of:")
        print("   - OPENAI_API_KEY")
        print("   - GOOGLE_API_KEY")
        print("   - ANTHROPIC_API_KEY")
        return

    # Test individual providers first
    await test_individual_llm_providers()

    # Run full reverse prompting test
    await test_live_reverse_prompting()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback

        traceback.print_exc()
