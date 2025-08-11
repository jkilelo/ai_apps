#!/usr/bin/env python3
"""
Simple working example of the Reverse Prompting Engine
This demonstrates basic functionality without requiring API keys
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to import reverse_prompting
sys.path.insert(0, str(Path(__file__).parent.parent))

from reverse_prompting import (
    ReversePromptingEngine,
    CodeArtifact,
    CodeLanguage,
    EngineConfig,
    PromptStrategy,
)


async def simple_example():
    """Simple example without LLM calls"""
    print("🚀 REVERSE PROMPTING ENGINE - SIMPLE EXAMPLE")
    print("=" * 60)

    # Create a simple code artifact
    code = CodeArtifact(
        name="hello_world",
        language=CodeLanguage.PYTHON,
        content='print("Hello, World!")',
        description="A simple hello world program",
    )

    print(f"📝 Created code artifact: {code.name}")
    print(f"💻 Language: {code.language}")
    print(f"📄 Content: {code.content}")
    print(f"🔑 Hash: {code.calculate_hash()[:16]}...")

    # Create engine config
    config = EngineConfig(
        max_iterations=1,
        enable_evolution=False,
        enable_monitoring=True,
        log_level="INFO",
    )

    # Create engine
    engine = ReversePromptingEngine(config=config)

    print(f"\n⚙️  Engine initialized")
    print(f"🗄️  Storage backend: {config.storage_backend}")
    print(f"📊 Monitoring enabled: {config.enable_monitoring}")

    # Start a session
    session_id = await engine.start_session(
        name="simple_example", artifact=code, strategies=[PromptStrategy.ZERO_SHOT]
    )

    print(f"\n🎯 Started session: {session_id}")

    # Get session info
    session = await engine.get_session(session_id)
    if session:
        print(f"📈 Session status: {session.status}")
        print(f"🔢 Generated prompts: {len(session.generated_prompts)}")
        print(f"🏗️  Created artifacts: {len(session.generated_artifacts)}")
        print(f"📊 Evaluations: {len(session.evaluations)}")

    # List all sessions
    sessions = await engine.list_sessions()
    print(f"\n📋 Total sessions stored: {len(sessions)}")

    # Cleanup
    await engine.cleanup()
    print("\n✅ Example completed successfully!")


def main():
    """Main function"""
    try:
        asyncio.run(simple_example())
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
