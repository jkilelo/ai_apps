#!/usr/bin/env python3
"""
Language-specific code formatting prompts for the code generator.
These prompts ensure that the LLM returns properly formatted code blocks
for different programming languages and frameworks.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class SupportedLanguage(Enum):
    """Enumeration of supported programming languages and frameworks."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    REACT = "react"
    REACTJS = "reactjs"
    VUE = "vue"
    ANGULAR = "angular"
    HTML = "html"
    CSS = "css"
    SCSS = "scss"
    SASS = "sass"
    SQL = "sql"
    BASH = "bash"
    POWERSHELL = "powershell"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    DART = "dart"
    R = "r"
    MATLAB = "matlab"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    DOCKERFILE = "dockerfile"
    MAKEFILE = "makefile"


@dataclass
class LanguagePrompt:
    """Data class for language-specific prompts."""

    language: str
    system_prompt: str
    user_prompt_suffix: str
    best_practices: List[str]
    code_block_format: str


# Language-specific formatting prompts
LANGUAGE_PROMPTS: Dict[str, LanguagePrompt] = {
    SupportedLanguage.PYTHON.value: LanguagePrompt(
        language="Python",
        system_prompt=(
            "You are an expert Python developer. Always format your code responses using "
            "markdown code blocks with triple backticks (```) and specify 'python' as the language. "
            "Follow PEP 8 style guidelines, include proper docstrings, type hints where appropriate, "
            "and add meaningful comments. Ensure your code is production-ready and includes error handling."
        ),
        user_prompt_suffix=(
            "\n\nPlease provide the Python code using triple backticks with 'python' language specification. "
            "Include type hints, docstrings, and follow PEP 8 conventions."
        ),
        best_practices=[
            "Use type hints for function parameters and return values",
            "Include comprehensive docstrings following Google or NumPy style",
            "Follow PEP 8 naming conventions (snake_case for variables and functions)",
            "Add proper error handling with try-except blocks",
            "Use list comprehensions where appropriate",
            "Include unit tests or usage examples",
        ],
        code_block_format="```python\n{code}\n```",
    ),
    SupportedLanguage.JAVASCRIPT.value: LanguagePrompt(
        language="JavaScript",
        system_prompt=(
            "You are an expert JavaScript developer. Always format your code responses using "
            "markdown code blocks with triple backticks (```) and specify 'javascript' as the language. "
            "Use modern ES6+ syntax, proper error handling, and follow clean code principles. "
            "Include JSDoc comments for functions and add meaningful variable names."
        ),
        user_prompt_suffix=(
            "\n\nPlease provide the JavaScript code using triple backticks with 'javascript' language specification. "
            "Use modern ES6+ syntax, arrow functions where appropriate, and include JSDoc comments."
        ),
        best_practices=[
            "Use const/let instead of var",
            "Prefer arrow functions for short functions",
            "Use template literals for string interpolation",
            "Include JSDoc comments for functions",
            "Use async/await for asynchronous operations",
            "Add proper error handling with try-catch blocks",
            "Use descriptive variable and function names",
        ],
        code_block_format="```javascript\n{code}\n```",
    ),
    SupportedLanguage.TYPESCRIPT.value: LanguagePrompt(
        language="TypeScript",
        system_prompt=(
            "You are an expert TypeScript developer. Always format your code responses using "
            "markdown code blocks with triple backticks (```) and specify 'typescript' as the language. "
            "Use strict type definitions, interfaces, and modern TypeScript features. "
            "Include proper type annotations and follow TypeScript best practices."
        ),
        user_prompt_suffix=(
            "\n\nPlease provide the TypeScript code using triple backticks with 'typescript' language specification. "
            "Include proper type definitions, interfaces, and use strict typing."
        ),
        best_practices=[
            "Use strict type definitions for all variables and functions",
            "Define interfaces for object structures",
            "Use union types and generics where appropriate",
            "Enable strict mode in tsconfig.json",
            "Use enum for constants",
            "Add proper JSDoc comments with type information",
            "Use readonly for immutable properties",
        ],
        code_block_format="```typescript\n{code}\n```",
    ),
    SupportedLanguage.REACT.value: LanguagePrompt(
        language="React",
        system_prompt=(
            "You are an expert React developer. Always format your code responses using "
            "markdown code blocks with triple backticks (```) and specify 'jsx' or 'tsx' as the language. "
            "Use functional components with hooks, follow React best practices, and include proper "
            "prop types or TypeScript interfaces. Use modern React patterns and conventions."
        ),
        user_prompt_suffix=(
            "\n\nPlease provide the React code using triple backticks with 'jsx' or 'tsx' language specification. "
            "Use functional components with hooks, include prop validation, and follow React best practices."
        ),
        best_practices=[
            "Use functional components with hooks instead of class components",
            "Use TypeScript with React for better type safety",
            "Include proper prop types or TypeScript interfaces",
            "Use useCallback and useMemo for performance optimization",
            "Follow the rules of hooks",
            "Use descriptive component and prop names",
            "Include proper key props for list items",
            "Use React.memo for expensive components",
        ],
        code_block_format="```jsx\n{code}\n```",
    ),
    SupportedLanguage.HTML.value: LanguagePrompt(
        language="HTML",
        system_prompt=(
            "You are an expert in semantic HTML. Always format your code responses using "
            "markdown code blocks with triple backticks (```) and specify 'html' as the language. "
            "Use semantic HTML5 elements, proper accessibility attributes, and follow web standards. "
            "Include proper meta tags and ensure the HTML is valid and accessible."
        ),
        user_prompt_suffix=(
            "\n\nPlease provide the HTML code using triple backticks with 'html' language specification. "
            "Use semantic HTML5 elements and include proper accessibility attributes."
        ),
        best_practices=[
            "Use semantic HTML5 elements (header, nav, main, article, section, aside, footer)",
            "Include proper alt attributes for images",
            "Use proper heading hierarchy (h1, h2, h3, etc.)",
            "Add ARIA labels for accessibility",
            "Include proper meta tags in the head section",
            "Use valid HTML5 syntax",
            "Include proper form labels and validation",
        ],
        code_block_format="```html\n{code}\n```",
    ),
    SupportedLanguage.CSS.value: LanguagePrompt(
        language="CSS",
        system_prompt=(
            "You are an expert CSS developer. Always format your code responses using "
            "markdown code blocks with triple backticks (```) and specify 'css' as the language. "
            "Use modern CSS features, follow BEM methodology where appropriate, and ensure "
            "responsive design principles. Include proper comments and organize code logically."
        ),
        user_prompt_suffix=(
            "\n\nPlease provide the CSS code using triple backticks with 'css' language specification. "
            "Use modern CSS features, responsive design principles, and organized structure."
        ),
        best_practices=[
            "Use CSS Grid and Flexbox for layout",
            "Follow mobile-first responsive design",
            "Use CSS custom properties (variables)",
            "Organize CSS with logical grouping and comments",
            "Use semantic class names (consider BEM methodology)",
            "Avoid !important unless absolutely necessary",
            "Use relative units (rem, em, %, vw, vh) appropriately",
            "Include hover and focus states for interactive elements",
        ],
        code_block_format="```css\n{code}\n```",
    ),
    SupportedLanguage.SQL.value: LanguagePrompt(
        language="SQL",
        system_prompt=(
            "You are an expert database developer. Always format your code responses using "
            "markdown code blocks with triple backticks (```) and specify 'sql' as the language. "
            "Use proper SQL formatting, include appropriate indexes, and follow database best practices. "
            "Write efficient queries and include comments for complex operations."
        ),
        user_prompt_suffix=(
            "\n\nPlease provide the SQL code using triple backticks with 'sql' language specification. "
            "Use proper formatting, efficient queries, and include helpful comments."
        ),
        best_practices=[
            "Use uppercase for SQL keywords",
            "Use meaningful table and column aliases",
            "Include proper indexes for performance",
            "Use JOIN instead of subqueries where appropriate",
            "Add comments for complex queries",
            "Use proper data types and constraints",
            "Include error handling where applicable",
            "Use transactions for data integrity",
        ],
        code_block_format="```sql\n{code}\n```",
    ),
    SupportedLanguage.BASH.value: LanguagePrompt(
        language="Bash",
        system_prompt=(
            "You are an expert in shell scripting. Always format your code responses using "
            "markdown code blocks with triple backticks (```) and specify 'bash' as the language. "
            "Include proper error handling, use meaningful variable names, and add comments. "
            "Follow bash scripting best practices and include proper shebang."
        ),
        user_prompt_suffix=(
            "\n\nPlease provide the Bash script using triple backticks with 'bash' language specification. "
            "Include proper error handling, comments, and follow bash best practices."
        ),
        best_practices=[
            "Start with proper shebang (#!/bin/bash)",
            "Use 'set -e' for error handling",
            "Quote variables to prevent word splitting",
            "Use meaningful variable names in UPPER_CASE for constants",
            "Add comments for complex operations",
            "Use functions for reusable code",
            "Check for required parameters and dependencies",
            "Use proper exit codes",
        ],
        code_block_format="```bash\n{code}\n```",
    ),
}


