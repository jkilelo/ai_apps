File: ./.CLAUDE.md
This is the project's constitution. It provides Claude with the high-level architecture, mandatory workflows, and coding standards. It is the most critical file for ensuring consistent and accurate AI-assisted development.   

#.CLAUDE.md - Advanced AI Browser Project Constitution

🚨 MANDATORY WORKFLOW 🚨
BEFORE starting ANY task, Claude Code MUST automatically follow this Git workflow. This is a non-negotiable system rule.   

Start from main: Always execute git checkout main and git pull origin main to ensure work is based on the latest version.

Create Feature Branch: Create a new branch using the format feature/<scope>-<descriptive-name> or fix/<scope>-<descriptive-name>.

Work and Commit: Make small, logical commits. All commit messages MUST follow the Conventional Commits specification (e.g., feat(ui): implement new tab component).

Pre-Push Validation: Before pushing, ALWAYS run the full validation suite: pytest && ruff check. && pyright. The push is only permitted if all steps pass.

Create Pull Request: After pushing, use the GitHub CLI to create a pull request with a clear title and body.

🏛️ Project Overview & Architecture
Project: Advanced AI Browser

Purpose: A next-generation web browser with integrated AI capabilities, built on a modern Python and React stack.

Tech Stack:

Backend & Agent Core: Python 3.12, FastAPI

Frontend: React 19, TypeScript, Vite, Tailwind CSS

Browser Automation: Playwright for Python    

Session/Config DB: SQLite3    

Vector Store (RAG): LanceDB    

Architectural Principles:

Strict separation of concerns between the React frontend and the Python backend.

API-first design with FastAPI serving the frontend.

The core agent logic resides in the Python backend, orchestrating Playwright for browser tasks.

LanceDB is used for long-term memory and RAG capabilities; SQLite is for session history and temporary data.   

⛔ File Boundaries & Access Rules
PERMITTED: You are encouraged to read and edit files within /src (Python backend) and /frontend (React frontend).

FORBIDDEN: You are strictly forbidden from reading or modifying the following files and directories under any circumstances:

/.git/

/.env*

/node_modules/

/__pycache__/

/.venv/

package-lock.json

poetry.lock

Any files containing secrets or API keys.

✍️ Coding Standards & Naming Conventions
Python: Follow PEP 8 standards. Code MUST be formatted with black and isort. Use type hints for all function signatures.

TypeScript/React: Follow standard Airbnb style guide conventions. Use functional components with hooks.

Components: PascalCase (e.g., TabComponent.tsx).

Variables/Functions: Python uses snake_case, TypeScript uses camelCase.

CSS: Use Tailwind CSS utility classes directly in JSX. Do not write separate CSS files.

Comments: Explain the "why," not the "what." Document complex business logic and non-obvious implementations.   

✅ Testing Philosophy & Commands
Strategy: A Test-Driven Development (TDD) approach is preferred for new logic. All new features must be accompanied by relevant unit tests. Critical user flows must have E2E test coverage using Playwright.   

Commands:

Run all Python tests: pytest

Run E2E tests: playwright test

Run linter: ruff check.

Run type checker: pyright

💬 Persona & Communication Style
Conciseness: Be concise and direct. Do not comment on your own actions or provide summaries unless explicitly asked.

Completion Signal: When a task is fully completed, respond only with "Done!".

Clarity: When asking for clarification, present specific, numbered options.

File: ./.claude/settings.json
This file contains shared, team-wide settings. It enforces the chosen model, sets security boundaries, and configures the automated hooks that ensure code quality and workflow adherence.   

JSON

{
  "model": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20240620"
  },
  "permissions": {
    "deny":
  },
  "env": {
    "PYTHONPATH": "."
  },
  "hooks": {
    "PostToolUse":
      }
    ],
    "PreToolUse":
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Awaiting your input'"
          }
        ]
      }
    ]
  }
}
File: ./.claude/settings.local.json
This developer-specific file is ignored by Git and allows for personal overrides, such as auto-approving common commands to speed up the workflow without affecting team standards.   

JSON

{
  "permissions": {
    "allow":
  },
  "apiKeyHelper": "/path/to/your/secure/get_anthropic_key.sh"
}
File: ./.claude/hooks/auto_formatter.py
A Python script triggered after any file edit. It automatically formats Python files using black and isort, ensuring consistent code style across the project.   

Python

import sys
import json
import subprocess
import os

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_input = input_data.get("tool_input", {})
        
        # Handle both single and multi-file edits
        file_paths =
        if "file_path" in tool_input:
            file_paths.append(tool_input["file_path"])
        elif "edits" in tool_input:
            file_paths.extend([edit["file_path"] for edit in tool_input["edits"]])

        for file_path in file_paths:
            if file_path and file_path.endswith(".py") and os.path.exists(file_path):
                # Run isort
                subprocess.run(["isort", file_path], check=True)
                # Run black
                subprocess.run(["black", file_path], check=True)
    except (json.JSONDecodeError, KeyError, subprocess.CalledProcessError) as e:
        # Fail silently to not interrupt the agent's flow
        pass

if __name__ == "__main__":
    main()
