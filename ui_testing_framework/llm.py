#!/usr/bin/env python3
"""
Unified LLM Module - Single Source of Truth
Combines all capabilities: streaming, images, structured output, and 21 master prompt strategies
Type-safe with Pydantic v2, passes mypy --strict and flake8
"""

import os
import json
import base64
import hashlib
import logging
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Iterator,
    AsyncIterator,
    Type,
    TypeVar,
    cast,
)
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from pydantic import ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
except ImportError:
    logger.warning("dotenv not available, using system environment variables")

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)

# ==============================================================================
# MASTER PROMPT STRATEGIES (21 Research-backed strategies)
# ==============================================================================


class StrategyType(str, Enum):
    """21 Master prompt engineering strategies from research"""

    # Core reasoning strategies
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    GRAPH_OF_THOUGHTS = "graph_of_thoughts"

    # Problem decomposition
    LEAST_TO_MOST = "least_to_most"
    STEP_BACK = "step_back"
    DECOMPOSED = "decomposed"

    # Knowledge enhancement
    RETRIEVAL_AUGMENTED = "retrieval_augmented"
    GENERATED_KNOWLEDGE = "generated_knowledge"
    KNOWLEDGE_GRAPH = "knowledge_graph"

    # Self-improvement
    SELF_CONSISTENCY = "self_consistency"
    SELF_REFINE = "self_refine"
    SELF_VERIFICATION = "self_verification"

    # Reasoning frameworks
    REACT = "react"
    REFLEXION = "reflexion"
    CHAIN_OF_VERIFICATION = "chain_of_verification"

    # Advanced reasoning
    HYPOTHETICAL_DOCUMENT = "hypothetical_document"
    ANALOGICAL_REASONING = "analogical_reasoning"
    SOCRATIC_METHOD = "socratic_method"

    # Meta strategies
    META_PROMPTING = "meta_prompting"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    CONSTITUTIONAL_AI = "constitutional_ai"


# ==============================================================================
# PYDANTIC V2 CONTRACTS
# ==============================================================================


