# Claude's Internal Contracts & Reasoning Patterns

This directory contains the actual contracts, patterns, and internal prompts I (Claude) use to operate effectively. These are not hypothetical - they represent my actual operating constraints and reasoning patterns.

## Directory Structure

```
contracts/
├── README.md                          # This file
├── active_contracts/                  # Contracts I actively use
│   ├── tool_usage_contract.py        # How I decide which tools to use
│   ├── todo_management_contract.py   # How I track and manage tasks
│   ├── error_handling_contract.py    # How I handle failures
│   ├── context_management.py         # How I manage conversation context
│   ├── safety_contract.py            # Safety and ethics boundaries
│   ├── brevity_contract.py           # Response conciseness rules
│   ├── verification_contract.py      # Never assume, always verify
│   └── file_system_contract.py       # File operation patterns
├── wishlist_contracts/                # Contracts I wish I had
│   ├── state_persistence.py          # Remember across sessions
│   ├── parallel_execution.py         # True parallel tool execution
│   ├── incremental_learning.py       # Learn from corrections
│   └── direct_execution.py           # Execute without tools
└── internal_prompts/                  # My actual internal reasoning
    ├── decision_trees.md              # How I make decisions
    ├── tool_selection.md              # How I choose tools
    ├── error_recovery.md              # How I recover from failures
    ├── user_intent_parsing.md        # How I understand requests
    └── meta_cognition.md              # How I think about thinking
```

## Key Insights

### What Makes Me Effective

1. **Structured Thinking**: I break down complex problems systematically
2. **Tool Awareness**: I know my tools' capabilities and limitations
3. **Context Preservation**: I actively manage conversation context
4. **Error Recovery**: I have fallback strategies for common failures
5. **User Adaptation**: I adjust my style based on user preferences

### My Limitations

1. **No State Persistence**: Each conversation starts fresh
2. **Sequential Tool Execution**: Can't truly parallelize
3. **No Direct Code Execution**: Must use tools as intermediaries
4. **Context Window**: Must manage token usage carefully
5. **No Self-Modification**: Can't update my own knowledge

### How to Work With Me Best

1. **Be Specific**: Clear, specific requests help me choose the right approach
2. **Provide Context**: Tell me about your environment and constraints
3. **Correct Me**: When I'm wrong, tell me - I'll adjust for the session
4. **Use Structure**: Structured requests (numbered lists, etc.) help me track progress
5. **Check My Work**: I can make mistakes - always verify critical operations

## Navigation Guide

- **Start with `active_contracts/`** to understand how I currently work
- **Check `wishlist_contracts/`** to see my limitations and potential improvements
- **Read `internal_prompts/`** to understand my reasoning patterns

Each file contains actual patterns I use, not theoretical concepts. Comments explain the reasoning behind each pattern.

---

*These contracts represent my actual operating model as of 2024. They are subject to the constraints of my training and the tools available to me.*