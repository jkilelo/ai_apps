"""
Main Reverse Prompting Engine

This module implements the core reverse prompting engine that orchestrates the
entire process: analyzing code, generating prompts, creating new code, and
evaluating results.
"""

import asyncio
import time
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from uuid import uuid4
import json
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.models import (
    CodeArtifact,
    PromptGeneration,
    ReversePromptingSession,
    EvaluationResult,
    StateSnapshot,
    EngineConfig,
    PromptStrategy,
    CodeLanguage,
    ExecutionStatus,
    VersionInfo,
)
from ..strategies.prompt_strategies import get_strategy, list_available_strategies
from ..evaluation.evaluators import ComprehensiveEvaluator
from ..storage.session_storage import SessionStorage
from ..utils.llm_interface import LLMInterface
from ..utils.code_executor import CodeExecutor
from ..utils.monitoring import PerformanceMonitor


class ReversePromptingEngine:
    """
    Main engine for reverse prompting operations.

    This engine coordinates the entire reverse prompting workflow:
    1. Analyze input code
    2. Generate prompts using various strategies
    3. Create new code using LLMs
    4. Evaluate similarity and functionality
    5. Evolve and improve prompts
    6. Manage state and persistence
    """

    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        storage: Optional[SessionStorage] = None,
        llm_interface: Optional[LLMInterface] = None,
        code_executor: Optional[CodeExecutor] = None,
    ):
        self.config = config or EngineConfig()
        self.storage = storage or SessionStorage(self.config)
        self.llm_interface = llm_interface or LLMInterface(self.config)
        self.code_executor = code_executor or CodeExecutor(self.config)

        self.evaluator = ComprehensiveEvaluator()
        self.monitor = PerformanceMonitor() if self.config.enable_monitoring else None

        # Internal state
        self.active_sessions: Dict[str, ReversePromptingSession] = {}
        self.strategy_performance: Dict[PromptStrategy, List[float]] = {}
        self.evolution_history: Dict[str, List[Dict[str, Any]]] = {}

        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=getattr(logging, self.config.log_level))

        self.logger.info("Reverse Prompting Engine initialized")

    async def run_reverse_prompting(
        self,
        target_code: CodeArtifact,
        session_name: str,
        target_description: Optional[str] = None,
        strategies: Optional[List[PromptStrategy]] = None,
        max_iterations: Optional[int] = None,
    ) -> ReversePromptingSession:
        """
        Run the complete reverse prompting process.

        Args:
            target_code: The original code to reverse-engineer prompts for
            session_name: Name for this reverse prompting session
            target_description: Description of what the code should do
            strategies: List of prompting strategies to use
            max_iterations: Maximum number of iterations per strategy

        Returns:
            Complete reverse prompting session with results
        """
        if self.monitor:
            self.monitor.start_operation("reverse_prompting")

        try:
            # Create new session
            session = ReversePromptingSession(
                name=session_name,
                original_artifact=target_code,
                target_description=target_description or "Generate equivalent code",
                session_config={
                    "max_iterations": max_iterations or self.config.max_iterations,
                    "strategies": [
                        s.value for s in (strategies or list_available_strategies())
                    ],
                    "timestamp": datetime.now().isoformat(),
                },
            )

            self.active_sessions[str(session.id)] = session
            self.logger.info(f"Started reverse prompting session: {session_name}")

            # Save initial state
            await self._save_state_snapshot(session, "session_created")

            # Run strategies
            strategies_to_use = strategies or list_available_strategies()
            session.strategies_used = strategies_to_use

            # Execute strategies in parallel if configured
            if self.config.parallel_strategies > 1:
                await self._run_strategies_parallel(session, strategies_to_use)
            else:
                await self._run_strategies_sequential(session, strategies_to_use)

            # Evolution phase if enabled
            if self.config.enable_evolution and session.evaluations:
                await self._evolve_prompts(session)

            # Final analysis and selection
            await self._finalize_session(session)

            # Save final state
            await self._save_state_snapshot(session, "session_completed")
            await self.storage.save_session(session)

            self.logger.info(f"Completed reverse prompting session: {session_name}")
            return session

        except Exception as e:
            self.logger.error(
                f"Error in reverse prompting session {session_name}: {str(e)}"
            )
            raise
        finally:
            if self.monitor:
                self.monitor.end_operation("reverse_prompting")

    async def _run_strategies_parallel(
        self, session: ReversePromptingSession, strategies: List[PromptStrategy]
    ):
        """Run multiple strategies in parallel."""
        max_workers = min(self.config.parallel_strategies, len(strategies))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all strategy tasks
            futures = {
                executor.submit(self._run_single_strategy, session, strategy): strategy
                for strategy in strategies
            }

            # Process completed strategies
            for future in as_completed(futures):
                strategy = futures[future]
                try:
                    await future.result()
                    self.logger.info(f"Completed strategy: {strategy.value}")
                except Exception as e:
                    self.logger.error(f"Strategy {strategy.value} failed: {str(e)}")

    async def _run_strategies_sequential(
        self, session: ReversePromptingSession, strategies: List[PromptStrategy]
    ):
        """Run strategies one after another."""
        for strategy in strategies:
            try:
                await self._run_single_strategy(session, strategy)
                self.logger.info(f"Completed strategy: {strategy.value}")
            except Exception as e:
                self.logger.error(f"Strategy {strategy.value} failed: {str(e)}")
                continue

    async def _run_single_strategy(
        self, session: ReversePromptingSession, strategy_type: PromptStrategy
    ):
        """Run a single prompting strategy."""
        strategy = get_strategy(strategy_type)
        max_iterations = session.session_config.get(
            "max_iterations", self.config.max_iterations
        )

        best_score = 0.0
        no_improvement_count = 0

        for iteration in range(max_iterations):
            try:
                # Generate prompt
                prompt_generation = strategy.generate_prompt(
                    session.original_artifact,
                    context={
                        "iteration": iteration,
                        "best_score_so_far": best_score,
                        "session_id": str(session.id),
                    },
                )

                session.generated_prompts.append(prompt_generation)

                # Generate code using LLM
                generated_code = await self._generate_code_from_prompt(
                    prompt_generation, session.original_artifact.language
                )

                if generated_code:
                    session.generated_artifacts.append(generated_code)

                    # Evaluate the generated code
                    evaluation = await self._evaluate_generated_code(
                        session.original_artifact, generated_code, prompt_generation.id
                    )

                    session.add_evaluation(evaluation)

                    # Track performance
                    self._update_strategy_performance(
                        strategy_type, evaluation.overall_score
                    )

                    # Check for improvement
                    if evaluation.overall_score > best_score:
                        best_score = evaluation.overall_score
                        no_improvement_count = 0

                        # Early termination if we reach success threshold
                        if evaluation.overall_score >= self.config.success_threshold:
                            self.logger.info(
                                f"Strategy {strategy_type.value} reached success threshold"
                            )
                            break
                    else:
                        no_improvement_count += 1

                        # Early termination if no improvement for several iterations
                        if no_improvement_count >= 3:
                            self.logger.info(
                                f"Strategy {strategy_type.value} stopped improving"
                            )
                            break

                # Save intermediate state
                if iteration % 5 == 0:
                    await self._save_state_snapshot(
                        session, f"strategy_{strategy_type.value}_iteration_{iteration}"
                    )

            except Exception as e:
                self.logger.error(
                    f"Error in iteration {iteration} of {strategy_type.value}: {str(e)}"
                )
                continue

    async def _generate_code_from_prompt(
        self, prompt_generation: PromptGeneration, target_language: CodeLanguage
    ) -> Optional[CodeArtifact]:
        """Generate code using LLM based on the prompt."""
        try:
            # Use the LLM interface to generate code
            response = await self.llm_interface.generate_code(
                prompt=prompt_generation.content,
                system_prompt=prompt_generation.system_prompt,
                language=target_language,
                max_tokens=self.config.max_prompt_length,
            )

            if response and response.get("code"):
                return CodeArtifact(
                    name=f"generated_{prompt_generation.id.hex[:8]}",
                    language=target_language,
                    content=response["code"],
                    description=f"Generated using {prompt_generation.strategy.value}",
                    metadata={
                        "prompt_id": str(prompt_generation.id),
                        "strategy": prompt_generation.strategy.value,
                        "llm_model": response.get("model", "unknown"),
                        "generation_time": response.get("generation_time", 0.0),
                    },
                )

        except Exception as e:
            self.logger.error(f"Failed to generate code from prompt: {str(e)}")
            return None

    async def _evaluate_generated_code(
        self, original: CodeArtifact, generated: CodeArtifact, prompt_id: str
    ) -> EvaluationResult:
        """Evaluate the generated code against the original."""
        try:
            # Use comprehensive evaluator
            evaluation = self.evaluator.evaluate(original, generated, prompt_id)

            # Add execution comparison if possible
            if self.code_executor:
                original_exec = await self.code_executor.execute(original)
                generated_exec = await self.code_executor.execute(generated)

                evaluation.execution_comparison = {
                    "original_status": (
                        original_exec.status.value if original_exec else "failed"
                    ),
                    "generated_status": (
                        generated_exec.status.value if generated_exec else "failed"
                    ),
                    "both_successful": (
                        original_exec
                        and original_exec.is_successful
                        and generated_exec
                        and generated_exec.is_successful
                    ),
                }

                # Update functional equivalence based on execution
                if evaluation.execution_comparison["both_successful"]:
                    evaluation.functional_equivalence = True

            return evaluation

        except Exception as e:
            self.logger.error(f"Failed to evaluate generated code: {str(e)}")
            # Return minimal evaluation result
            return EvaluationResult(
                original_artifact_id=original.id,
                generated_artifact_id=generated.id,
                prompt_id=prompt_id,
                overall_score=0.0,
                success=False,
                notes=f"Evaluation failed: {str(e)}",
            )

    async def _evolve_prompts(self, session: ReversePromptingSession):
        """Evolve prompts using genetic algorithm principles."""
        if not session.evaluations:
            return

        self.logger.info("Starting prompt evolution phase")

        # Get best performing prompts
        best_evaluations = sorted(
            session.evaluations, key=lambda e: e.overall_score, reverse=True
        )[: self.config.population_size // 2]

        # Evolution iterations
        for generation in range(self.config.evolution_generations):
            new_prompts = []

            # Mutation: modify best prompts
            for eval_result in best_evaluations:
                original_prompt = next(
                    (
                        p
                        for p in session.generated_prompts
                        if p.id == eval_result.prompt_id
                    ),
                    None,
                )
                if original_prompt:
                    mutated = await self._mutate_prompt(original_prompt, session)
                    if mutated:
                        new_prompts.append(mutated)

            # Crossover: combine good prompts
            for i in range(0, len(best_evaluations) - 1, 2):
                eval1, eval2 = best_evaluations[i], best_evaluations[i + 1]
                prompt1 = next(
                    (p for p in session.generated_prompts if p.id == eval1.prompt_id),
                    None,
                )
                prompt2 = next(
                    (p for p in session.generated_prompts if p.id == eval2.prompt_id),
                    None,
                )

                if prompt1 and prompt2:
                    crossover = await self._crossover_prompts(prompt1, prompt2, session)
                    if crossover:
                        new_prompts.append(crossover)

            # Evaluate new prompts
            for new_prompt in new_prompts:
                generated_code = await self._generate_code_from_prompt(
                    new_prompt, session.original_artifact.language
                )

                if generated_code:
                    session.generated_artifacts.append(generated_code)
                    session.generated_prompts.append(new_prompt)

                    evaluation = await self._evaluate_generated_code(
                        session.original_artifact, generated_code, new_prompt.id
                    )

                    session.add_evaluation(evaluation)

            self.logger.info(f"Completed evolution generation {generation + 1}")

    async def _mutate_prompt(
        self, original_prompt: PromptGeneration, session: ReversePromptingSession
    ) -> Optional[PromptGeneration]:
        """Create a mutated version of a prompt."""
        if random.random() > self.config.mutation_rate:
            return None

        # Simple mutation: add variation instructions
        mutation_instructions = [
            "Focus more on code efficiency and optimization.",
            "Emphasize code readability and documentation.",
            "Add more error handling and edge case consideration.",
            "Include more specific implementation details.",
            "Consider alternative algorithmic approaches.",
        ]

        mutation = random.choice(mutation_instructions)
        mutated_content = f"{original_prompt.content}\n\nAdditional focus: {mutation}"

        return PromptGeneration(
            template_id=original_prompt.template_id,
            strategy=original_prompt.strategy,
            content=mutated_content,
            system_prompt=original_prompt.system_prompt,
            target_artifact_id=original_prompt.target_artifact_id,
            variables=original_prompt.variables,
            metadata={
                **original_prompt.metadata,
                "mutation": mutation,
                "parent_prompt": str(original_prompt.id),
            },
        )

    async def _crossover_prompts(
        self,
        prompt1: PromptGeneration,
        prompt2: PromptGeneration,
        session: ReversePromptingSession,
    ) -> Optional[PromptGeneration]:
        """Create a crossover of two prompts."""
        if random.random() > self.config.crossover_rate:
            return None

        # Simple crossover: combine content from both prompts
        crossover_content = f"{prompt1.content[:len(prompt1.content)//2]}\n{prompt2.content[len(prompt2.content)//2:]}"

        return PromptGeneration(
            template_id=prompt1.template_id,
            strategy=prompt1.strategy,
            content=crossover_content,
            system_prompt=prompt1.system_prompt or prompt2.system_prompt,
            target_artifact_id=prompt1.target_artifact_id,
            variables={**prompt1.variables, **prompt2.variables},
            metadata={
                "crossover": True,
                "parent_prompts": [str(prompt1.id), str(prompt2.id)],
            },
        )

    async def _finalize_session(self, session: ReversePromptingSession):
        """Finalize the session with analysis and recommendations."""
        if not session.evaluations:
            return

        # Sort evaluations by score
        session.evaluations.sort(key=lambda e: e.overall_score, reverse=True)

        # Update best result (should already be set, but ensure consistency)
        session.best_result = session.evaluations[0]

        # Calculate final metrics
        success_rate = session.get_success_rate()
        avg_score = sum(e.overall_score for e in session.evaluations) / len(
            session.evaluations
        )

        # Generate session summary
        session.session_config.update(
            {
                "final_success_rate": success_rate,
                "average_score": avg_score,
                "best_score": session.best_result.overall_score,
                "total_prompts": len(session.generated_prompts),
                "total_artifacts": len(session.generated_artifacts),
                "total_evaluations": len(session.evaluations),
                "completion_time": datetime.now().isoformat(),
            }
        )

        self.logger.info(
            f"Session finalized - Success rate: {success_rate:.2%}, Best score: {session.best_result.overall_score:.3f}"
        )

    def _update_strategy_performance(self, strategy: PromptStrategy, score: float):
        """Update performance tracking for a strategy."""
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = []

        self.strategy_performance[strategy].append(score)

        # Keep only recent performance data
        if len(self.strategy_performance[strategy]) > 100:
            self.strategy_performance[strategy] = self.strategy_performance[strategy][
                -100:
            ]

    async def _save_state_snapshot(
        self, session: ReversePromptingSession, state_type: str
    ):
        """Save a state snapshot for recovery purposes."""
        if not self.config.enable_caching:
            return

        snapshot_data = {
            "session": session.dict(),
            "timestamp": datetime.now().isoformat(),
            "state_type": state_type,
        }

        snapshot = StateSnapshot.create(
            session_id=session.id, state_type=state_type, data=snapshot_data
        )

        await self.storage.save_state_snapshot(snapshot)

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a session."""
        session = self.active_sessions.get(session_id)
        if not session:
            # Try loading from storage
            session = await self.storage.load_session(session_id)

        if not session:
            return None

        return {
            "id": str(session.id),
            "name": session.name,
            "status": "active" if session_id in self.active_sessions else "completed",
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "strategies_used": [s.value for s in session.strategies_used],
            "total_prompts": len(session.generated_prompts),
            "total_evaluations": len(session.evaluations),
            "best_score": (
                session.best_result.overall_score if session.best_result else 0.0
            ),
            "success_rate": session.get_success_rate(),
        }

    async def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions."""
        sessions = await self.storage.list_sessions(limit)
        return [
            {
                "id": str(session.id),
                "name": session.name,
                "created_at": session.created_at.isoformat(),
                "best_score": (
                    session.best_result.overall_score if session.best_result else 0.0
                ),
                "success_rate": session.get_success_rate(),
            }
            for session in sessions
        ]

    async def get_strategy_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics for all strategies."""
        performance = {}

        for strategy, scores in self.strategy_performance.items():
            if scores:
                performance[strategy.value] = {
                    "average_score": sum(scores) / len(scores),
                    "max_score": max(scores),
                    "min_score": min(scores),
                    "success_rate": sum(
                        1 for s in scores if s >= self.config.success_threshold
                    )
                    / len(scores),
                    "total_runs": len(scores),
                }

        return performance

    async def cleanup(self):
        """Cleanup resources and save state."""
        self.logger.info("Cleaning up Reverse Prompting Engine")

        # Save any active sessions
        for session in self.active_sessions.values():
            await self.storage.save_session(session)

        # Cleanup storage
        if hasattr(self.storage, "cleanup"):
            await self.storage.cleanup()

        # Cleanup LLM interface
        if hasattr(self.llm_interface, "cleanup"):
            await self.llm_interface.cleanup()

        self.active_sessions.clear()
        self.logger.info("Cleanup completed")


# For easy importing
__all__ = ["ReversePromptingEngine"]
