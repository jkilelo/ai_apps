"""
Shared LLM utilities for the UI Testing Framework
Centralizes common LLM operations to follow DRY principles
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from prompts import StrategyName, enhance_with_strategy

class LLMResponseParser:
    """Centralized JSON parsing for LLM responses"""
    
    @staticmethod
    def clean_response(response: str) -> str:
        """
        Remove markdown blocks and clean response
        
        Args:
            response: Raw LLM response
            
        Returns:
            Cleaned response string
        """
        response = response.strip()
        
        # Remove markdown code blocks
        if '```json' in response:
            response = response.replace('```json', '').replace('```', '')
            response = response.strip()
        elif '```' in response:
            # Remove generic markdown blocks
            lines = response.split('\n')
            in_block = False
            cleaned_lines = []
            
            for line in lines:
                if line.strip() == '```':
                    in_block = not in_block
                    continue
                if not in_block or not line.startswith('```'):
                    cleaned_lines.append(line)
            
            response = '\n'.join(cleaned_lines).strip()
        
        return response
    
    @staticmethod
    def fix_json_errors(json_str: str) -> str:
        """
        Fix common JSON errors from LLM output
        
        Args:
            json_str: Potentially malformed JSON string
            
        Returns:
            Fixed JSON string
        """
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix missing commas between elements
        json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
        json_str = re.sub(r'}\s*\n\s*{', '},\n{', json_str)
        json_str = re.sub(r']\s*\n\s*\[', '],\n[', json_str)
        
        # Replace single quotes with double quotes (but not inside strings)
        json_str = re.sub(r"(?<=[{\[,:]\s)'", '"', json_str)
        json_str = re.sub(r"'(?=\s*[,}\]:])", '"', json_str)
        
        return json_str
    
    @staticmethod
    def parse_json_array(response: str, strict: bool = True) -> List[Dict[str, Any]]:
        """
        Parse JSON array from LLM response
        
        Args:
            response: LLM response containing JSON array
            strict: If True, raise exception on parse failure. If False, return empty list
            
        Returns:
            Parsed JSON array
            
        Raises:
            ValueError: If strict=True and parsing fails
        """
        # Clean the response
        response = LLMResponseParser.clean_response(response)
        
        # Try direct JSON parse
        if response.startswith('['):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Try to fix common JSON errors
                response = LLMResponseParser.fix_json_errors(response)
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
        
        # Try to extract JSON array using regex
        json_match = re.search(r'\[.*?\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Try fixing errors
                json_str = LLMResponseParser.fix_json_errors(json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
        
        if strict:
            raise ValueError(f"Could not parse JSON array from response: {response[:200]}...")
        return []
    
    @staticmethod
    def parse_json_object(response: str, strict: bool = True) -> Dict[str, Any]:
        """
        Parse JSON object from LLM response
        
        Args:
            response: LLM response containing JSON object
            strict: If True, raise exception on parse failure. If False, return empty dict
            
        Returns:
            Parsed JSON object
            
        Raises:
            ValueError: If strict=True and parsing fails
        """
        # Clean the response
        response = LLMResponseParser.clean_response(response)
        
        # Try direct JSON parse
        if response.startswith('{'):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Try to fix common JSON errors
                response = LLMResponseParser.fix_json_errors(response)
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass
        
        # Try to extract JSON object using regex
        # More sophisticated regex to handle nested objects
        brace_count = 0
        json_start = -1
        
        for i, char in enumerate(response):
            if char == '{':
                if brace_count == 0:
                    json_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and json_start != -1:
                    json_str = response[json_start:i+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # Try fixing errors
                        json_str = LLMResponseParser.fix_json_errors(json_str)
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue
        
        if strict:
            raise ValueError(f"Could not parse JSON object from response: {response[:200]}...")
        return {}


class StrategySelector:
    """Centralized strategy selection for different tasks"""
    
    # Comprehensive strategy mapping for all tasks
    STRATEGY_MAP = {
        # Element analysis strategies
        "element_analysis": StrategyName.CHAIN_OF_THOUGHT,
        "semantic_understanding": StrategyName.META_COGNITIVE_FRAMEWORK,
        "page_classification": StrategyName.FEW_SHOT,
        "framework_detection": StrategyName.CHAIN_OF_TABLE,
        "interaction_prediction": StrategyName.REFLEXION,
        
        # Test generation strategies
        "scenario_generation": StrategyName.TREE_OF_THOUGHTS,
        "gherkin_creation": StrategyName.PROGRAM_AIDED_LANGUAGE,
        "test_data_generation": StrategyName.SELF_CONSISTENCY,
        "edge_case_discovery": StrategyName.DEBATE,
        "test_scenario": StrategyName.PROGRAM_AIDED_LANGUAGE,
        
        # QA strategies
        "qa_generation": StrategyName.TREE_OF_THOUGHTS,
        "qa_planning": StrategyName.QA_ENGINEER_AGENT,
        
        # Validation strategies
        "validation": StrategyName.SELF_CONSISTENCY,
        "validation_rules": StrategyName.REFLEXION,
        
        # Security & accessibility
        "accessibility": StrategyName.CONSTITUTIONAL_AI,
        "accessibility_testing": StrategyName.CONSTITUTIONAL_AI,
        "security": StrategyName.DEBATE,
        "security_testing": StrategyName.CHAIN_OF_THOUGHT,
        
        # Performance & error handling
        "performance_scenarios": StrategyName.META_COGNITIVE_FRAMEWORK,
        "error_scenarios": StrategyName.FEW_SHOT,
        "error_handling": StrategyName.FEW_SHOT,
        
        # Integration & data
        "integration_testing": StrategyName.CHAIN_OF_TABLE,
        "data_validation": StrategyName.CHAIN_OF_TABLE,
    }
    
    @classmethod
    def get_strategy(cls, task: str) -> str:
        """
        Get strategy for a specific task
        
        Args:
            task: Task type/name
            
        Returns:
            Strategy name as string
        """
        strategy = cls.STRATEGY_MAP.get(task, StrategyName.CHAIN_OF_THOUGHT)
        return strategy.value if hasattr(strategy, 'value') else strategy
    
    @classmethod
    def get_strategy_enum(cls, task: str) -> StrategyName:
        """
        Get strategy enum for a specific task
        
        Args:
            task: Task type/name
            
        Returns:
            StrategyName enum value
        """
        return cls.STRATEGY_MAP.get(task, StrategyName.CHAIN_OF_THOUGHT)
    
    @classmethod
    def list_tasks(cls) -> List[str]:
        """
        List all available tasks
        
        Returns:
            List of task names
        """
        return list(cls.STRATEGY_MAP.keys())
    
    @classmethod
    def list_strategies_for_category(cls, category: str) -> Dict[str, str]:
        """
        List all strategies for a category of tasks
        
        Args:
            category: Category name (e.g., 'test', 'element', 'qa')
            
        Returns:
            Dictionary of task -> strategy mappings
        """
        result = {}
        for task, strategy in cls.STRATEGY_MAP.items():
            if category.lower() in task.lower():
                result[task] = strategy.value if hasattr(strategy, 'value') else strategy
        return result


class LLMPromptBuilder:
    """Helper class to build consistent prompts"""
    
    @staticmethod
    def build_json_prompt(
        task_description: str,
        context: Dict[str, Any],
        expected_structure: Dict[str, str],
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build a consistent JSON-requesting prompt
        
        Args:
            task_description: What the LLM should do
            context: Context information (will be formatted as key: value)
            expected_structure: Expected JSON structure with field descriptions
            examples: Optional examples to include
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [task_description, ""]
        
        # Add context
        if context:
            prompt_parts.append("CONTEXT:")
            for key, value in context.items():
                if isinstance(value, (list, dict)):
                    prompt_parts.append(f"{key}: {json.dumps(value, indent=2)}")
                else:
                    prompt_parts.append(f"{key}: {value}")
            prompt_parts.append("")
        
        # Add examples if provided
        if examples:
            prompt_parts.append("EXAMPLES:")
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"Example {i}:")
                prompt_parts.append(json.dumps(example, indent=2))
            prompt_parts.append("")
        
        # Add expected structure
        prompt_parts.append("Return JSON with this exact structure:")
        structure_json = json.dumps(expected_structure, indent=2)
        prompt_parts.append(structure_json)
        prompt_parts.append("")
        prompt_parts.append("IMPORTANT: Return ONLY valid JSON, no markdown blocks or explanations.")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def build_analysis_prompt(
        items_to_analyze: List[Any],
        analysis_instructions: str,
        output_format: str = "json"
    ) -> str:
        """
        Build a prompt for analyzing items
        
        Args:
            items_to_analyze: Items to analyze (will be JSON serialized)
            analysis_instructions: What analysis to perform
            output_format: Expected output format
            
        Returns:
            Formatted analysis prompt
        """
        prompt_parts = [
            analysis_instructions,
            "",
            "ITEMS TO ANALYZE:",
            json.dumps(items_to_analyze, indent=2) if isinstance(items_to_analyze, (list, dict)) else str(items_to_analyze),
            ""
        ]
        
        if output_format == "json":
            prompt_parts.append("Return your analysis as valid JSON.")
        else:
            prompt_parts.append(f"Return your analysis in {output_format} format.")
        
        return "\n".join(prompt_parts)


def prepare_llm_messages(
    user_content: str,
    system_content: Optional[str] = None,
    strategy: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Prepare messages for LLM call with optional strategy enhancement
    
    Args:
        user_content: User message content
        system_content: Optional system message (defaults to helpful assistant if not provided)
        strategy: Optional strategy name to apply
        
    Returns:
        List of message dictionaries ready for LLM call
    """
    messages = []
    
    # Always include a system message - use default if not provided
    if system_content:
        messages.append({"role": "system", "content": system_content})
    else:
        messages.append({"role": "system", "content": "You are a helpful assistant that genuinely helps users."})
    
    messages.append({"role": "user", "content": user_content})
    
    if strategy:
        messages = enhance_with_strategy(messages, strategy)
    
    return messages


# Export main components
__all__ = [
    'LLMResponseParser',
    'StrategySelector',
    'LLMPromptBuilder',
    'prepare_llm_messages'
]