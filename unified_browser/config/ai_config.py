"""
AI/LLM configuration module.

This module defines configuration for AI providers, models, and intelligent features.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core import (
    AGENT_HIERARCHY_LEVELS,
    DEFAULT_LLM_MAX_TOKENS,
    DEFAULT_LLM_TEMPERATURE,
    LLM_PROVIDERS,
    LLM_TIMEOUT,
    LLMProvider,
    MAX_CONVERSATION_HISTORY,
    MAX_LLM_CALLS_PER_MINUTE,
    MULTI_MODAL_ENABLED,
    VISION_LANGUAGE_MODEL,
)


@dataclass
class ModelConfig:
    """Configuration for a specific AI model."""

    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None

    # Model parameters
    temperature: float = DEFAULT_LLM_TEMPERATURE
    max_tokens: int = DEFAULT_LLM_MAX_TOKENS
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # Request settings
    timeout: int = LLM_TIMEOUT
    max_retries: int = 3
    retry_delay_ms: int = 1000

    # Cost tracking
    track_usage: bool = True
    cost_per_1k_tokens: Optional[float] = None
    max_cost_per_session: Optional[float] = None


@dataclass
class VisionConfig:
    """Configuration for vision/image analysis."""

    enabled: bool = MULTI_MODAL_ENABLED
    provider: LLMProvider = LLMProvider.GEMINI
    model_name: str = VISION_LANGUAGE_MODEL

    # Vision settings
    enable_ocr: bool = True
    enable_object_detection: bool = True
    enable_visual_grounding: bool = True

    # Image processing
    max_image_size_mb: int = 10
    resize_large_images: bool = True
    target_resolution: tuple[int, int] = (1920, 1080)
    jpeg_quality: int = 95

    # Analysis settings
    confidence_threshold: float = 0.85
    max_objects_per_image: int = 100
    include_bounding_boxes: bool = True
    include_confidence_scores: bool = True

    # Screenshot settings
    capture_before_action: bool = True
    capture_after_action: bool = True
    capture_on_error: bool = True
    screenshot_format: str = "png"


@dataclass
class AgentConfig:
    """Configuration for AI agents."""

    # Hierarchical agents
    enable_hierarchical_agents: bool = True
    hierarchy_levels: int = AGENT_HIERARCHY_LEVELS

    # Agent types
    enable_planner_agent: bool = True
    enable_executor_agent: bool = True
    enable_verifier_agent: bool = True
    enable_reflector_agent: bool = True

    # Agent coordination
    consensus_required: bool = False
    voting_threshold: float = 0.6
    communication_timeout_ms: int = 5000

    # Agent behavior
    max_planning_steps: int = 10
    max_execution_attempts: int = 3
    enable_self_correction: bool = True
    enable_learning: bool = False

    # Memory
    short_term_memory_size: int = 100
    long_term_memory_enabled: bool = False
    memory_persistence_path: Optional[Path] = None


@dataclass
class PromptConfig:
    """Configuration for prompt engineering."""

    # Prompt strategies
    use_chain_of_thought: bool = True
    use_few_shot: bool = True
    use_role_playing: bool = True
    use_structured_output: bool = True

    # Prompt templates
    system_prompt: Optional[str] = None
    task_prompt_template: Optional[str] = None
    error_prompt_template: Optional[str] = None
    reflection_prompt_template: Optional[str] = None

    # Examples for few-shot
    example_tasks: List[Dict[str, str]] = field(default_factory=list)
    max_examples: int = 5

    # Output formatting
    output_format: str = "json"  # json, markdown, plain
    include_reasoning: bool = True
    include_confidence: bool = True

    # Context management
    max_context_length: int = 4000
    context_compression: bool = True
    preserve_important_context: bool = True


@dataclass
class ConversationConfig:
    """Configuration for conversation management."""

    # History management
    maintain_history: bool = True
    max_history_length: int = MAX_CONVERSATION_HISTORY
    compress_old_messages: bool = True

    # Context window
    sliding_window: bool = True
    window_size: int = 10
    overlap_size: int = 2

    # Memory
    save_conversations: bool = False
    conversation_log_path: Optional[Path] = None

    # Summarization
    auto_summarize: bool = True
    summarize_after_messages: int = 20
    summary_max_length: int = 500

    # Turn management
    max_turns_per_task: int = 10
    allow_clarification: bool = True
    require_confirmation: bool = False


@dataclass
class DecisionConfig:
    """Configuration for autonomous decision making."""

    # Decision making
    autonomous_mode: bool = False
    confidence_threshold: float = 0.8
    require_user_approval: bool = True

    # Risk assessment
    assess_risk: bool = True
    max_risk_level: str = "medium"  # low, medium, high
    risk_factors: List[str] = field(
        default_factory=lambda: ["data_loss", "security", "cost", "irreversible"]
    )

    # Action planning
    plan_before_execute: bool = True
    max_plan_depth: int = 5
    parallel_actions: bool = False

    # Learning
    learn_from_feedback: bool = False
    feedback_weight: float = 0.3
    success_memory_size: int = 100
    failure_memory_size: int = 100


@dataclass
class ProviderAPIConfig:
    """Provider-specific API configuration."""

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    openai_organization: Optional[str] = None

    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_api_base: Optional[str] = None

    # Google/Gemini
    google_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_project_id: Optional[str] = None

    # XAI
    xai_api_key: Optional[str] = None
    xai_api_base: Optional[str] = None

    # Rate limits per provider
    rate_limits: Dict[str, int] = field(
        default_factory=lambda: {
            "openai": 60,
            "anthropic": 50,
            "google": 60,
            "gemini": 60,
            "xai": 30,
        }
    )


@dataclass
class AIConfig:
    """Main AI/LLM configuration."""

    # Primary model
    primary_provider: LLMProvider = LLMProvider.GEMINI
    primary_model: str = "gemini-2.5-flash"

    # Fallback models
    fallback_providers: List[LLMProvider] = field(default_factory=list)
    auto_fallback: bool = True

    # Model configurations
    models: Dict[str, ModelConfig] = field(default_factory=dict)

    # Sub-configurations
    vision: VisionConfig = field(default_factory=VisionConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    prompts: PromptConfig = field(default_factory=PromptConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    decision: DecisionConfig = field(default_factory=DecisionConfig)
    api: ProviderAPIConfig = field(default_factory=ProviderAPIConfig)

    # Global settings
    rate_limit: int = MAX_LLM_CALLS_PER_MINUTE
    cache_responses: bool = True
    cache_ttl_seconds: int = 3600

    @classmethod
    def basic_config(cls) -> AIConfig:
        """Create basic AI configuration."""
        return cls(
            primary_provider=LLMProvider.GEMINI,
            primary_model="gemini-2.5-flash",
            vision=VisionConfig(enabled=False),
            agents=AgentConfig(enable_hierarchical_agents=False),
            decision=DecisionConfig(autonomous_mode=False),
        )

    @classmethod
    def advanced_config(cls) -> AIConfig:
        """Create advanced AI configuration with vision."""
        return cls(
            primary_provider=LLMProvider.GEMINI,
            primary_model="gemini-2.5-flash",
            fallback_providers=[LLMProvider.OPENAI],
            vision=VisionConfig(
                enabled=True,
                enable_ocr=True,
                enable_object_detection=True,
            ),
            agents=AgentConfig(
                enable_hierarchical_agents=True,
                enable_planner_agent=True,
                enable_executor_agent=True,
                enable_verifier_agent=True,
            ),
            prompts=PromptConfig(
                use_chain_of_thought=True,
                use_few_shot=True,
            ),
            conversation=ConversationConfig(
                maintain_history=True,
                auto_summarize=True,
            ),
        )

    @classmethod
    def autonomous_config(cls) -> AIConfig:
        """Create autonomous AI configuration."""
        return cls(
            primary_provider=LLMProvider.GEMINI,
            primary_model="gemini-2.5-pro",
            fallback_providers=[LLMProvider.OPENAI, LLMProvider.ANTHROPIC],
            vision=VisionConfig(
                enabled=True,
                enable_ocr=True,
                enable_object_detection=True,
                enable_visual_grounding=True,
            ),
            agents=AgentConfig(
                enable_hierarchical_agents=True,
                enable_planner_agent=True,
                enable_executor_agent=True,
                enable_verifier_agent=True,
                enable_reflector_agent=True,
                enable_self_correction=True,
                enable_learning=True,
            ),
            prompts=PromptConfig(
                use_chain_of_thought=True,
                use_few_shot=True,
                use_structured_output=True,
                include_reasoning=True,
            ),
            conversation=ConversationConfig(
                maintain_history=True,
                auto_summarize=True,
                save_conversations=True,
            ),
            decision=DecisionConfig(
                autonomous_mode=True,
                plan_before_execute=True,
                assess_risk=True,
                learn_from_feedback=True,
            ),
        )

    def get_model_config(self, provider: LLMProvider) -> Optional[ModelConfig]:
        """Get model configuration for a specific provider."""
        return self.models.get(provider.value)

    def add_model_config(self, config: ModelConfig) -> None:
        """Add a model configuration."""
        self.models[config.provider.value] = config