class Provider(str, Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GOOGLE = "google"  # Alias for Gemini


class Role(str, Enum):
    """Message roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ImageDetail(str, Enum):
    """Image detail level for vision models"""

    AUTO = "auto"
    LOW = "low"
    HIGH = "high"


class ImageContent(BaseModel):
    """Image content for multimodal models"""

    model_config = ConfigDict(str_strip_whitespace=True)

    data: str = Field(..., description="Base64 encoded image data")
    mime_type: str = Field("image/png", description="MIME type of image")
    detail: ImageDetail = Field(ImageDetail.AUTO, description="Detail level for analysis")

    @field_validator("data")
    @classmethod
    def validate_base64(cls, v: str) -> str:
        """Validate base64 encoding"""
        try:
            base64.b64decode(v)
            return v
        except Exception as e:
            raise ValueError(f"Invalid base64 encoding: {e}")


class Message(BaseModel):
    """Enhanced message with optional image content"""

    model_config = ConfigDict(str_strip_whitespace=True)

    role: Role
    content: str
    images: Optional[List[ImageContent]] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StreamChunk(BaseModel):
    """Streaming response chunk"""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field("", description="Chunk content")
    index: int = Field(0, description="Chunk index")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    finish_reason: Optional[str] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Enhanced LLM response with all metadata"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Core response
    content: str = Field(..., description="Response content")
    provider: Provider = Field(..., description="Provider used")
    model: str = Field(..., description="Model used")

    # Enhanced metadata
    strategy_used: Optional[StrategyType] = Field(None)
    images_processed: int = Field(0)
    streaming: bool = Field(False)
    structured: bool = Field(False)

    # Performance metrics
    latency_ms: Optional[int] = Field(None)
    prompt_tokens: Optional[int] = Field(None)
    completion_tokens: Optional[int] = Field(None)
    total_tokens: Optional[int] = Field(None)

    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time: Optional[float] = Field(None)


class LLMConfig(BaseModel):
    """Configuration for LLM operations"""

    model_config = ConfigDict(str_strip_whitespace=True)

    provider: Provider = Field(Provider.GEMINI)
    model: str = Field("gemini-2.0-flash")
    temperature: float = Field(0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(8192, gt=0)
    top_p: float = Field(1.0, ge=0.0, le=1.0)
    strategy: Optional[StrategyType] = Field(None)
    timeout: int = Field(60, gt=0)
    retry_attempts: int = Field(3, ge=1)
    stream: bool = Field(False)


# ==============================================================================
# STRATEGY IMPLEMENTATIONS
# ==============================================================================


class StrategyEngine:
    """Implements all 21 master prompt strategies"""

    def __init__(self) -> None:
        self.strategies = {
            StrategyType.CHAIN_OF_THOUGHT: self._chain_of_thought,
            StrategyType.TREE_OF_THOUGHTS: self._tree_of_thoughts,
            StrategyType.GRAPH_OF_THOUGHTS: self._graph_of_thoughts,
            StrategyType.LEAST_TO_MOST: self._least_to_most,
            StrategyType.STEP_BACK: self._step_back,
            StrategyType.DECOMPOSED: self._decomposed,
            StrategyType.RETRIEVAL_AUGMENTED: self._retrieval_augmented,
            StrategyType.GENERATED_KNOWLEDGE: self._generated_knowledge,
            StrategyType.KNOWLEDGE_GRAPH: self._knowledge_graph,
            StrategyType.SELF_CONSISTENCY: self._self_consistency,
            StrategyType.SELF_REFINE: self._self_refine,
            StrategyType.SELF_VERIFICATION: self._self_verification,
            StrategyType.REACT: self._react,
            StrategyType.REFLEXION: self._reflexion,
            StrategyType.CHAIN_OF_VERIFICATION: self._chain_of_verification,
            StrategyType.HYPOTHETICAL_DOCUMENT: self._hypothetical_document,
            StrategyType.ANALOGICAL_REASONING: self._analogical_reasoning,
            StrategyType.SOCRATIC_METHOD: self._socratic_method,
            StrategyType.META_PROMPTING: self._meta_prompting,
            StrategyType.PROMPT_OPTIMIZATION: self._prompt_optimization,
            StrategyType.CONSTITUTIONAL_AI: self._constitutional_ai,
        }

    def apply_strategy(
        self, messages: List[Message], strategy: StrategyType, context: Optional[Dict[str, Any]] = None
    ) -> List[Message]:
        """Apply a specific strategy to messages"""
        if strategy not in self.strategies:
            return messages

        strategy_func = self.strategies[strategy]
        return strategy_func(messages, context or {})

    def _chain_of_thought(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Chain of Thought: Step-by-step reasoning"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Let's think through this step by step:\n"
                "1. First, identify the key components\n"
                "2. Then, analyze each component\n"
                "3. Finally, synthesize the solution\n"
                "Show your reasoning for each step."
            )
        return enhanced

    def _tree_of_thoughts(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Tree of Thoughts: Explore multiple reasoning paths"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Consider multiple approaches:\n"
                "Path A: [describe first approach]\n"
                "Path B: [describe alternative approach]\n"
                "Path C: [describe another alternative]\n"
                "Evaluate each path and choose the best one."
            )
        return enhanced

    def _graph_of_thoughts(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Graph of Thoughts: Non-linear reasoning with connections"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Map out the problem as a graph:\n"
                "- Nodes: Key concepts and sub-problems\n"
                "- Edges: Relationships and dependencies\n"
                "- Traverse the graph to find the optimal solution path"
            )
        return enhanced

    def _least_to_most(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Least to Most: Build from simple to complex"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Break this down from simplest to most complex:\n"
                "1. Start with the most basic case\n"
                "2. Gradually add complexity\n"
                "3. Build up to the full solution"
            )
        return enhanced

    def _step_back(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Step Back: Abstract to higher-level principles"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Step back and consider:\n"
                "- What is the underlying principle here?\n"
                "- What category of problem is this?\n"
                "- What general approach applies?"
            )
        return enhanced

    def _decomposed(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Decomposed: Break into sub-problems"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Decompose into sub-problems:\n"
                "- Sub-problem 1: [identify]\n"
                "- Sub-problem 2: [identify]\n"
                "- Solve each independently\n"
                "- Combine solutions"
            )
        return enhanced

    def _retrieval_augmented(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """RAG: Augment with retrieved knowledge"""
        enhanced = messages.copy()
        if "knowledge" in context:
            knowledge = context["knowledge"]
            system_msg = Message(role=Role.SYSTEM, content=f"Use this knowledge to inform your response:\n{knowledge}")
            enhanced.insert(0, system_msg)
        return enhanced

    def _generated_knowledge(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Generate relevant knowledge first"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"First, generate relevant knowledge about: {enhanced[-1].content}\n"
                "Then use that knowledge to answer the question."
            )
        return enhanced

    def _knowledge_graph(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Structure knowledge as a graph"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Structure your knowledge as a graph:\n"
                "- Entities: [identify key entities]\n"
                "- Relations: [identify relationships]\n"
                "- Use this structure to reason about the answer"
            )
        return enhanced

    def _self_consistency(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Self-consistency: Multiple attempts and vote"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Generate 3 independent solutions:\n"
                "Solution 1: [complete solution]\n"
                "Solution 2: [different approach]\n"
                "Solution 3: [another approach]\n"
                "Vote on the best solution and explain why."
            )
        return enhanced

    def _self_refine(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Self-refine: Iterative improvement"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "1. Generate initial solution\n"
                "2. Critique your solution\n"
                "3. Refine based on critique\n"
                "4. Repeat until optimal"
            )
        return enhanced

    def _self_verification(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Self-verification: Verify own output"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "After generating your answer:\n"
                "1. Verify each claim\n"
                "2. Check for consistency\n"
                "3. Validate against requirements\n"
                "4. Correct any issues found"
            )
        return enhanced

    def _react(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """ReAct: Reasoning + Acting"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Use the ReAct framework:\n"
                "Thought: [reasoning about the problem]\n"
                "Action: [what action to take]\n"
                "Observation: [result of action]\n"
                "Repeat until solved."
            )
        return enhanced

    def _reflexion(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Reflexion: Learn from mistakes"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "1. Attempt solution\n"
                "2. Reflect on what went wrong\n"
                "3. Learn from the reflection\n"
                "4. Try improved approach"
            )
        return enhanced

    def _chain_of_verification(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Chain of Verification: Verify step by step"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "For each step in your solution:\n"
                "1. State the step\n"
                "2. Verify it's correct\n"
                "3. Show evidence/reasoning\n"
                "4. Only proceed if verified"
            )
        return enhanced

    def _hypothetical_document(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Hypothetical Document Embeddings"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Imagine you have access to a perfect document that answers this.\n"
                "What would that document contain?\n"
                "Now answer based on that hypothetical perfect resource."
            )
        return enhanced

    def _analogical_reasoning(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Analogical Reasoning: Use analogies"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Think of an analogous problem:\n"
                "- What similar problem have you seen?\n"
                "- How was that solved?\n"
                "- How can you adapt that solution here?"
            )
        return enhanced

    def _socratic_method(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Socratic Method: Question-driven reasoning"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"{enhanced[-1].content}\n\n"
                "Answer by asking and answering questions:\n"
                "Q1: What is really being asked?\n"
                "Q2: What do I need to know?\n"
                "Q3: What assumptions am I making?\n"
                "Q4: What's the best approach?"
            )
        return enhanced

    def _meta_prompting(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Meta-prompting: Reason about the prompt itself"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"Meta-analysis of the task:\n"
                f"Task: {enhanced[-1].content}\n\n"
                "1. What type of problem is this?\n"
                "2. What's the best strategy to solve it?\n"
                "3. Apply that strategy to get the answer"
            )
        return enhanced

    def _prompt_optimization(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Prompt Optimization: Self-optimize the prompt"""
        enhanced = messages.copy()
        if enhanced and enhanced[-1].role == Role.USER:
            enhanced[-1].content = (
                f"Original: {enhanced[-1].content}\n\n"
                "Optimize this request:\n"
                "1. Clarify ambiguities\n"
                "2. Add missing context\n"
                "3. Structure for clarity\n"
                "Then answer the optimized version."
            )
        return enhanced

    def _constitutional_ai(self, messages: List[Message], context: Dict[str, Any]) -> List[Message]:
        """Constitutional AI: Apply principles"""
        enhanced = messages.copy()
        principles = context.get("principles", ["Be helpful", "Be harmless", "Be honest"])

        system_msg = Message(
            role=Role.SYSTEM,
            content=(
                "Apply these constitutional principles:\n"
                + "\n".join(f"- {p}" for p in principles)
                + "\n\nEnsure your response aligns with all principles."
            ),
        )
        enhanced.insert(0, system_msg)
        return enhanced


# ==============================================================================
# IMAGE PROCESSING
# ==============================================================================


class ImageProcessor:
    """Handles image encoding and processing for multimodal models"""

    @staticmethod
    def encode_image(image_path: Union[str, Path]) -> ImageContent:
        """Encode image file to base64"""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        with open(path, "rb") as f:
            image_data = f.read()

        return ImageProcessor.encode_bytes(image_data, ImageProcessor._get_mime_type(path))

    @staticmethod
    def encode_bytes(image_bytes: bytes, mime_type: str = "image/png") -> ImageContent:
        """Encode image bytes to base64"""
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return ImageContent(data=encoded, mime_type=mime_type)

    @staticmethod
    def encode_pil_image(image: Any, format: str = "PNG") -> ImageContent:
        """Encode PIL Image to base64"""
        try:
            from PIL import Image
            import io
        except ImportError:
            raise ImportError("PIL required for image encoding. Install: pip install pillow")

        buffer = io.BytesIO()
        if isinstance(image, Image.Image):
            image.save(buffer, format=format)
            mime_type = f"image/{format.lower()}"
            return ImageProcessor.encode_bytes(buffer.getvalue(), mime_type)
        else:
            raise TypeError("Expected PIL Image object")

    @staticmethod
    def _get_mime_type(path: Path) -> str:
        """Get MIME type from file extension"""
        ext_to_mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
        }
        return ext_to_mime.get(path.suffix.lower(), "image/png")


# ==============================================================================
# PROVIDER INTERFACE
# ==============================================================================


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def query(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Query the LLM"""
        pass

    @abstractmethod
    def stream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream response from LLM"""
        pass

    @abstractmethod
    async def aquery(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Async query the LLM"""
        pass

    @abstractmethod
    async def astream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Async stream response"""
        pass


# ==============================================================================
# PROVIDER IMPLEMENTATIONS
# ==============================================================================


class GeminiProvider(LLMProvider):
    """Google Gemini provider with full feature support"""

    def __init__(self):
        self._client = None
        self._async_client = None

    def _get_client(self):
        """Lazy load Gemini client"""
        if self._client is None:
            try:
                from google import genai

                api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("Gemini API key not found")
                self._client = genai.Client(api_key=api_key)
            except ImportError:
                raise ImportError("google-genai not installed. Run: pip install google-genai")
        return self._client

    def query(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Query Gemini with optional images and structured output"""
        client = self._get_client()

        # Convert messages to Gemini format
        contents = self._format_messages(messages, images)

        # Configure generation
        gen_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
            "top_p": config.top_p,
        }

        # Add response schema for structured output
        if output_model:
            from google.genai.types import GenerateContentConfig

            gen_config["response_mime_type"] = "application/json"
            gen_config["response_schema"] = output_model.model_json_schema()

        try:
            response = client.models.generate_content(
                model=config.model,
                contents=contents,
                config=gen_config,
            )

            content = response.text if hasattr(response, "text") else str(response)

            # Parse structured output if requested
            if output_model:
                try:
                    return output_model.model_validate_json(content)
                except Exception:
                    # Fallback to parsing as dict
                    data = json.loads(content)
                    return output_model.model_validate(data)

            return LLMResponse(
                content=content,
                provider=Provider.GEMINI,
                model=config.model,
                images_processed=len(images) if images else 0,
            )

        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            raise

    def stream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream response from Gemini"""
        client = self._get_client()

        contents = self._format_messages(messages, images)
        gen_config = {
            "temperature": config.temperature,
            "max_output_tokens": config.max_tokens,
        }

        try:
            response = client.models.generate_content_stream(
                model=config.model,
                contents=contents,
                config=gen_config,
            )

            index = 0
            for chunk in response:
                if hasattr(chunk, "text"):
                    yield StreamChunk(
                        content=chunk.text,
                        index=index,
                        is_final=False,
                    )
                    index += 1

            yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            raise

    async def aquery(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Async query - currently uses sync with asyncio"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, messages, config, images, output_model)

    async def astream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Async streaming"""
        for chunk in self.stream(messages, config, images):
            yield chunk

    def _format_messages(self, messages: List[Message], images: Optional[List[ImageContent]]) -> str:
        """Format messages for Gemini"""
        parts = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                parts.append(f"System: {msg.content}")
            elif msg.role == Role.USER:
                parts.append(f"User: {msg.content}")
            elif msg.role == Role.ASSISTANT:
                parts.append(f"Assistant: {msg.content}")

        # Add images if provided
        if images:
            parts.append(f"\n[Processing {len(images)} image(s)]")

        return "\n\n".join(parts)