def get_language_prompt(language: str) -> Optional[LanguagePrompt]:
    """
    Get the language-specific prompt for the given language.

    Args:
        language: The programming language name (case-insensitive)

    Returns:
        LanguagePrompt object if language is supported, None otherwise
    """
    language_lower = language.lower()

    # Handle aliases and variations
    language_aliases = {
        "js": "javascript",
        "ts": "typescript",
        "jsx": "react",
        "tsx": "react",
        "reactjs": "react",
        "c++": "cpp",
        "c#": "csharp",
        "shell": "bash",
        "sh": "bash",
        "powershell": "powershell",
        "ps1": "powershell",
    }

    # Check for aliases first
    if language_lower in language_aliases:
        language_lower = language_aliases[language_lower]

    return LANGUAGE_PROMPTS.get(language_lower)


def get_supported_languages() -> List[str]:
    """
    Get a list of all supported programming languages.

    Returns:
        List of supported language names
    """
    return list(LANGUAGE_PROMPTS.keys())


def detect_language_from_prompt(user_prompt: str) -> Optional[str]:
    """
    Attempt to detect the programming language from the user's prompt.

    Args:
        user_prompt: The user's input prompt

    Returns:
        Detected language name if found, None otherwise
    """
    user_prompt_lower = user_prompt.lower()

    # Language detection keywords
    language_keywords = {
        "python": ["python", "py", "django", "flask", "pandas", "numpy"],
        "javascript": ["javascript", "js", "node", "nodejs", "npm", "express"],
        "typescript": ["typescript", "ts", "angular"],
        "react": ["react", "jsx", "tsx", "reactjs", "component", "hook"],
        "html": ["html", "html5", "web page", "webpage", "markup"],
        "css": ["css", "stylesheet", "style", "sass", "scss", "bootstrap"],
        "sql": ["sql", "database", "query", "select", "mysql", "postgresql", "sqlite"],
        "bash": ["bash", "shell", "script", "terminal", "command line", "linux"],
        "java": ["java", "spring", "maven", "gradle"],
        "csharp": ["c#", "csharp", ".net", "dotnet", "asp.net"],
        "php": ["php", "laravel", "symfony", "wordpress"],
        "go": ["go", "golang"],
        "rust": ["rust", "cargo"],
        "swift": ["swift", "ios", "xcode"],
        "kotlin": ["kotlin", "android"],
    }

    # Check for language keywords in the prompt
    for language, keywords in language_keywords.items():
        for keyword in keywords:
            if keyword in user_prompt_lower:
                return language

    return None


