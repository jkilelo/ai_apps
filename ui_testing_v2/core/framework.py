"""
Main UI Testing Framework v2 class
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4, UUID

from .config import get_config, Config
from .exceptions import UITestingError, ValidationError
from .interfaces import (
    ElementExtractorInterface,
    TestGeneratorInterface,
    CodeGeneratorInterface,
    CodeExecutorInterface,
)
from ..models.common import (
    ElementData,
    TestCase,
    GeneratedCode,
    ExecutionResult,
    BrowserType,
    FrameworkType,
    LanguageType,
)
from ..models.database import TaskStatus, TestSession
from ..services import (
    get_service_container,
    ServiceContainer,
    get_state_manager,
    get_database_manager,
    get_ai_service_factory,
)
from ..services.state_manager import WorkflowDefinition, WorkflowStep

logger = logging.getLogger(__name__)


class WorkflowResult:
    """Workflow execution result"""
    
    def __init__(
        self,
        workflow_id: str,
        session_id: UUID,
        start_time: datetime,
        status: TaskStatus = TaskStatus.PENDING,
        configuration: Optional[Dict[str, Any]] = None,
    ):
        self.workflow_id = workflow_id
        self.session_id = session_id
        self.start_time = start_time
        self.end_time: Optional[datetime] = None
        self.duration: Optional[float] = None
        self.status = status
        self.configuration = configuration or {}
        
        # Results
        self.extraction_result: Optional[Dict[str, Any]] = None
        self.generation_result: Optional[Dict[str, Any]] = None
        self.code_result: Optional[Dict[str, Any]] = None
        self.execution_result: Optional[ExecutionResult] = None
        
        # Counts
        self.total_elements: int = 0
        self.total_test_cases: int = 0
        self.total_code_files: int = 0
        
        # Metadata
        self.metadata: Dict[str, Any] = {}


class UITestingFramework:
    """
    Main UI Testing Framework v2 class
    
    Orchestrates the complete workflow:
    1. Element Extraction
    2. Test Case Generation  
    3. Code Generation
    4. Code Execution
    
    Integrates with:
    - Database for persistence
    - State management for workflow tracking
    - AI services for intelligent analysis
    - Caching for performance
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        service_container: Optional[ServiceContainer] = None,
        element_extractor: Optional[ElementExtractorInterface] = None,
        test_generator: Optional[TestGeneratorInterface] = None,
        code_generator: Optional[CodeGeneratorInterface] = None,
        code_executor: Optional[CodeExecutorInterface] = None,
    ) -> None:
        self.config = config or get_config()
        self.service_container = service_container
        
        # Components will be injected or created with defaults
        self._element_extractor = element_extractor
        self._test_generator = test_generator
        self._code_generator = code_generator
        self._code_executor = code_executor
        
        # Framework state
        self._initialized = False
        self._workflows: Dict[str, WorkflowResult] = {}
        
        logger.info("UI Testing Framework v2 initialized")
    
    async def __aenter__(self) -> "UITestingFramework":
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self) -> None:
        """Initialize the framework and all components"""
        if self._initialized:
            return
        
        logger.info("Initializing UI Testing Framework v2...")
        
        try:
            # Initialize service container if not provided
            if not self.service_container:
                self.service_container = await get_service_container()
            
            # Initialize Phase 1 Day 4 - Element Extraction Component
            from ui_testing_v2.components.element_extraction_component import ElementExtractionComponent
            if not self._element_extractor:
                self._element_extractor = ElementExtractionComponent(
                    self.config,
                    self.service_container.get_database_manager(),
                    self.service_container.get_ai_service_factory(),
                    self.service_container.get_cache_service()
                )
            
            # Initialize Phase 1 Day 5 - Test Case Generation Component
            from ui_testing_v2.components.test_case_generator import TestCaseGenerationComponent
            if not self._test_generator:
                self._test_generator = TestCaseGenerationComponent(
                    self.config,
                    self.service_container.get_ai_service_factory(),
                    self.service_container.get_cache_service(),
                    self.service_container.get_database_manager(),
                    self._element_extractor.element_analysis_service if self._element_extractor else None
                )
            
            # Initialize other components
            if self._element_extractor and hasattr(self._element_extractor, 'initialize'):
                await self._element_extractor.initialize()
            if self._test_generator and hasattr(self._test_generator, 'initialize'):
                await self._test_generator.initialize()
            if self._code_generator and hasattr(self._code_generator, 'initialize'):
                await self._code_generator.initialize()
            if self._code_executor and hasattr(self._code_executor, 'initialize'):
                await self._code_executor.initialize()
            
            self._initialized = True
            logger.info("Framework initialization completed")
            
        except Exception as e:
            logger.error(f"Framework initialization failed: {e}")
            raise UITestingError(f"Framework initialization failed: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup framework resources"""
        if not self._initialized:
            return
        
        logger.info("Cleaning up UI Testing Framework v2...")
        
        try:
            # Cleanup components
            if self._element_extractor and hasattr(self._element_extractor, 'cleanup'):
                await self._element_extractor.cleanup()
            if self._test_generator and hasattr(self._test_generator, 'cleanup'):
                await self._test_generator.cleanup()
            if self._code_generator and hasattr(self._code_generator, 'cleanup'):
                await self._code_generator.cleanup()
            if self._code_executor and hasattr(self._code_executor, 'cleanup'):
                await self._code_executor.cleanup()
            
            self._initialized = False
            logger.info("Framework cleanup completed")
            
        except Exception as e:
            logger.error(f"Framework cleanup failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check framework and component health"""
        health_status = {
            "framework": "healthy",
            "initialized": self._initialized,
            "timestamp": datetime.now().isoformat(),
            "components": {},
        }
        
        try:
            # Check service container health
            if self.service_container:
                health_status["services"] = await self.service_container.health_check()
            
            # Check component health
            if self._element_extractor and hasattr(self._element_extractor, 'health_check'):
                health_status["components"]["element_extractor"] = await self._element_extractor.health_check()
            if self._test_generator and hasattr(self._test_generator, 'health_check'):
                health_status["components"]["test_generator"] = await self._test_generator.health_check()
            if self._code_generator and hasattr(self._code_generator, 'health_check'):
                health_status["components"]["code_generator"] = await self._code_generator.health_check()
            if self._code_executor and hasattr(self._code_executor, 'health_check'):
                health_status["components"]["code_executor"] = await self._code_executor.health_check()
            
        except Exception as e:
            health_status["framework"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def run_complete_workflow(
        self,
        url: str,
        project_id: Optional[UUID] = None,
        session_name: Optional[str] = None,
        test_requirements: Optional[str] = None,
        frameworks: Optional[List[FrameworkType]] = None,
        languages: Optional[List[LanguageType]] = None,
        browsers: Optional[List[BrowserType]] = None,
        **kwargs: Any,
    ) -> WorkflowResult:
        """
        Run the complete testing workflow with database persistence
        
        Args:
            url: Target URL to test
            project_id: Project ID for organization
            session_name: Name for the test session
            test_requirements: Natural language test requirements
            frameworks: Target test frameworks
            languages: Target programming languages
            browsers: Browsers to test on
            **kwargs: Additional configuration
            
        Returns:
            Complete workflow result
        """
        if not self._initialized:
            await self.initialize()
        
        workflow_id = str(uuid4())
        start_time = datetime.now()
        
        logger.info(f"Starting complete workflow {workflow_id} for URL: {url}")
        
        # Create test session in database
        state_manager = await get_state_manager()
        session = await state_manager.session_manager.create_session(
            name=session_name or f"Test Session for {url}",
            url=url,
            project_id=project_id,
            extraction_config={
                "strategies": ["auto", "ai_assisted"],
                "timeout": 30,
            },
            test_config={
                "requirements": test_requirements,
                "frameworks": [f.value for f in frameworks] if frameworks else ["playwright"],
                "languages": [l.value for l in languages] if languages else ["python"],
            },
            ai_config={
                "provider": self.config.ai.default_provider,
                "enable_vision": self.config.ai.enable_vision,
            },
        )
        
        # Initialize workflow result
        workflow_result = WorkflowResult(
            workflow_id=workflow_id,
            session_id=session.id,
            start_time=start_time,
            status=TaskStatus.RUNNING,
            configuration={
                "url": url,
                "test_requirements": test_requirements,
                "frameworks": frameworks,
                "languages": languages,
                "browsers": browsers,
                **kwargs,
            },
        )
        
        self._workflows[workflow_id] = workflow_result
        
        # Start session
        await state_manager.session_manager.start_session(
            session.id,
            initial_step="element_extraction"
        )
        
        try:
            # Create workflow definition
            workflow_def = self._create_workflow_definition(
                url, session.id, test_requirements, frameworks, languages, browsers, **kwargs
            )
            
            # Execute workflow using state manager
            await state_manager.workflow_manager.create_workflow(
                workflow_id=workflow_id,
                definition=workflow_def,
                config=workflow_result.configuration,
            )
            
            await state_manager.workflow_manager.start_workflow(
                workflow_id=workflow_id,
                definition=workflow_def,
                context={
                    "session_id": str(session.id),
                    "url": url,
                    "workflow_result": workflow_result,
                },
            )
            
            # Wait for workflow completion (in a real implementation, this would be async)
            # For now, we'll execute steps sequentially
            workflow_result = await self._execute_workflow_steps(
                workflow_result, session.id, url, test_requirements, frameworks, languages, browsers, **kwargs
            )
            
            # Complete session
            await state_manager.session_manager.complete_session(
                session.id,
                results={
                    "workflow_id": workflow_id,
                    "total_elements": workflow_result.total_elements,
                    "total_test_cases": workflow_result.total_test_cases,
                    "total_code_files": workflow_result.total_code_files,
                }
            )
            
            logger.info(f"Workflow {workflow_id} completed successfully in {workflow_result.duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            workflow_result.status = TaskStatus.FAILED
            workflow_result.end_time = datetime.now()
            workflow_result.duration = (workflow_result.end_time - start_time).total_seconds()
            workflow_result.metadata["error"] = str(e)
            
            # Fail session
            await state_manager.session_manager.fail_session(
                session.id,
                error_message=str(e),
                error_details={"workflow_id": workflow_id}
            )
            
            raise UITestingError(f"Workflow execution failed: {e}")
        
        return workflow_result
    
    def _create_workflow_definition(
        self,
        url: str,
        session_id: UUID,
        test_requirements: Optional[str],
        frameworks: Optional[List[FrameworkType]],
        languages: Optional[List[LanguageType]],
        browsers: Optional[List[BrowserType]],
        **kwargs: Any,
    ) -> WorkflowDefinition:
        """Create workflow definition with steps"""
        
        async def extract_elements_step(context: Dict[str, Any]) -> List[ElementData]:
            return await self.extract_elements(url, session_id=session_id, **kwargs)
        
        async def generate_tests_step(context: Dict[str, Any]) -> List[TestCase]:
            elements = context.get("step_1_result", [])
            return await self.generate_test_cases(elements, session_id, test_requirements, **kwargs)
        
        async def generate_code_step(context: Dict[str, Any]) -> List[GeneratedCode]:
            test_cases = context.get("step_2_result", [])
            frameworks_list = frameworks or [FrameworkType.PLAYWRIGHT]
            languages_list = languages or [LanguageType.PYTHON]
            
            generated_codes = []
            for framework in frameworks_list:
                for language in languages_list:
                    code = await self.generate_code(test_cases, framework, language, **kwargs)
                    generated_codes.append(code)
            return generated_codes
        
        async def execute_tests_step(context: Dict[str, Any]) -> ExecutionResult:
            generated_codes = context.get("step_3_result", [])
            if generated_codes:
                return await self.execute_tests(generated_codes[0], browsers, **kwargs)
            raise ValueError("No generated code available for execution")
        
        steps = [
            WorkflowStep(
                name="extract_elements",
                description="Extract UI elements from webpage",
                action=extract_elements_step,
                timeout=300,
                retry_count=2,
            ),
            WorkflowStep(
                name="generate_test_cases",
                description="Generate test cases from elements",
                action=generate_tests_step,
                timeout=300,
                retry_count=1,
            ),
            WorkflowStep(
                name="generate_code",
                description="Generate test code",
                action=generate_code_step,
                timeout=300,
                retry_count=1,
            ),
            WorkflowStep(
                name="execute_tests",
                description="Execute generated tests",
                action=execute_tests_step,
                timeout=600,
                retry_count=1,
            ),
        ]
        
        return WorkflowDefinition(
            name="complete_ui_testing_workflow",
            description="Complete UI testing workflow with element extraction, test generation, code generation, and execution",
            steps=steps,
            timeout=1800,  # 30 minutes
        )
    
    async def _execute_workflow_steps(
        self,
        workflow_result: WorkflowResult,
        session_id: UUID,
        url: str,
        test_requirements: Optional[str],
        frameworks: Optional[List[FrameworkType]],
        languages: Optional[List[LanguageType]],
        browsers: Optional[List[BrowserType]],
        **kwargs: Any,
    ) -> WorkflowResult:
        """Execute workflow steps and update results"""
        state_manager = await get_state_manager()
        
        # Step 1: Element Extraction
        await state_manager.session_manager.update_session_progress(
            session_id, 25, "extracting_elements"
        )
        elements = await self.extract_elements(url, session_id=session_id, **kwargs)
        workflow_result.extraction_result = {
            "elements_count": len(elements),
            "completed_at": datetime.now().isoformat(),
        }
        workflow_result.total_elements = len(elements)
        
        # Step 2: Test Case Generation
        await state_manager.session_manager.update_session_progress(
            session_id, 50, "generating_test_cases"
        )
        test_cases = await self.generate_test_cases(elements, session_id, test_requirements, **kwargs)
        workflow_result.generation_result = {
            "test_cases_count": len(test_cases),
            "completed_at": datetime.now().isoformat(),
        }
        workflow_result.total_test_cases = len(test_cases)
        
        # Step 3: Code Generation
        await state_manager.session_manager.update_session_progress(
            session_id, 75, "generating_code"
        )
        frameworks = frameworks or [FrameworkType.PLAYWRIGHT]
        languages = languages or [LanguageType.PYTHON]
        
        generated_codes = []
        for framework in frameworks:
            for language in languages:
                code = await self.generate_code(test_cases, framework, language, **kwargs)
                generated_codes.append(code)
        
        workflow_result.code_result = {
            "generated_codes_count": len(generated_codes),
            "frameworks": [f.value for f in frameworks],
            "languages": [l.value for l in languages],
            "completed_at": datetime.now().isoformat(),
        }
        workflow_result.total_code_files = len(generated_codes)
        
        # Step 4: Code Execution
        await state_manager.session_manager.update_session_progress(
            session_id, 90, "executing_tests"
        )
        browsers = browsers or [BrowserType.CHROMIUM]
        
        if generated_codes:
            execution_result = await self.execute_tests(generated_codes[0], browsers, **kwargs)
            workflow_result.execution_result = execution_result
        
        # Complete workflow
        await state_manager.session_manager.update_session_progress(
            session_id, 100, "completed"
        )
        
        end_time = datetime.now()
        workflow_result.end_time = end_time
        workflow_result.duration = (end_time - workflow_result.start_time).total_seconds()
        workflow_result.status = TaskStatus.COMPLETED
        
        return workflow_result
    
    async def extract_elements(
        self,
        url: str,
        session_id: Optional[UUID] = None,
        strategies: Optional[List[str]] = None,
        browser: Optional[BrowserType] = None,
        **kwargs: Any,
    ) -> List[ElementData]:
        """Extract elements from a webpage"""
        if not self._element_extractor:
            # Create default element extractor using AI services
            from ..components.element_extraction import AIElementExtractor
            ai_factory = await get_ai_service_factory()
            self._element_extractor = AIElementExtractor(
                ai_service_factory=ai_factory,
                config=self.config.browser.dict()
            )
            await self._element_extractor.initialize()
        
        if not url:
            raise ValidationError("URL is required for element extraction")
        
        try:
            elements = await self._element_extractor.extract_elements(
                url=url,
                strategies=strategies or ["auto", "ai_assisted"],
                browser=browser or BrowserType.CHROMIUM,
                **kwargs,
            )
            
            # Store elements in database if session_id is provided
            if session_id and elements:
                db_manager = await get_database_manager()
                from ..services.database import ElementRepository
                element_repo = ElementRepository(db_manager)
                
                element_data_list = []
                for element in elements:
                    element_data_list.append(element.dict())
                
                await element_repo.save_elements(session_id, element_data_list)
            
            logger.info(f"Extracted {len(elements)} elements from {url}")
            return elements
            
        except Exception as e:
            logger.error(f"Element extraction failed for {url}: {e}")
            raise UITestingError(f"Element extraction failed: {e}")
    
    async def generate_test_cases(
        self,
        elements: List[ElementData],
        session_id: Optional[UUID] = None,
        requirements: Optional[str] = None,
        test_types: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[TestCase]:
        """Generate test cases from extracted elements"""
        if not self._test_generator:
            # Create default test generator using AI services
            from ..components.test_generation import AITestGenerator
            ai_factory = await get_ai_service_factory()
            prompt_manager = self.service_container.get_prompt_manager()
            self._test_generator = AITestGenerator(
                ai_service_factory=ai_factory,
                prompt_manager=prompt_manager,
                config=self.config.testing.dict()
            )
            await self._test_generator.initialize()
        
        if not elements:
            raise ValidationError("Elements are required for test generation")
        
        try:
            test_cases = await self._test_generator.generate_test_cases(
                elements=elements,
                requirements=requirements,
                test_types=test_types or ["functional", "ui"],
                **kwargs,
            )
            
            # Store test cases in database if session_id is provided
            if session_id and test_cases:
                db_manager = await get_database_manager()
                async with db_manager.get_session() as db_session:
                    for test_case in test_cases:
                        from ..models.database import TestCase as DBTestCase
                        db_test_case = DBTestCase(
                            session_id=session_id,
                            name=test_case.name,
                            description=test_case.description,
                            test_type=test_case.test_type,
                            steps=test_case.steps,
                            expected_results=test_case.expected_results,
                            test_data=test_case.test_data,
                            ai_prompt_used=getattr(test_case, 'ai_prompt_used', None),
                            ai_provider=self.config.ai.default_provider,
                        )
                        db_session.add(db_test_case)
                    await db_session.commit()
            
            logger.info(f"Generated {len(test_cases)} test cases from {len(elements)} elements")
            return test_cases
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            raise UITestingError(f"Test generation failed: {e}")
    
    async def generate_code(
        self,
        test_cases: List[TestCase],
        framework: FrameworkType,
        language: LanguageType,
        **kwargs: Any,
    ) -> GeneratedCode:
        """Generate test code for a specific framework and language"""
        if not self._code_generator:
            # Create default code generator using AI services
            from ..components.code_generation import AICodeGenerator
            ai_factory = await get_ai_service_factory()
            prompt_manager = self.service_container.get_prompt_manager()
            self._code_generator = AICodeGenerator(
                ai_service_factory=ai_factory,
                prompt_manager=prompt_manager,
                config={}
            )
            await self._code_generator.initialize()
        
        if not test_cases:
            raise ValidationError("Test cases are required for code generation")
        
        try:
            generated_code = await self._code_generator.generate_code(
                test_cases=test_cases,
                framework=framework,
                language=language,
                **kwargs,
            )
            logger.info(f"Generated {framework.value} code in {language.value} for {len(test_cases)} test cases")
            return generated_code
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise UITestingError(f"Code generation failed: {e}")
    
    async def execute_tests(
        self,
        generated_code: GeneratedCode,
        browsers: Optional[List[BrowserType]] = None,
        parallel: bool = True,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute generated test code"""
        if not self._code_executor:
            # Create default code executor
            from ..components.code_execution import PlaywrightExecutor
            self._code_executor = PlaywrightExecutor(
                config=self.config.browser.dict()
            )
            await self._code_executor.initialize()
        
        if not generated_code:
            raise ValidationError("Generated code is required for execution")
        
        try:
            execution_result = await self._code_executor.execute_tests(
                generated_code=generated_code,
                browsers=browsers or [BrowserType.CHROMIUM],
                parallel=parallel,
                **kwargs,
            )
            logger.info(f"Executed tests with {execution_result.success_rate:.1f}% success rate")
            return execution_result
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            raise UITestingError(f"Test execution failed: {e}")
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowResult]:
        """Get workflow result by ID"""
        return self._workflows.get(workflow_id)
    
    def list_workflows(self) -> List[WorkflowResult]:
        """List all workflow results"""
        return list(self._workflows.values())
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return False
        
        if workflow.status == TaskStatus.RUNNING:
            workflow.status = TaskStatus.CANCELLED
            workflow.end_time = datetime.now()
            if workflow.start_time:
                workflow.duration = (workflow.end_time - workflow.start_time).total_seconds()
            
            # Cancel workflow in state manager
            if self.service_container:
                state_manager = self.service_container.get_state_manager()
                await state_manager.workflow_manager.cancel_workflow(workflow_id)
            
            logger.info(f"Workflow {workflow_id} cancelled")
            return True
        
        return False
    
    async def get_session_data(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        """Get comprehensive session data including elements and test cases"""
        try:
            db_manager = await get_database_manager()
            from ..services.database import SessionRepository, ElementRepository
            
            session_repo = SessionRepository(db_manager)
            element_repo = ElementRepository(db_manager)
            
            # Get session details
            session = await session_repo.get_session(session_id)
            if not session:
                return None
            
            # Get associated elements
            elements = await element_repo.get_session_elements(session_id)
            
            # Get test cases
            async with db_manager.get_session() as db_session:
                from sqlmodel import select
                from ..models.database import TestCase as DBTestCase
                result = await db_session.execute(
                    select(DBTestCase).where(DBTestCase.session_id == session_id)
                )
                test_cases = result.scalars().all()
            
            return {
                "session": {
                    "id": str(session.id),
                    "name": session.name,
                    "url": session.url,
                    "status": session.status,
                    "progress_percentage": session.progress_percentage,
                    "current_step": session.current_step,
                    "created_at": session.created_at.isoformat(),
                    "started_at": session.started_at.isoformat() if session.started_at else None,
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                    "execution_duration": session.execution_duration,
                },
                "elements": [
                    {
                        "id": str(element.id),
                        "tag_name": element.tag_name,
                        "element_type": element.element_type,
                        "text_content": element.text_content,
                        "is_clickable": element.is_clickable,
                        "is_form_field": element.is_form_field,
                        "css_selector": element.css_selector,
                        "ai_description": element.ai_description,
                        "confidence_score": element.confidence_score,
                    }
                    for element in elements
                ],
                "test_cases": [
                    {
                        "id": str(test_case.id),
                        "name": test_case.name,
                        "description": test_case.description,
                        "test_type": test_case.test_type,
                        "priority": test_case.priority,
                        "steps": test_case.steps,
                        "is_executable": test_case.is_executable,
                    }
                    for test_case in test_cases
                ],
                "summary": {
                    "total_elements": len(elements),
                    "total_test_cases": len(test_cases),
                    "clickable_elements": len([e for e in elements if e.is_clickable]),
                    "form_elements": len([e for e in elements if e.is_form_field]),
                }
            }
        
        except Exception as e:
            logger.error(f"Failed to get session data for {session_id}: {e}")
            return None