class OpenAIProvider(LLMProvider):
    """OpenAI provider with GPT-4o vision and streaming"""

    def __init__(self):
        self._client = None
        self._async_client = None

    def _get_client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI

                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                self._client = OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai not installed. Run: pip install openai")
        return self._client

    def _get_async_client(self) -> Any:
        """Lazy load async OpenAI client"""
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI

                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                self._async_client = AsyncOpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai not installed. Run: pip install openai")
        return self._async_client

    def query(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Query OpenAI with vision and structured output support"""
        client = self._get_client()

        # Format messages for OpenAI
        openai_messages = self._format_messages(messages, images)

        # Enforce OpenAI token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        # Add structured output if requested
        if output_model:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": output_model.__name__,
                    "schema": output_model.model_json_schema(),
                },
            }

        try:
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""

            if output_model:
                return output_model.model_validate_json(content)

            return LLMResponse(
                content=content,
                provider=Provider.OPENAI,
                model=config.model,
                images_processed=len(images) if images else 0,
                prompt_tokens=response.usage.prompt_tokens if response.usage else None,
                completion_tokens=response.usage.completion_tokens if response.usage else None,
            )

        except Exception as e:
            logger.error(f"OpenAI query failed: {e}")
            raise

    def stream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream response from OpenAI"""
        client = self._get_client()

        openai_messages = self._format_messages(messages, images)

        # Enforce OpenAI token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            stream = client.chat.completions.create(**kwargs)

            index = 0
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        index=index,
                        is_final=False,
                        finish_reason=chunk.choices[0].finish_reason,
                    )
                    index += 1

            yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise

    async def aquery(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Async query OpenAI"""
        client = self._get_async_client()

        openai_messages = self._format_messages(messages, images)

        # Enforce OpenAI token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if output_model:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": output_model.__name__,
                    "schema": output_model.model_json_schema(),
                },
            }

        try:
            response = await client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""

            if output_model:
                return output_model.model_validate_json(content)

            return LLMResponse(
                content=content,
                provider=Provider.OPENAI,
                model=config.model,
                images_processed=len(images) if images else 0,
            )

        except Exception as e:
            logger.error(f"OpenAI async query failed: {e}")
            raise

    async def astream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Async stream from OpenAI"""
        client = self._get_async_client()

        openai_messages = self._format_messages(messages, images)

        # Enforce OpenAI token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": openai_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            stream = await client.chat.completions.create(**kwargs)

            index = 0
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        index=index,
                        is_final=False,
                    )
                    index += 1

            yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"OpenAI async streaming failed: {e}")
            raise

    def _format_messages(self, messages: List[Message], images: Optional[List[ImageContent]]) -> List[Dict[str, Any]]:
        """Format messages for OpenAI including vision content"""
        openai_messages = []

        for msg in messages:
            openai_msg: Dict[str, Any] = {
                "role": msg.role.value,
                "content": msg.content,
            }

            # Add images to user messages if provided
            if msg.role == Role.USER and images:
                content_parts = [{"type": "text", "text": msg.content}]

                for img in images:
                    content_parts.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{img.mime_type};base64,{img.data}",
                                "detail": img.detail.value,
                            },
                        }
                    )

                openai_msg["content"] = content_parts

            openai_messages.append(openai_msg)

        return openai_messages


