"""Enhanced ReAct Orchestrator with proper reasoning patterns and self-correction"""

from typing import Dict, Any, List, Optional, Literal, Union
from pydantic import BaseModel, Field
from loguru import logger
from playwright.async_api import Page
import time
import asyncio
from enum import Enum

from cognition.llm import ILLMProvider
from cognition.agents import PlannerAgent, SelfCorrectingBrowserAgent, BrowserAgent
from cognition.actions import AgentAction, FinishedAction, FailedAction
from cognition.prompts import PromptBuilder
from perception.state_observer import StateObserver
from perception.models import WebPageState


class ReasoningType(str, Enum):
    """Types of reasoning patterns"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    SELF_CONSISTENCY = "self_consistency"
    DIRECT = "direct"


class ReActStep(BaseModel):
    """Single step in ReAct loop"""
    step_number: int = Field(..., description="Step number in the loop")
    thought: str = Field(..., description="Reasoning about current state")
    action: Optional[AgentAction] = Field(None, description="Action to take")
    observation: Optional[str] = Field(None, description="Observation from action")
    reflection: Optional[str] = Field(None, description="Reflection on outcome")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in this step")
    timestamp: float = Field(default_factory=time.time)


class ReActSession(BaseModel):
    """Complete ReAct reasoning session"""
    task: str = Field(..., description="The task being executed")
    steps: List[ReActStep] = Field(default_factory=list, description="All reasoning steps")
    final_result: Optional[Dict[str, Any]] = Field(None, description="Final execution result")
    total_iterations: int = Field(default=0, description="Total iterations performed")
    success: bool = Field(default=False, description="Whether task succeeded")
    reasoning_type: ReasoningType = Field(default=ReasoningType.CHAIN_OF_THOUGHT)
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = Field(None)
    
    @property
    def duration(self) -> float:
        """Get session duration in seconds"""
        end = self.end_time or time.time()
        return end - self.start_time


class ReActConfig(BaseModel):
    """Configuration for ReAct orchestrator"""
    max_reasoning_iterations: int = Field(default=5, ge=1, le=20)
    self_correction_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    action_confidence_required: float = Field(default=0.8, ge=0.0, le=1.0)
    enable_chain_of_thought: bool = Field(default=True)
    enable_tree_of_thoughts: bool = Field(default=False)
    enable_self_consistency: bool = Field(default=False)
    reflection_trigger_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    max_correction_attempts: int = Field(default=3, ge=1, le=10)
    observation_timeout_ms: int = Field(default=5000, ge=1000, le=30000)


class AgentOrchestrator:
    """Enhanced ReAct Orchestrator with proper reasoning patterns and self-correction"""
    
    def __init__(
        self, 
        llm_provider: ILLMProvider, 
        config: Optional[ReActConfig] = None,
        enable_self_correction: bool = True
    ):
        self.llm = llm_provider
        self.config = config or ReActConfig()
        self.planner = PlannerAgent(llm_provider)
        self.state_observer = StateObserver()
        self.prompt_builder = PromptBuilder()
        
        if enable_self_correction:
            self.browser_agent = SelfCorrectingBrowserAgent(
                llm_provider,
                max_corrections=self.config.max_correction_attempts
            )
        else:
            self.browser_agent = BrowserAgent(llm_provider)
        
        self.enable_self_correction = enable_self_correction
        self.current_session: Optional[ReActSession] = None
        self.conversation_history: List[Dict[str, Any]] = []
        
    async def execute_task_with_react(
        self,
        page: Page,
        task: str,
        context: Optional[List[Dict]] = None,
        reasoning_type: ReasoningType = ReasoningType.CHAIN_OF_THOUGHT
    ) -> Dict[str, Any]:
        """Execute task using ReAct loop with proper reasoning patterns"""
        logger.info(f"Starting ReAct execution for task: {task}")
        
        # Initialize session
        self.current_session = ReActSession(
            task=task,
            reasoning_type=reasoning_type
        )
        
        try:
            if reasoning_type == ReasoningType.TREE_OF_THOUGHTS and self.config.enable_tree_of_thoughts:
                return await self._execute_with_tree_of_thoughts(page, task, context)
            elif reasoning_type == ReasoningType.SELF_CONSISTENCY and self.config.enable_self_consistency:
                return await self._execute_with_self_consistency(page, task, context)
            else:
                return await self._execute_with_chain_of_thought(page, task, context)
                
        except Exception as e:
            logger.error(f"ReAct execution failed: {e}")
            self.current_session.success = False
            self.current_session.end_time = time.time()
            return self._format_failure_result(str(e))
        finally:
            if self.current_session:
                self.current_session.end_time = time.time()
                self._save_session_to_history()
    
    async def _execute_with_chain_of_thought(
        self,
        page: Page,
        task: str,
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Execute using Chain-of-Thought reasoning"""
        logger.debug("Using Chain-of-Thought reasoning pattern")
        
        for iteration in range(self.config.max_reasoning_iterations):
            logger.debug(f"ReAct iteration {iteration + 1}/{self.config.max_reasoning_iterations}")
            
            # THOUGHT: Reason about current state
            thought = await self._generate_thought(page, task, context)
            confidence = await self._calculate_thought_confidence(thought)
            
            step = ReActStep(
                step_number=iteration + 1,
                thought=thought,
                confidence=confidence
            )
            
            logger.info(f"Thought: {step.thought[:200]}...")
            
            # Check if we should reflect on low confidence
            if step.confidence < self.config.reflection_trigger_threshold:
                step.reflection = await self._generate_reflection(step.thought, "low_confidence")
                logger.warning(f"Low confidence reflection: {step.reflection[:200]}...")
            
            # ACTION: Decide what to do
            action_result = await self._generate_action(step.thought, page, task)
            if not action_result["success"]:
                step.observation = f"Failed to generate action: {action_result['error']}"
                self.current_session.steps.append(step)
                continue
            
            step.action = action_result["action"]
            
            # Check action confidence
            if step.action.confidence < self.config.action_confidence_required:
                logger.warning(f"Low action confidence: {step.action.confidence}")
                if self.enable_self_correction:
                    correction_result = await self._attempt_action_correction(step, page, task)
                    if correction_result["success"]:
                        step.action = correction_result["corrected_action"]
                    else:
                        step.observation = f"Action correction failed: {correction_result['error']}"
                        self.current_session.steps.append(step)
                        continue
            
            # Check if task is complete
            if isinstance(step.action, FinishedAction):
                step.observation = "Task completed successfully"
                self.current_session.steps.append(step)
                self.current_session.success = True
                return self._format_success_result(step.action)
            
            # Check if task failed
            if isinstance(step.action, FailedAction):
                step.observation = f"Task failed: {step.action.reason}"
                self.current_session.steps.append(step)
                return self._format_failure_result(step.action.reason)
            
            # OBSERVATION: Execute action and observe result
            observation_result = await self._execute_and_observe(step.action, page)
            step.observation = observation_result["observation"]
            
            # REFLECTION: Evaluate outcome
            if not observation_result["success"]:
                step.reflection = await self._generate_reflection(
                    step.thought, 
                    "action_failed",
                    {"action": step.action, "error": observation_result["error"]}
                )
                
                if self.enable_self_correction:
                    correction_result = await self._attempt_error_correction(
                        step, page, task, observation_result["error"]
                    )
                    if correction_result["success"]:
                        step.observation += f" | Correction applied: {correction_result['correction']}"
            
            self.current_session.steps.append(step)
            self.current_session.total_iterations += 1
            
            # Small delay between iterations
            await asyncio.sleep(0.1)
        
        # Max iterations reached
        return self._format_failure_result("Maximum reasoning iterations reached")
    
    async def _execute_with_tree_of_thoughts(
        self,
        page: Page,
        task: str,
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Execute using Tree-of-Thoughts reasoning (simplified implementation)"""
        logger.debug("Using Tree-of-Thoughts reasoning pattern")
        
        # Generate multiple reasoning paths
        reasoning_paths = await self._generate_multiple_thoughts(page, task, context, num_paths=3)
        
        # Evaluate and select best path
        best_path = await self._select_best_reasoning_path(reasoning_paths)
        
        # Execute selected path
        return await self._execute_reasoning_path(page, task, best_path)
    
    async def _execute_with_self_consistency(
        self,
        page: Page,
        task: str,
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Execute using Self-Consistency reasoning"""
        logger.debug("Using Self-Consistency reasoning pattern")
        
        # Generate multiple solutions
        solutions = []
        for i in range(3):
            solution = await self._execute_with_chain_of_thought(page, task, context)
            solutions.append(solution)
        
        # Vote on best solution
        return await self._vote_on_best_solution(solutions)
    
    async def execute_complex_task(
        self, 
        page: Page, 
        user_query: str,
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complex task by decomposing and executing sub-tasks (legacy method)
        This method now uses the enhanced ReAct loop internally
        
        Args:
            page: Playwright page
            user_query: Natural language user request
            context: Optional context from memory
            
        Returns:
            Execution results
        """
        logger.info(f"Orchestrator executing complex task: {user_query}")
        
        # Create plan
        try:
            plan = await self.planner.create_plan(user_query)
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {
                "query": user_query,
                "success": False,
                "error": f"Planning failed: {str(e)}",
                "plan": [],
                "results": []
            }
        
        # Execute sub-tasks using ReAct loop
        results = []
        overall_success = True
        
        for i, sub_task in enumerate(plan.sub_tasks, 1):
            logger.info(f"Executing sub-task {i}/{len(plan.sub_tasks)}: {sub_task}")
            
            try:
                # Execute sub-task with ReAct
                result = await self.execute_task_with_react(
                    page=page,
                    task=sub_task,
                    context=context,
                    reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
                )
                
                results.append({
                    "sub_task": sub_task,
                    "success": result.get("success", False),
                    "summary": result.get("summary", ""),
                    "error": result.get("error"),
                    "iterations": result.get("iterations", 0),
                    "corrections": result.get("corrections_made", 0) if self.enable_self_correction else 0,
                    "reasoning_steps": result.get("reasoning_steps", []),
                    "confidence": result.get("confidence", 0.0)
                })
                
                # Check if we should continue
                if not result.get("success"):
                    logger.warning(f"Sub-task failed: {sub_task}")
                    
                    # Determine if this is a critical failure
                    if self._is_critical_failure(sub_task, plan.sub_tasks):
                        logger.error("Critical sub-task failed, stopping execution")
                        overall_success = False
                        break
                    else:
                        logger.info("Non-critical failure, continuing with remaining tasks")
                        
            except Exception as e:
                logger.error(f"Sub-task execution failed: {e}")
                results.append({
                    "sub_task": sub_task,
                    "success": False,
                    "error": str(e),
                    "iterations": 0
                })
                
                if self._is_critical_failure(sub_task, plan.sub_tasks):
                    overall_success = False
                    break
        
        # Compile final results with enhanced data
        return {
            "query": user_query,
            "plan": plan.sub_tasks,
            "results": results,
            "overall_success": overall_success and all(r["success"] for r in results),
            "completed_tasks": sum(1 for r in results if r["success"]),
            "total_tasks": len(plan.sub_tasks),
            "context_used": context is not None,
            "reasoning_type": "chain_of_thought",
            "session_duration": sum(r.get("duration", 0) for r in results),
            "total_reasoning_steps": sum(len(r.get("reasoning_steps", [])) for r in results)
        }
    
    def _is_critical_failure(self, failed_task: str, all_tasks: List[str]) -> bool:
        """
        Determine if a task failure is critical
        
        Args:
            failed_task: The task that failed
            all_tasks: All tasks in the plan
            
        Returns:
            True if failure is critical and should stop execution
        """
        # Navigation and authentication tasks are usually critical
        critical_keywords = ["navigate", "login", "authenticate", "sign in", "access"]
        
        failed_lower = failed_task.lower()
        for keyword in critical_keywords:
            if keyword in failed_lower:
                return True
        
        # First task is usually critical
        if all_tasks and failed_task == all_tasks[0]:
            return True
        
        return False
    
    async def _generate_thought(
        self,
        page: Page,
        task: str,
        context: Optional[List[Dict]] = None
    ) -> str:
        """Generate reasoning thought about current state"""
        # Get current page state
        perception_result = await self.state_observer.observe(
            page,
            capture_screenshot=True,
            annotate_visuals=True
        )
        
        if not perception_result.success or not perception_result.state:
            return "Cannot perceive current page state to reason about next steps."
        
        state = perception_result.state
        
        # Build reasoning prompt
        prompt = self.prompt_builder.build_reasoning_prompt(
            task=task,
            current_state=state,
            conversation_history=self.conversation_history[-3:],  # Last 3 exchanges
            reasoning_steps=[step.model_dump() for step in self.current_session.steps[-2:]] if self.current_session else []  # Last 2 steps converted to dicts
        )
        
        try:
            thought = await self.llm.generate_text(prompt)
            return thought.strip()
        except Exception as e:
            logger.error(f"Failed to generate thought: {e}")
            return f"Unable to generate reasoning due to error: {str(e)}"
    
    async def _calculate_thought_confidence(self, thought: str) -> float:
        """Calculate confidence in the reasoning thought"""
        # Simple heuristics for confidence calculation
        confidence = 0.5  # Base confidence
        
        # Boost confidence for specific patterns
        if "I need to" in thought or "I should" in thought:
            confidence += 0.2
        if "because" in thought or "since" in thought:
            confidence += 0.1
        if "then" in thought or "next" in thought:
            confidence += 0.1
        if len(thought.split()) > 20:  # Detailed reasoning
            confidence += 0.1
        
        # Reduce confidence for uncertainty indicators
        if "maybe" in thought or "might" in thought or "possibly" in thought:
            confidence -= 0.2
        if "not sure" in thought or "unclear" in thought:
            confidence -= 0.3
        
        return max(0.0, min(1.0, confidence))
    
    async def _generate_action(
        self,
        thought: str,
        page: Page,
        task: str
    ) -> Dict[str, Any]:
        """Generate action based on reasoning thought"""
        # Get current page state for action generation
        perception_result = await self.state_observer.observe(
            page,
            capture_screenshot=True,
            annotate_visuals=True
        )
        
        if not perception_result.success or not perception_result.state:
            return {"success": False, "error": "Cannot perceive page state for action generation"}
        
        state = perception_result.state
        
        # Build action generation prompt
        prompt = self.prompt_builder.build_action_prompt(
            task=task,
            reasoning=thought,
            state=state,
            history=[step.model_dump() for step in self.current_session.steps[-3:]] if self.current_session else []
        )
        
        try:
            action = await self.llm.generate_structured(
                prompt=prompt,
                output_model=AgentAction
            )
            return {"success": True, "action": action}
        except Exception as e:
            logger.error(f"Failed to generate action: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_and_observe(
        self,
        action: AgentAction,
        page: Page
    ) -> Dict[str, Any]:
        """Execute action and observe the result"""
        try:
            # Get current state before action
            pre_state = await self.state_observer.observe(page, capture_screenshot=False)
            
            # Execute action through browser agent
            execution_result = await self.browser_agent.dispatcher.dispatch(
                action=action,
                page=page,
                element_map=pre_state.state.element_map if pre_state.success else {}
            )
            
            # Wait for page to settle
            await asyncio.sleep(0.5)
            
            # Observe result
            post_state = await self.state_observer.observe(page, capture_screenshot=False)
            
            if execution_result.success:
                observation = f"Action '{action.action}' executed successfully."
                if hasattr(action, 'justification'):
                    observation += f" Reason: {action.justification}"
                if execution_result.data:
                    observation += f" Result: {execution_result.data}"
                    
                return {"success": True, "observation": observation}
            else:
                error_msg = execution_result.error or "Unknown execution error"
                observation = f"Action '{action.action}' failed: {error_msg}"
                return {"success": False, "observation": observation, "error": error_msg}
                
        except Exception as e:
            logger.error(f"Failed to execute and observe action: {e}")
            return {
                "success": False,
                "observation": f"Execution failed with exception: {str(e)}",
                "error": str(e)
            }
    
    async def _generate_reflection(
        self,
        thought: str,
        trigger_reason: Literal["low_confidence", "action_failed", "unexpected_result"],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate reflection on reasoning or action outcome"""
        prompt = f"""
        Current reasoning: {thought}
        
        Reflection trigger: {trigger_reason}
        """
        
        if additional_context:
            prompt += f"\nAdditional context: {additional_context}"
        
        prompt += """
        
        Reflect on what might be going wrong and how to improve:
        1. Is the reasoning sound?
        2. Are there missing considerations?
        3. What alternative approaches might work better?
        4. What should be adjusted for the next attempt?
        
        Reflection:
        """
        
        try:
            reflection = await self.llm.generate_text(prompt)
            return reflection.strip()
        except Exception as e:
            logger.error(f"Failed to generate reflection: {e}")
            return f"Unable to reflect due to error: {str(e)}"
    
    async def _attempt_action_correction(
        self,
        step: ReActStep,
        page: Page,
        task: str
    ) -> Dict[str, Any]:
        """Attempt to correct low-confidence action"""
        correction_prompt = f"""
        Task: {task}
        Current reasoning: {step.thought}
        Proposed action: {step.action.model_dump() if step.action else 'None'}
        Action confidence: {step.action.confidence if step.action else 0.0}
        
        The proposed action has low confidence. Please provide a corrected action with better confidence.
        Consider:
        1. Is the target element correct?
        2. Is the action type appropriate?
        3. Are there alternative approaches?
        
        Provide a corrected action:
        """
        
        try:
            corrected_action = await self.llm.generate_structured(
                prompt=correction_prompt,
                output_model=AgentAction
            )
            
            if corrected_action.confidence > step.action.confidence:
                return {"success": True, "corrected_action": corrected_action}
            else:
                return {"success": False, "error": "Correction did not improve confidence"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _attempt_error_correction(
        self,
        step: ReActStep,
        page: Page,
        task: str,
        error: str
    ) -> Dict[str, Any]:
        """Attempt to correct action execution error"""
        correction_prompt = f"""
        Task: {task}
        Failed action: {step.action.model_dump() if step.action else 'None'}
        Error: {error}
        
        The action failed to execute. Suggest a correction strategy:
        1. What might have caused the failure?
        2. How can we adjust our approach?
        3. What should we try differently?
        
        Provide correction strategy:
        """
        
        try:
            correction = await self.llm.generate_text(correction_prompt)
            return {"success": True, "correction": correction.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Placeholder methods for advanced reasoning patterns
    async def _generate_multiple_thoughts(
        self, page: Page, task: str, context: Optional[List[Dict]], num_paths: int = 3
    ) -> List[str]:
        """Generate multiple reasoning paths for Tree-of-Thoughts"""
        thoughts = []
        for i in range(num_paths):
            thought = await self._generate_thought(page, task, context)
            thoughts.append(thought)
        return thoughts
    
    async def _select_best_reasoning_path(self, paths: List[str]) -> str:
        """Select best reasoning path from multiple options"""
        # Simple implementation - return first path
        # In production, this would involve more sophisticated evaluation
        return paths[0] if paths else ""
    
    async def _execute_reasoning_path(
        self, page: Page, task: str, reasoning_path: str
    ) -> Dict[str, Any]:
        """Execute a specific reasoning path"""
        # Simplified - delegate to chain of thought
        return await self._execute_with_chain_of_thought(page, task, None)
    
    async def _vote_on_best_solution(self, solutions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Vote on best solution from multiple attempts"""
        # Simple voting - return first successful solution
        for solution in solutions:
            if solution.get("success"):
                return solution
        return solutions[0] if solutions else self._format_failure_result("No solutions generated")
    
    def _format_success_result(self, finished_action: FinishedAction) -> Dict[str, Any]:
        """Format successful task result"""
        return {
            "success": True,
            "summary": finished_action.summary,
            "extracted_data": finished_action.extracted_data,
            "iterations": self.current_session.total_iterations if self.current_session else 0,
            "reasoning_steps": [step.model_dump() for step in self.current_session.steps] if self.current_session else [],
            "duration": self.current_session.duration if self.current_session else 0.0,
            "confidence": finished_action.confidence,
            "reasoning_type": self.current_session.reasoning_type.value if self.current_session else "unknown"
        }
    
    def _format_failure_result(self, error: str) -> Dict[str, Any]:
        """Format failed task result"""
        return {
            "success": False,
            "error": error,
            "iterations": self.current_session.total_iterations if self.current_session else 0,
            "reasoning_steps": [step.model_dump() for step in self.current_session.steps] if self.current_session else [],
            "duration": self.current_session.duration if self.current_session else 0.0,
            "reasoning_type": self.current_session.reasoning_type.value if self.current_session else "unknown"
        }
    
    def _save_session_to_history(self):
        """Save current ReAct session to conversation history"""
        if self.current_session:
            session_summary = {
                "task": self.current_session.task,
                "success": self.current_session.success,
                "duration": self.current_session.duration,
                "steps_count": len(self.current_session.steps),
                "reasoning_type": self.current_session.reasoning_type.value,
                "timestamp": self.current_session.start_time
            }
            self.conversation_history.append(session_summary)
            
            # Keep only last 10 sessions
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about ReAct sessions"""
        if not self.conversation_history:
            return {"total_sessions": 0, "success_rate": 0.0, "avg_duration": 0.0}
        
        total_sessions = len(self.conversation_history)
        successful_sessions = sum(1 for session in self.conversation_history if session["success"])
        success_rate = successful_sessions / total_sessions
        avg_duration = sum(session["duration"] for session in self.conversation_history) / total_sessions
        
        return {
            "total_sessions": total_sessions,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "successful_sessions": successful_sessions
        }
    
    def update_config(self, new_config: ReActConfig):
        """Update ReAct configuration"""
        self.config = new_config
        logger.info(f"Updated ReAct config: {self.config.model_dump()}")
    
    async def reset(self):
        """Reset orchestrator state"""
        await self.browser_agent.reset()
        self.current_session = None
        self.conversation_history = []
        logger.info("AgentOrchestrator state reset")