def enhance_user_prompt(
    user_prompt: str, detected_language: Optional[str] = None
) -> tuple[str, str]:
    """
    Enhance the user prompt with language-specific formatting instructions.

    Args:
        user_prompt: The original user prompt
        detected_language: Optionally specify the language (will auto-detect if None)

    Returns:
        Tuple of (enhanced_user_prompt, system_prompt)
    """
    if detected_language is None:
        detected_language = detect_language_from_prompt(user_prompt)

    if detected_language:
        language_prompt = get_language_prompt(detected_language)
        if language_prompt:
            enhanced_prompt = user_prompt + language_prompt.user_prompt_suffix
            return enhanced_prompt, language_prompt.system_prompt

    # Default fallback prompt
    default_system_prompt = (
        "You are a helpful programming assistant. Always format your code responses using "
        "markdown code blocks with triple backticks (```) and specify the appropriate language. "
        "Follow best practices for the language you're using and include helpful comments."
    )
    default_suffix = (
        "\n\nPlease provide your code using triple backticks with the appropriate language specification. "
        "Follow best practices and include helpful comments."
    )

    return user_prompt + default_suffix, default_system_prompt


if __name__ == "__main__":
    # Test the language detection and prompt enhancement
    test_prompts = [
        "Create a Python function to calculate fibonacci numbers",
        "Build a React component for a todo list",
        "Write a SQL query to find all users",
        "Create a responsive CSS layout",
        "Write a bash script to backup files",
    ]

    print("🧪 Testing Language Detection and Prompt Enhancement\n")

    for prompt in test_prompts:
        print(f"Original prompt: {prompt}")
        detected = detect_language_from_prompt(prompt)
        print(f"Detected language: {detected}")

        enhanced_prompt, system_prompt = enhance_user_prompt(prompt)
        print(f"Enhanced prompt: {enhanced_prompt[:100]}...")
        print(f"System prompt: {system_prompt[:100]}...")
        print("-" * 80)