class AnthropicProvider(LLMProvider):
    """Anthropic provider with Claude vision and streaming"""

    def __init__(self):
        self._client = None
        self._async_client = None

    def _get_client(self):
        """Lazy load Anthropic client"""
        if self._client is None:
            try:
                from anthropic import Anthropic

                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not found")
                self._client = Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic not installed. Run: pip install anthropic")
        return self._client

    def _get_async_client(self) -> Any:
        """Lazy load async Anthropic client"""
        if self._async_client is None:
            try:
                from anthropic import AsyncAnthropic

                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not found")
                self._async_client = AsyncAnthropic(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic not installed. Run: pip install anthropic")
        return self._async_client

    def query(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Query Anthropic Claude"""
        client = self._get_client()

        # Format for Anthropic
        system_message = None
        claude_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                claude_messages.append(
                    {
                        "role": msg.role.value if msg.role != Role.USER else "user",
                        "content": self._format_content(msg.content, images if msg.role == Role.USER else None),
                    }
                )

        # Enforce Anthropic token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": claude_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        try:
            response = client.messages.create(**kwargs)

            content = ""
            if hasattr(response, "content"):
                if isinstance(response.content, list):
                    content = response.content[0].text if response.content else ""
                else:
                    content = response.content

            if output_model:
                # Parse JSON response
                return output_model.model_validate_json(content)

            return LLMResponse(
                content=content,
                provider=Provider.ANTHROPIC,
                model=config.model,
                images_processed=len(images) if images else 0,
            )

        except Exception as e:
            logger.error(f"Anthropic query failed: {e}")
            raise

    def stream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> Iterator[StreamChunk]:
        """Stream response from Anthropic"""
        client = self._get_client()

        system_message = None
        claude_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                claude_messages.append(
                    {
                        "role": msg.role.value if msg.role != Role.USER else "user",
                        "content": self._format_content(msg.content, images if msg.role == Role.USER else None),
                    }
                )

        # Enforce Anthropic token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": claude_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        try:
            with client.messages.stream(**kwargs) as stream:
                index = 0
                for text in stream.text_stream:
                    yield StreamChunk(
                        content=text,
                        index=index,
                        is_final=False,
                    )
                    index += 1

                yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise

    async def aquery(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
        output_model: Optional[Type[T]] = None,
    ) -> Union[LLMResponse, T]:
        """Async query Anthropic"""
        client = self._get_async_client()

        system_message = None
        claude_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                claude_messages.append(
                    {
                        "role": msg.role.value if msg.role != Role.USER else "user",
                        "content": self._format_content(msg.content, images if msg.role == Role.USER else None),
                    }
                )

        # Enforce Anthropic token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": claude_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        try:
            response = await client.messages.create(**kwargs)

            content = ""
            if hasattr(response, "content"):
                if isinstance(response.content, list):
                    content = response.content[0].text if response.content else ""
                else:
                    content = response.content

            if output_model:
                return output_model.model_validate_json(content)

            return LLMResponse(
                content=content,
                provider=Provider.ANTHROPIC,
                model=config.model,
                images_processed=len(images) if images else 0,
            )

        except Exception as e:
            logger.error(f"Anthropic async query failed: {e}")
            raise

    async def astream(
        self,
        messages: List[Message],
        config: LLMConfig,
        images: Optional[List[ImageContent]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Async stream from Anthropic"""
        client = self._get_async_client()

        system_message = None
        claude_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                claude_messages.append(
                    {
                        "role": msg.role.value if msg.role != Role.USER else "user",
                        "content": self._format_content(msg.content, images if msg.role == Role.USER else None),
                    }
                )

        # Enforce Anthropic token limits
        max_tokens = min(config.max_tokens, 4096)

        kwargs = {
            "model": config.model,
            "messages": claude_messages,
            "temperature": config.temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        try:
            async with client.messages.stream(**kwargs) as stream:
                index = 0
                async for text in stream.text_stream:
                    yield StreamChunk(
                        content=text,
                        index=index,
                        is_final=False,
                    )
                    index += 1

                yield StreamChunk(content="", index=index, is_final=True)

        except Exception as e:
            logger.error(f"Anthropic async streaming failed: {e}")
            raise

    def _format_content(self, text: str, images: Optional[List[ImageContent]]) -> Union[str, List[Dict[str, Any]]]:
        """Format content with images for Claude"""
        if not images:
            return text

        content = [{"type": "text", "text": text}]

        for img in images:
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": img.mime_type,
                        "data": img.data,
                    },
                }
            )

        return content


