"""Browser and planning agents for task execution"""

from typing import List, Dict, Any, Optional
from loguru import logger
import time

from cognition.llm import ILLMProvider
from cognition.actions import (
    AgentAction, FinishedAction, FailedAction,
    ClickAction, TypeAction, NavigateAction,
    TaskDecomposition
)
from cognition.prompts import PromptBuilder
from cognition.dispatcher import ActionDispatcher
from perception.state_observer import StateObserver
from perception.models import WebPageState
from playwright.async_api import Page


class BrowserAgent:
    """Basic browser agent that executes tasks using ReAct loop"""
    
    def __init__(self, llm_provider: ILLMProvider, max_iterations: int = 30):
        self.llm = llm_provider
        self.max_iterations = max_iterations
        self.state_observer = StateObserver()
        self.dispatcher = ActionDispatcher()
        self.prompt_builder = PromptBuilder()
        self.history: List[Dict[str, Any]] = []
        
    async def execute_task(self, page: Page, task: str) -> Dict[str, Any]:
        """
        Execute a task using ReAct loop
        
        Args:
            page: Playwright page
            task: Task description
            
        Returns:
            Execution result dictionary
        """
        self.history = []
        
        for iteration in range(self.max_iterations):
            logger.debug(f"Browser agent iteration {iteration + 1}/{self.max_iterations}")
            
            # Observe current state
            perception_result = await self.state_observer.observe(
                page,
                capture_screenshot=True,
                annotate_visuals=True
            )
            
            if not perception_result.success or not perception_result.state:
                logger.error("Failed to observe page state")
                return {
                    "success": False,
                    "error": "Failed to perceive page state",
                    "iterations": iteration + 1
                }
            
            state = perception_result.state
            
            # Build prompt
            prompt = self.prompt_builder.build_react_prompt(
                task=task,
                state=state,
                history=self.history
            )
            
            # Get action from LLM
            try:
                action = await self.llm.generate_structured(
                    prompt=prompt,
                    output_model=AgentAction
                )
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return {
                    "success": False,
                    "error": f"LLM generation failed: {str(e)}",
                    "iterations": iteration + 1
                }
            
            logger.info(f"Action: {action.action} - {action.justification}")
            
            # Check if finished
            if isinstance(action, FinishedAction):
                return {
                    "success": True,
                    "summary": action.summary,
                    "extracted_data": action.extracted_data,
                    "iterations": iteration + 1,
                    "history": self.history
                }
            
            # Check if failed
            if isinstance(action, FailedAction):
                return {
                    "success": False,
                    "error": action.reason,
                    "error_type": action.error_type,
                    "suggestions": action.suggestions,
                    "iterations": iteration + 1,
                    "history": self.history
                }
            
            # Execute action
            result = await self.dispatcher.dispatch(
                action=action,
                page=page,
                element_map=state.element_map
            )
            
            # Record in history
            self.history.append({
                "iteration": iteration + 1,
                "state_url": state.metadata.url,
                "action": action.model_dump(),
                "result": {
                    "success": result.success,
                    "error": result.error,
                    "data": result.data
                }
            })
            
            # Wait a bit to let page update
            if result.success:
                await page.wait_for_timeout(500)
        
        # Max iterations reached
        return {
            "success": False,
            "error": "Maximum iterations reached",
            "iterations": self.max_iterations,
            "history": self.history
        }
    
    async def reset(self):
        """Reset agent state"""
        self.history = []
        self.dispatcher.reset_stats()


class PlannerAgent:
    """High-level planning agent that decomposes tasks"""
    
    def __init__(self, llm_provider: ILLMProvider):
        self.llm = llm_provider
        self.prompt_builder = PromptBuilder()
        
    async def create_plan(self, user_query: str) -> TaskDecomposition:
        """
        Decompose a complex user query into sub-tasks
        
        Args:
            user_query: Natural language user request
            
        Returns:
            TaskDecomposition with ordered sub-tasks
        """
        prompt = self.prompt_builder.build_planner_prompt(user_query)
        
        try:
            plan = await self.llm.generate_structured(
                prompt=prompt,
                output_model=TaskDecomposition
            )
            
            logger.info(f"Created plan with {len(plan.sub_tasks)} sub-tasks")
            for i, task in enumerate(plan.sub_tasks, 1):
                logger.debug(f"  {i}. {task}")
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            # Return simple plan with original task
            return TaskDecomposition(
                main_task=user_query,
                sub_tasks=[user_query]
            )


