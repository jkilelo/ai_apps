"""
Intermediate Test Format

Defines the JSON intermediate format for reliable test generation.
This format serves as a bridge between natural language and Gherkin.
"""

import json
import logging
from typing import Dict, List, Any, Optional
# from jsonschema import validate, ValidationError, Draft7Validator
# For now, we'll use simple validation without jsonschema

logger = logging.getLogger(__name__)


class IntermediateTestFormat:
    """
    Manages the intermediate JSON format for test scenarios.
    
    This format ensures:
    - Consistent structure between LLM outputs
    - Easy conversion to Gherkin
    - Validation and error handling
    - Support for advanced Gherkin features
    """
    
    # JSON Schema for test scenarios
    SCENARIO_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["title", "steps"],
        "properties": {
            "title": {
                "type": "string",
                "description": "Clear, descriptive scenario title",
                "minLength": 5,
                "maxLength": 200
            },
            "description": {
                "type": "string",
                "description": "Detailed description of what the scenario tests"
            },
            "type": {
                "type": "string",
                "enum": ["scenario", "scenario_outline"],
                "default": "scenario"
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_-]+$"
                },
                "description": "Tags for categorization and filtering"
            },
            "priority": {
                "type": "string",
                "enum": ["critical", "high", "medium", "low"],
                "default": "medium"
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence score for the scenario"
            },
            "prerequisites": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Prerequisites or setup requirements"
            },
            "steps": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "$ref": "#/definitions/step"
                }
            },
            "examples": {
                "type": "object",
                "description": "Data table for scenario outlines",
                "patternProperties": {
                    "^[a-zA-Z_][a-zA-Z0-9_]*$": {
                        "type": "array",
                        "items": {
                            "type": ["string", "number", "boolean", "null"]
                        }
                    }
                }
            },
            "expected_duration": {
                "type": "integer",
                "description": "Expected duration in seconds",
                "minimum": 1
            },
            "business_value": {
                "type": "string",
                "description": "Business value or impact of this test"
            }
        },
        "definitions": {
            "step": {
                "type": "object",
                "required": ["action", "description"],
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "navigate", "click", "fill", "type", "select", 
                            "check", "uncheck", "hover", "drag", "upload",
                            "wait", "verify", "assert", "screenshot",
                            "scroll", "clear", "press", "right_click"
                        ]
                    },
                    "description": {
                        "type": "string",
                        "description": "Human-readable description of the step"
                    },
                    "element_selector": {
                        "type": "string",
                        "description": "CSS selector or XPath for the element"
                    },
                    "test_data": {
                        "type": "object",
                        "description": "Data needed for the step",
                        "properties": {
                            "value": {
                                "type": ["string", "number", "boolean"],
                                "description": "Value to input or verify"
                            },
                            "url": {
                                "type": "string",
                                "format": "uri-reference"
                            },
                            "file_path": {
                                "type": "string"
                            },
                            "wait_time": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 30000
                            },
                            "key": {
                                "type": "string",
                                "description": "Keyboard key to press"
                            },
                            "options": {
                                "type": "object",
                                "description": "Additional options for the action"
                            }
                        }
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout for this step in seconds",
                        "minimum": 1,
                        "maximum": 300,
                        "default": 10
                    },
                    "optional": {
                        "type": "boolean",
                        "description": "Whether this step is optional",
                        "default": False
                    },
                    "error_handling": {
                        "type": "string",
                        "enum": ["fail", "continue", "retry"],
                        "default": "fail"
                    }
                }
            }
        }
    }
    
    # Test data generation templates
    DATA_TEMPLATES = {
        "valid_email": [
            "user@example.com",
            "test.user@company.com",
            "john.doe+test@email.co.uk"
        ],
        "invalid_email": [
            "notanemail",
            "@example.com",
            "user@",
            "user..test@example.com"
        ],
        "valid_phone": [
            "+1-555-123-4567",
            "(555) 123-4567",
            "555.123.4567"
        ],
        "invalid_phone": [
            "123",
            "phone-number",
            "555-CALL-NOW"
        ],
        "valid_password": [
            "SecurePass123!",
            "P@ssw0rd2024",
            "MyStr0ng!Pass"
        ],
        "weak_password": [
            "password",
            "12345678",
            "qwerty"
        ],
        "valid_credit_card": [
            "4111111111111111",  # Test Visa
            "5500000000000004",  # Test Mastercard
            "340000000000009"    # Test Amex
        ],
        "valid_date": [
            "2024-12-31",
            "01/15/2025",
            "March 1, 2024"
        ],
        "boundary_numbers": {
            "min": [-2147483648, 0, 1],
            "max": [2147483647, 999999, 100],
            "invalid": [-999999999999, "NaN", "infinity"]
        },
        "special_characters": [
            "!@#$%^&*()",
            "<script>alert('test')</script>",
            "'; DROP TABLE users; --",
            "\\n\\r\\t"
        ],
        "unicode_strings": [
            "Hello 世界",
            "Café ☕",
            "🎉 Emoji test 🎉",
            "Ñoño"
        ]
    }
    
    @classmethod
    def validate_scenario(cls, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a scenario against the schema.
        
        Returns:
            Dict with 'valid' bool and 'errors' list
        """
        errors = []
        
        # Basic validation without jsonschema
        if not scenario.get('title'):
            errors.append("Scenario must have a title")
        
        if not scenario.get('steps'):
            errors.append("Scenario must have steps")
        
        # Validate step structure
        for i, step in enumerate(scenario.get('steps', [])):
            if not step.get('action'):
                errors.append(f"Step {i} must have an action")
            if not step.get('description'):
                errors.append(f"Step {i} must have a description")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @classmethod
    def validate_scenarios(cls, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate multiple scenarios and return only valid ones.
        """
        valid_scenarios = []
        
        for i, scenario in enumerate(scenarios):
            validation_result = cls.validate_scenario(scenario)
            
            if validation_result["valid"]:
                valid_scenarios.append(scenario)
            else:
                logger.warning(
                    f"Scenario {i} validation failed: {validation_result['errors']}"
                )
                logger.debug(f"Failed scenario structure: {scenario}")
                
                # Try to fix common issues
                fixed_scenario = cls._attempt_fix_scenario(scenario)
                if fixed_scenario:
                    revalidation = cls.validate_scenario(fixed_scenario)
                    if revalidation["valid"]:
                        logger.info(f"Successfully fixed scenario {i}")
                        valid_scenarios.append(fixed_scenario)
        
        return valid_scenarios
    
    @classmethod
    def _attempt_fix_scenario(cls, scenario: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to fix common validation issues."""
        fixed = scenario.copy()
        
        # Ensure required fields
        if "title" not in fixed or not fixed["title"]:
            fixed["title"] = "Untitled Test Scenario"
        
        if "steps" not in fixed or not fixed["steps"]:
            return None  # Can't fix missing steps
        
        # Fix step issues
        fixed_steps = []
        for step in fixed.get("steps", []):
            fixed_step = step.copy()
            
            # Ensure required step fields
            if "action" not in fixed_step:
                # Try to infer action from description
                fixed_step["action"] = cls._infer_action(
                    fixed_step.get("description", "")
                )
            
            if "description" not in fixed_step:
                fixed_step["description"] = f"Perform {fixed_step.get('action', 'action')}"
            
            # Validate action value
            valid_actions = cls.SCENARIO_SCHEMA["definitions"]["step"]["properties"]["action"]["enum"]
            if fixed_step.get("action") not in valid_actions:
                fixed_step["action"] = "click"  # Default action
            
            fixed_steps.append(fixed_step)
        
        fixed["steps"] = fixed_steps
        
        # Fix type if invalid
        if fixed.get("type") not in ["scenario", "scenario_outline"]:
            fixed["type"] = "scenario"
        
        # Fix priority if invalid
        if fixed.get("priority") not in ["critical", "high", "medium", "low"]:
            fixed["priority"] = "medium"
        
        # Ensure confidence is in range
        if "confidence" in fixed:
            fixed["confidence"] = max(0, min(1, float(fixed["confidence"])))
        
        return fixed
    
    @classmethod
    def _infer_action(cls, description: str) -> str:
        """Infer action type from description."""
        description_lower = description.lower()
        
        action_keywords = {
            "click": ["click", "tap", "press"],
            "fill": ["enter", "type", "input", "fill"],
            "select": ["select", "choose", "pick"],
            "navigate": ["navigate", "go to", "open", "visit"],
            "verify": ["verify", "check", "assert", "should"],
            "wait": ["wait", "pause", "delay"],
            "hover": ["hover", "mouse over"],
            "scroll": ["scroll", "swipe"],
            "upload": ["upload", "attach", "browse"]
        }
        
        for action, keywords in action_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return action
        
        return "click"  # Default action
    
    @classmethod
    def create_scenario_template(
        cls,
        scenario_type: str = "generic",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a scenario template for specific types."""
        templates = {
            "form_submission": {
                "title": "Submit form with valid data",
                "type": "scenario",
                "tags": ["form", "positive", "submission"],
                "priority": "high",
                "steps": [
                    {
                        "action": "navigate",
                        "description": "Navigate to form page",
                        "test_data": {"url": kwargs.get("url", "/form")}
                    },
                    {
                        "action": "fill",
                        "description": "Fill in required fields",
                        "element_selector": "input[required]",
                        "test_data": {"value": "{{field_value}}"}
                    },
                    {
                        "action": "click",
                        "description": "Submit the form",
                        "element_selector": "button[type='submit']"
                    },
                    {
                        "action": "verify",
                        "description": "Verify successful submission",
                        "test_data": {"value": "Success message displayed"}
                    }
                ]
            },
            "login": {
                "title": "User login with valid credentials",
                "type": "scenario_outline",
                "tags": ["authentication", "login"],
                "priority": "critical",
                "steps": [
                    {
                        "action": "navigate",
                        "description": "Go to login page",
                        "test_data": {"url": "/login"}
                    },
                    {
                        "action": "fill",
                        "description": "Enter username",
                        "element_selector": "#username",
                        "test_data": {"value": "<username>"}
                    },
                    {
                        "action": "fill",
                        "description": "Enter password",
                        "element_selector": "#password",
                        "test_data": {"value": "<password>"}
                    },
                    {
                        "action": "click",
                        "description": "Click login button",
                        "element_selector": "button[type='submit']"
                    },
                    {
                        "action": "verify",
                        "description": "Verify login success",
                        "test_data": {"value": "<expected_result>"}
                    }
                ],
                "examples": {
                    "username": ["user1", "admin", "test@email.com"],
                    "password": ["Pass123!", "Admin@2024", "TestPass!"],
                    "expected_result": ["Dashboard visible", "Admin panel visible", "User home visible"]
                }
            },
            "search": {
                "title": "Search functionality",
                "type": "scenario",
                "tags": ["search", "functionality"],
                "priority": "high",
                "steps": [
                    {
                        "action": "fill",
                        "description": "Enter search query",
                        "element_selector": "input[type='search']",
                        "test_data": {"value": kwargs.get("search_term", "test query")}
                    },
                    {
                        "action": "click",
                        "description": "Click search button",
                        "element_selector": "button[type='submit']"
                    },
                    {
                        "action": "wait",
                        "description": "Wait for results to load",
                        "test_data": {"wait_time": 2000}
                    },
                    {
                        "action": "verify",
                        "description": "Verify search results displayed",
                        "element_selector": ".search-results"
                    }
                ]
            },
            "navigation": {
                "title": "Navigate through main menu",
                "type": "scenario",
                "tags": ["navigation", "menu"],
                "priority": "medium",
                "steps": [
                    {
                        "action": "click",
                        "description": "Click menu item",
                        "element_selector": kwargs.get("menu_selector", ".menu-item")
                    },
                    {
                        "action": "verify",
                        "description": "Verify page navigation",
                        "test_data": {"url": kwargs.get("expected_url", "/page")}
                    }
                ]
            }
        }
        
        return templates.get(scenario_type, cls._create_generic_template(**kwargs))
    
    @classmethod
    def _create_generic_template(cls, **kwargs) -> Dict[str, Any]:
        """Create a generic scenario template."""
        return {
            "title": kwargs.get("title", "Generic test scenario"),
            "type": "scenario",
            "tags": kwargs.get("tags", ["generic"]),
            "priority": kwargs.get("priority", "medium"),
            "steps": [
                {
                    "action": "navigate",
                    "description": "Navigate to test page",
                    "test_data": {"url": kwargs.get("url", "/")}
                },
                {
                    "action": "verify",
                    "description": "Verify page loaded",
                    "element_selector": "body"
                }
            ]
        }
    
    @classmethod
    def generate_test_data(
        cls,
        data_type: str,
        count: int = 3,
        include_invalid: bool = False
    ) -> List[Any]:
        """Generate test data for specific types."""
        if data_type in cls.DATA_TEMPLATES:
            valid_data = cls.DATA_TEMPLATES.get(data_type, [])
            
            if include_invalid:
                invalid_key = f"invalid_{data_type.replace('valid_', '')}"
                invalid_data = cls.DATA_TEMPLATES.get(invalid_key, [])
                return (valid_data + invalid_data)[:count]
            
            return valid_data[:count]
        
        # Generate dynamic data
        if data_type == "random_string":
            import string
            import random
            return [
                ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                for _ in range(count)
            ]
        
        elif data_type == "random_number":
            import random
            return [random.randint(1, 1000) for _ in range(count)]
        
        elif data_type == "timestamp":
            from datetime import datetime, timedelta
            now = datetime.now()
            return [
                (now + timedelta(days=i)).isoformat()
                for i in range(count)
            ]
        
        return []
    
    @classmethod
    def merge_scenarios(
        cls,
        scenarios: List[Dict[str, Any]],
        strategy: str = "combine"
    ) -> List[Dict[str, Any]]:
        """
        Merge similar scenarios to avoid duplication.
        
        Strategies:
        - combine: Combine similar scenarios into scenario outlines
        - dedupe: Remove exact duplicates
        - merge_steps: Merge scenarios with similar steps
        """
        if strategy == "dedupe":
            # Remove exact duplicates based on title and steps
            seen = set()
            unique_scenarios = []
            
            for scenario in scenarios:
                key = cls._generate_scenario_key(scenario)
                if key not in seen:
                    seen.add(key)
                    unique_scenarios.append(scenario)
            
            return unique_scenarios
        
        elif strategy == "combine":
            # Combine similar scenarios into outlines
            groups = cls._group_similar_scenarios(scenarios)
            combined_scenarios = []
            
            for group in groups:
                if len(group) > 1:
                    outline = cls._create_scenario_outline_from_group(group)
                    combined_scenarios.append(outline)
                else:
                    combined_scenarios.extend(group)
            
            return combined_scenarios
        
        else:
            return scenarios
    
    @classmethod
    def _generate_scenario_key(cls, scenario: Dict[str, Any]) -> str:
        """Generate a unique key for scenario comparison."""
        # Create key from essential elements
        key_parts = [
            scenario.get("title", ""),
            len(scenario.get("steps", [])),
            ",".join(step.get("action", "") for step in scenario.get("steps", []))
        ]
        
        return "|".join(str(part) for part in key_parts)
    
    @classmethod
    def _group_similar_scenarios(
        cls,
        scenarios: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group scenarios that are similar enough to combine."""
        groups = []
        
        for scenario in scenarios:
            added_to_group = False
            
            for group in groups:
                if cls._are_scenarios_similar(scenario, group[0]):
                    group.append(scenario)
                    added_to_group = True
                    break
            
            if not added_to_group:
                groups.append([scenario])
        
        return groups
    
    @classmethod
    def _are_scenarios_similar(
        cls,
        scenario1: Dict[str, Any],
        scenario2: Dict[str, Any],
        threshold: float = 0.8
    ) -> bool:
        """Check if two scenarios are similar enough to combine."""
        # Compare step sequences
        steps1 = scenario1.get("steps", [])
        steps2 = scenario2.get("steps", [])
        
        if abs(len(steps1) - len(steps2)) > 2:
            return False
        
        # Compare step actions
        actions1 = [s.get("action", "") for s in steps1]
        actions2 = [s.get("action", "") for s in steps2]
        
        # Calculate similarity
        common_actions = set(actions1) & set(actions2)
        similarity = len(common_actions) / max(len(actions1), len(actions2))
        
        return similarity >= threshold
    
    @classmethod
    def _create_scenario_outline_from_group(
        cls,
        group: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a scenario outline from a group of similar scenarios."""
        # Use the first scenario as template
        template = group[0].copy()
        template["type"] = "scenario_outline"
        
        # Find varying data points
        examples = {}
        varying_indices = []
        
        # Compare steps to find variations
        for i, step in enumerate(template.get("steps", [])):
            values = []
            
            for scenario in group:
                if i < len(scenario.get("steps", [])):
                    step_data = scenario["steps"][i].get("test_data", {})
                    value = step_data.get("value", "")
                    values.append(value)
            
            # If values vary, create parameter
            if len(set(values)) > 1:
                param_name = f"param_{i}"
                examples[param_name] = values
                step["test_data"]["value"] = f"<{param_name}>"
                varying_indices.append(i)
        
        # Add expected results if they vary
        expected_results = [s.get("expected_result", "") for s in group]
        if len(set(expected_results)) > 1:
            examples["expected_result"] = expected_results
        
        if examples:
            template["examples"] = examples
        
        # Update title to reflect outline nature
        template["title"] = template.get("title", "").replace(
            "with", "with different"
        )
        
        return template
    
    @classmethod
    def optimize_scenarios(
        cls,
        scenarios: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimize scenarios for better maintainability and execution."""
        optimized = []
        
        for scenario in scenarios:
            optimized_scenario = scenario.copy()
            
            # Optimize steps
            optimized_steps = []
            prev_action = None
            
            for step in scenario.get("steps", []):
                # Skip redundant waits
                if step.get("action") == "wait" and prev_action == "wait":
                    continue
                
                # Combine consecutive fills into single step if same element
                if (step.get("action") == "fill" and 
                    prev_action == "fill" and
                    len(optimized_steps) > 0 and
                    step.get("element_selector") == optimized_steps[-1].get("element_selector")):
                    
                    # Combine values
                    prev_value = optimized_steps[-1]["test_data"].get("value", "")
                    new_value = step["test_data"].get("value", "")
                    optimized_steps[-1]["test_data"]["value"] = prev_value + new_value
                    continue
                
                optimized_steps.append(step)
                prev_action = step.get("action")
            
            optimized_scenario["steps"] = optimized_steps
            
            # Add default timeout if not specified
            for step in optimized_scenario["steps"]:
                if "timeout" not in step:
                    step["timeout"] = 10
            
            optimized.append(optimized_scenario)
        
        return optimized