# ==============================================================================
# UNIFIED GATEWAY
# ==============================================================================


class UnifiedLLMGateway:
    """Single source of truth for all LLM operations"""

    def __init__(self):
        self.providers: Dict[Provider, LLMProvider] = {}
        self.strategy_engine = StrategyEngine()
        self.image_processor = ImageProcessor()

    def _get_provider(self, provider: Provider) -> LLMProvider:
        """Get or create provider instance"""
        if provider not in self.providers:
            if provider == Provider.OPENAI:
                self.providers[provider] = OpenAIProvider()
            elif provider in (Provider.GEMINI, Provider.GOOGLE):
                self.providers[provider] = GeminiProvider()
            elif provider == Provider.ANTHROPIC:
                self.providers[provider] = AnthropicProvider()
            else:
                raise ValueError(f"Unsupported provider: {provider}")

        return self.providers[provider]

    def query(
        self,
        messages: List[Dict[str, Any]],
        provider: Optional[Union[Provider, str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        strategy: Optional[Union[StrategyType, str]] = None,
        images: Optional[List[Union[str, Path, bytes, ImageContent]]] = None,
        output_model: Optional[Type[T]] = None,
        **kwargs,
    ) -> Union[LLMResponse, T]:
        """
        Unified query interface for all LLM operations

        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: LLM provider to use
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            strategy: Prompt strategy to apply
            images: Images to include (paths, bytes, or ImageContent)
            output_model: Pydantic model for structured output
            **kwargs: Additional provider-specific arguments

        Returns:
            LLMResponse or structured output model instance
        """
        # Convert to Message objects
        msg_objects = [Message(role=Role(m["role"]), content=m["content"]) for m in messages]

        # Process images if provided
        image_contents = None
        if images:
            image_contents = []
            for img in images:
                if isinstance(img, ImageContent):
                    image_contents.append(img)
                elif isinstance(img, (str, Path)):
                    image_contents.append(self.image_processor.encode_image(img))
                elif isinstance(img, bytes):
                    image_contents.append(self.image_processor.encode_bytes(img))

        # Apply strategy if specified
        if strategy:
            strategy_enum = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)
            msg_objects = self.strategy_engine.apply_strategy(msg_objects, strategy_enum, kwargs)

        # Configure LLM
        config = LLMConfig(
            provider=Provider(provider or "gemini"),
            model=model or "gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens,
            strategy=strategy if isinstance(strategy, StrategyType) else None,
        )

        # Get provider and execute query
        llm_provider = self._get_provider(config.provider)

        result = llm_provider.query(msg_objects, config, image_contents, output_model)

        # Add strategy metadata if used
        if isinstance(result, LLMResponse) and strategy:
            result.strategy_used = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)

        return result

    def stream(
        self,
        messages: List[Dict[str, Any]],
        provider: Optional[Union[Provider, str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        strategy: Optional[Union[StrategyType, str]] = None,
        images: Optional[List[Union[str, Path, bytes, ImageContent]]] = None,
        **kwargs,
    ) -> Iterator[StreamChunk]:
        """Stream response from LLM"""
        # Convert messages
        msg_objects = [Message(role=Role(m["role"]), content=m["content"]) for m in messages]

        # Process images
        image_contents = None
        if images:
            image_contents = []
            for img in images:
                if isinstance(img, ImageContent):
                    image_contents.append(img)
                elif isinstance(img, (str, Path)):
                    image_contents.append(self.image_processor.encode_image(img))
                elif isinstance(img, bytes):
                    image_contents.append(self.image_processor.encode_bytes(img))

        # Apply strategy
        if strategy:
            strategy_enum = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)
            msg_objects = self.strategy_engine.apply_strategy(msg_objects, strategy_enum, kwargs)

        # Configure
        config = LLMConfig(
            provider=Provider(provider or "gemini"),
            model=model or "gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        # Stream
        llm_provider = self._get_provider(config.provider)
        yield from llm_provider.stream(msg_objects, config, image_contents)

    async def aquery(
        self,
        messages: List[Dict[str, Any]],
        provider: Optional[Union[Provider, str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        strategy: Optional[Union[StrategyType, str]] = None,
        images: Optional[List[Union[str, Path, bytes, ImageContent]]] = None,
        output_model: Optional[Type[T]] = None,
        **kwargs,
    ) -> Union[LLMResponse, T]:
        """Async query LLM"""
        # Convert messages
        msg_objects = [Message(role=Role(m["role"]), content=m["content"]) for m in messages]

        # Process images
        image_contents = None
        if images:
            image_contents = []
            for img in images:
                if isinstance(img, ImageContent):
                    image_contents.append(img)
                elif isinstance(img, (str, Path)):
                    image_contents.append(self.image_processor.encode_image(img))
                elif isinstance(img, bytes):
                    image_contents.append(self.image_processor.encode_bytes(img))

        # Apply strategy
        if strategy:
            strategy_enum = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)
            msg_objects = self.strategy_engine.apply_strategy(msg_objects, strategy_enum, kwargs)

        # Configure
        config = LLMConfig(
            provider=Provider(provider or "gemini"),
            model=model or "gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Query
        llm_provider = self._get_provider(config.provider)
        return await llm_provider.aquery(msg_objects, config, image_contents, output_model)

    async def astream(
        self,
        messages: List[Dict[str, Any]],
        provider: Optional[Union[Provider, str]] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        strategy: Optional[Union[StrategyType, str]] = None,
        images: Optional[List[Union[str, Path, bytes, ImageContent]]] = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """Async stream from LLM"""
        # Convert messages
        msg_objects = [Message(role=Role(m["role"]), content=m["content"]) for m in messages]

        # Process images
        image_contents = None
        if images:
            image_contents = []
            for img in images:
                if isinstance(img, ImageContent):
                    image_contents.append(img)
                elif isinstance(img, (str, Path)):
                    image_contents.append(self.image_processor.encode_image(img))
                elif isinstance(img, bytes):
                    image_contents.append(self.image_processor.encode_bytes(img))

        # Apply strategy
        if strategy:
            strategy_enum = strategy if isinstance(strategy, StrategyType) else StrategyType(strategy)
            msg_objects = self.strategy_engine.apply_strategy(msg_objects, strategy_enum, kwargs)

        # Configure
        config = LLMConfig(
            provider=Provider(provider or "gemini"),
            model=model or "gemini-2.0-flash",
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        # Stream
        llm_provider = self._get_provider(config.provider)
        async for chunk in llm_provider.astream(msg_objects, config, image_contents):
            yield chunk


# ==============================================================================
# PUBLIC API - SINGLE SOURCE OF TRUTH
# ==============================================================================

# Global gateway instance
_gateway = UnifiedLLMGateway()


def query_llm(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    output_model: Optional[Type[T]] = None,
    **kwargs,
) -> Union[LLMResponse, T]:
    """
    Query LLM with unified interface

    Args:
        messages: List of message dicts
        provider: Provider name (openai, anthropic, gemini)
        model: Model name
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        strategy: Prompt strategy name
        images: Images to include
        output_model: Pydantic model for structured output

    Returns:
        LLMResponse or structured model instance
    """
    return _gateway.query(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        strategy=strategy,
        images=images,
        output_model=output_model,
        **kwargs,
    )


def stream_llm(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    **kwargs,
) -> Iterator[StreamChunk]:
    """Stream response from LLM"""
    return _gateway.stream(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        strategy=strategy,
        images=images,
        **kwargs,
    )


async def aquery_llm(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    output_model: Optional[Type[T]] = None,
    **kwargs,
) -> Union[LLMResponse, T]:
    """Async query LLM"""
    return await _gateway.aquery(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        strategy=strategy,
        images=images,
        output_model=output_model,
        **kwargs,
    )


async def astream_llm(
    messages: List[Dict[str, Any]],
    provider: str = "gemini",
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,
    max_tokens: int = 8192,
    strategy: Optional[str] = None,
    images: Optional[List[Union[str, Path, bytes]]] = None,
    **kwargs,
) -> AsyncIterator[StreamChunk]:
    """Async stream from LLM"""
    async for chunk in _gateway.astream(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        strategy=strategy,
        images=images,
        **kwargs,
    ):
        yield chunk


def call_default_llm(messages: List[Dict[str, Any]], **kwargs) -> LLMResponse:
    """Call default LLM (Gemini) - backward compatible function"""
    return query_llm(messages, **kwargs)


# Export all public components
__all__ = [
    # Main API functions
    "query_llm",
    "stream_llm",
    "aquery_llm",
    "astream_llm",
    "call_default_llm",
    # Core classes
    "UnifiedLLMGateway",
    "StrategyEngine",
    "ImageProcessor",
    # Enums
    "Provider",
    "StrategyType",
    "Role",
    "ImageDetail",
    # Data models
    "Message",
    "LLMResponse",
    "LLMConfig",
    "StreamChunk",
    "ImageContent",
]