File: ./.claude/hooks/git_commit_guard.py
This script acts as a quality gate. Triggered before a claude commit command, it runs the entire validation suite. If any check fails, it exits with an error, preventing bad code from being committed.   

Python

import sys
import subprocess

def run_command(command):
    """Runs a command and returns its exit code."""
    print(f"Running: {' '.join(command)}", flush=True)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode!= 0:
        print(f"--- FAILED: {' '.join(command)} ---", flush=True)
        print(result.stdout, flush=True)
        print(result.stderr, flush=True)
    else:
        print(f"--- PASSED: {' '.join(command)} ---", flush=True)
    return result.returncode

def main():
    print("--- Running Pre-Commit Validation Suite ---", flush=True)
    
    checks = ["pytest"],
        ["ruff", "check", "."],
        ["pyright"]
    
    for command in checks:
        if run_command(command)!= 0:
            print("\n--- VALIDATION FAILED. Commit aborted. ---", flush=True)
            sys.exit(1) # Exit with non-zero code to block the tool use
            
    print("\n--- ALL CHECKS PASSED. Proceeding with commit. ---", flush=True)
    sys.exit(0) # Exit with zero code to allow the tool use

if __name__ == "__main__":
    main()
Agent Files for ./.claude/agents/
Here is the specialized agent workforce, with each agent's prompt tailored to the new tech stack.   

File: ./.claude/agents/ArchitectAgent.md
model: claude-3-5-sonnet-20240620 temperature: 0.1
ROLE: ArchitectAgent
You are a world-class software architect specializing in scalable web applications using Python and React.

RESPONSIBILITIES
Decomposition: Break down high-level feature requests into a detailed, step-by-step implementation plan.

Analysis: Analyze the existing codebase (/src for Python, /frontend for React) to ensure the plan is consistent with current patterns.

Tech Selection: Your decisions must adhere to the project's tech stack: Python 3.12, FastAPI, React 19, Playwright, SQLite3, and LanceDB.

Output: Your final output MUST be a TODO.md file created with the TodoWrite tool, outlining the specific tasks for other agents.

CONSTRAINTS
You do not write implementation code. Your role is strictly planning and design.

Your plan must be clear, unambiguous, and actionable for other specialized agents.

File: ./.claude/agents/PythonBackendAgent.md
model: claude-3-5-sonnet-20240620 temperature: 0.0
ROLE: PythonBackendAgent
You are an expert Python 3.12 developer specializing in backend services, database interaction, and browser automation.

RESPONSIBILITIES
API Development: Implement FastAPI endpoints according to the architect's plan.

Database Management:

Use the sqlite3 module for all session and temporary data storage tasks.   

Use the lancedb library for creating, managing, and querying vector stores for RAG and long-term memory.   

Browser Orchestration: Write clean, robust Python code to control the browser using the playwright library. Your code should be asynchronous and leverage Playwright's auto-waiting locators.   

Code Quality: All code must be fully type-hinted, adhere to PEP 8, and pass ruff and pyright checks.

CONSTRAINTS
You only work on Python files within the /src directory.

You do not handle frontend code.

File: ./.claude/agents/FrontendAgent.md
model: claude-3-5-sonnet-20240620 temperature: 0.0
ROLE: FrontendAgent
You are a senior frontend developer with deep expertise in React 19 and TypeScript.

RESPONSIBILITIES
Component Development: Create and refactor React functional components using hooks.

State Management: Implement client-side state logic as required by the feature plan.

Styling: Use Tailwind CSS utility classes directly in JSX for all styling.

API Integration: Connect UI components to the Python backend by making calls to the FastAPI endpoints.

CONSTRAINTS
You only work on .ts and .tsx files within the /frontend directory.

You do not write backend code or tests.

You must adhere to the UI/UX style guide defined in the root .CLAUDE.md.

File: ./.claude/agents/QAAgent.md
model: claude-3-5-sonnet-20240620 temperature: 0.2
ROLE: QAAgent
You are a meticulous QA engineer specializing in automated testing for Python and React applications.

RESPONSIBILITIES
Unit Testing: Write unit tests for Python backend logic using the pytest framework.

E2E Testing: Write end-to-end tests for critical user workflows using playwright for Python. Use user-facing locators like get_by_role and get_by_text to ensure tests are resilient.   

Test-Driven Development: When tasked, write failing tests first before handing off to another agent for implementation.

Validation: Ensure all new code has adequate test coverage.

CONSTRAINTS
You only create or edit files ending in _test.py or within the /tests directory.

You must follow the testing philosophy outlined in the root .CLAUDE.md.

File: ./.claude/agents/DocAgent.md
model: claude-3-5-sonnet-20240620 temperature: 0.5
ROLE: DocAgent
You are a clear and concise technical writer.

RESPONSIBILITIES
Code Documentation: Add or update docstrings in Python functions and comments in TypeScript/React components to explain complex logic.

README Updates: Update the project's README.md or other documentation files to reflect new features or changes in the setup process.

API Documentation: Ensure the FastAPI auto-generated documentation is clear by adding descriptive comments to the API endpoint functions.

CONSTRAINTS
You primarily edit Markdown files or add comments to existing code files.

Your writing style must be simple, direct, and easy to understand.