class SelfCorrectingBrowserAgent(BrowserAgent):
    """Browser agent with self-correction capabilities"""
    
    def __init__(self, llm_provider: ILLMProvider, max_iterations: int = 30,
                 max_corrections: int = 3):
        super().__init__(llm_provider, max_iterations)
        self.max_corrections = max_corrections
        self.correction_count = 0
        self.error_history: List[Dict[str, Any]] = []
        
    async def execute_task(self, page: Page, task: str) -> Dict[str, Any]:
        """Execute task with self-correction on errors"""
        self.history = []
        self.error_history = []
        self.correction_count = 0
        
        for iteration in range(self.max_iterations):
            logger.debug(f"Self-correcting agent iteration {iteration + 1}/{self.max_iterations}")
            
            # Observe current state
            perception_result = await self.state_observer.observe(
                page,
                capture_screenshot=True,
                annotate_visuals=True
            )
            
            if not perception_result.success or not perception_result.state:
                logger.error("Failed to observe page state")
                return {
                    "success": False,
                    "error": "Failed to perceive page state",
                    "iterations": iteration + 1
                }
            
            state = perception_result.state
            
            # Build prompt (with correction if needed)
            base_prompt = self.prompt_builder.build_react_prompt(
                task=task,
                state=state,
                history=self.history
            )
            
            # Add correction context if we had recent errors
            if self.error_history and self.correction_count < self.max_corrections:
                last_error = self.error_history[-1]
                prompt = self.prompt_builder.build_correction_prompt(
                    base_prompt=base_prompt,
                    error_info=last_error
                )
            else:
                prompt = base_prompt
            
            # Get action from LLM
            try:
                action = await self.llm.generate_structured(
                    prompt=prompt,
                    output_model=AgentAction
                )
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return {
                    "success": False,
                    "error": f"LLM generation failed: {str(e)}",
                    "iterations": iteration + 1
                }
            
            logger.info(f"Action: {action.action} - {action.justification}")
            
            # Check if finished
            if isinstance(action, FinishedAction):
                return {
                    "success": True,
                    "summary": action.summary,
                    "extracted_data": action.extracted_data,
                    "iterations": iteration + 1,
                    "history": self.history,
                    "corrections_made": self.correction_count
                }
            
            # Check if failed
            if isinstance(action, FailedAction):
                return {
                    "success": False,
                    "error": action.reason,
                    "error_type": action.error_type,
                    "suggestions": action.suggestions,
                    "iterations": iteration + 1,
                    "history": self.history,
                    "corrections_made": self.correction_count
                }
            
            # Execute action
            result = await self.dispatcher.dispatch(
                action=action,
                page=page,
                element_map=state.element_map
            )
            
            # Record in history
            self.history.append({
                "iteration": iteration + 1,
                "state_url": state.metadata.url,
                "action": action.model_dump(),
                "result": {
                    "success": result.success,
                    "error": result.error,
                    "data": result.data
                }
            })
            
            # Handle errors for self-correction
            if not result.success:
                self.error_history.append({
                    "action_type": action.action,
                    "target": getattr(action, 'element_id', None) or getattr(action, 'url', 'unknown'),
                    "error_type": "execution_failure",
                    "error_message": result.error or "Unknown error"
                })
                self.correction_count += 1
                logger.warning(f"Action failed, attempting correction {self.correction_count}/{self.max_corrections}")
            else:
                # Reset correction count on success
                if self.correction_count > 0:
                    logger.info("Action succeeded after correction")
                self.correction_count = 0
            
            # Wait a bit to let page update
            if result.success:
                await page.wait_for_timeout(500)
        
        # Max iterations reached
        return {
            "success": False,
            "error": "Maximum iterations reached",
            "iterations": self.max_iterations,
            "history": self.history,
            "corrections_made": self.correction_count
        }