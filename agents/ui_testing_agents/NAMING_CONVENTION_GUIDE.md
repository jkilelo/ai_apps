# Professional Naming Convention Guide

## Naming Standards Applied

### 1. Folder Naming Convention
- **PascalCase** for main packages: `TestAutomationFramework`
- **snake_case** for Python packages: `test_automation_framework`
- **kebab-case** for documentation folders: `api-documentation`

### 2. File Naming Convention
- **snake_case** for Python modules: `llm_client.py`
- **PascalCase** for configuration: `Requirements.txt`
- **UPPERCASE** for environment files: `.env`, `LICENSE`
- **kebab-case** for scripts: `setup-windows.bat`

### 3. Class Naming (PascalCase)
- `SmartBrowserAgent` → `BrowserAutomationAgent`
- `UltimateTestAgent` → `TestOrchestrationAgent`

### 4. Function Naming (snake_case)
- Descriptive verbs: `generate_test_scenarios()`
- Clear purpose: `validate_api_contract()`

## Renaming Map

### Current → Professional Name

#### Root Level Files
```
llm.py                      → llm_client.py
test_portable.py            → system_verification.py
setup.py                    → setup_installer.py
setup.bat                   → setup-windows.bat
setup.sh                    → setup-unix.sh
requirements.txt            → Requirements.txt
.env.template              → .env.template
README.md                  → README.md
```

#### Main Package
```
workplace_agents_v2/        → test_automation_framework/
```

#### Core Modules
```
core.py                    → framework_core.py
llm_integration_v2.py      → ai_test_generator.py
browser_navigation_agent.py → browser_automation_agent.py
gherkin_generation_tools.py → bdd_test_generator.py
browser.py                 → browser_controller.py
ultimate_agents.py         → test_orchestration_agent.py
```

#### Execution Package
```
nexus_executor/            → test_execution_engine/
  sandbox.py              →   isolated_executor.py
  code_validator.py       →   syntax_validator.py
  test_runner.py         →   test_runner.py
```

#### Examples Folder
```
examples/                  → sample_implementations/
  01_ecommerce_checkout_test.py    → ecommerce_checkout_automation.py
  02_banking_security_test.py      → financial_security_validation.py
  03_social_media_test.py         → social_platform_automation.py
  04_api_integration_test.py      → api_contract_validation.py
  05_accessibility_compliance_test.py → wcag_compliance_validation.py
  quick_demo.py                    → quick_start_demo.py
  test_examples.py                 → validate_samples.py
```

## Variable Naming Conventions

### Before → After
```python
# Constants (UPPER_SNAKE_CASE)
max_scenarios = 5          → MAX_SCENARIOS = 5
api_timeout = 30          → API_TIMEOUT = 30

# Private variables (leading underscore)
llm_client = ...          → _llm_client = ...
internal_state = ...      → _internal_state = ...

# Public methods (descriptive verbs)
def generate_gherkin_with_llm()    → def generate_bdd_test_cases()
def enhance_code_with_llm()        → def enhance_code_quality()
def predict_flakiness_with_llm()   → def predict_test_stability()
```

## Import Statement Updates

### Before
```python
from workplace_agents_v2.llm_integration_v2 import generate_gherkin_with_llm
from workplace_agents_v2.browser_navigation_agent import SmartBrowserAgent
```

### After
```python
from test_automation_framework.ai_test_generator import generate_bdd_test_cases
from test_automation_framework.browser_automation_agent import BrowserAutomationAgent
```

## Professional Function Names

### Current → Professional
```
generate_gherkin_with_llm()         → generate_bdd_test_cases()
generate_playwright_code_with_llm()  → generate_automation_code()
generate_test_ids_with_llm()        → generate_element_identifiers()
generate_ai_scenarios_with_llm()    → generate_test_scenarios()
generate_test_data_with_llm()       → generate_test_datasets()
predict_flakiness_with_llm()        → predict_test_stability()
generate_visual_tests_with_llm()    → generate_visual_regression_tests()
analyze_accessibility_with_llm()    → analyze_accessibility_compliance()
generate_api_contracts_with_llm()   → generate_api_contracts()
optimize_execution_with_llm()       → optimize_test_execution()
enhance_code_with_llm()             → enhance_code_quality()
orchestrate_test_execution_with_llm() → orchestrate_test_suite()
generate_page_object_with_llm()     → generate_page_object_model()
generate_security_tests_with_llm()  → generate_security_validations()
validate_with_constitutional_ai()    → validate_ethical_compliance()
generate_api_tests_with_llm()       → generate_api_test_suite()
generate_performance_tests_with_llm() → generate_performance_benchmarks()
generate_accessibility_tests_with_llm() → generate_accessibility_suite()
```

## Class Name Updates

### Current → Professional
```python
SmartBrowserAgent           → BrowserAutomationAgent
UltimateTestAgent           → TestOrchestrationAgent
StealthBrowser              → SecureBrowserController
```

## Professional Package Structure

```
test_automation_framework/
├── __init__.py
├── framework_core.py           # Core framework initialization
├── ai_test_generator.py        # AI-powered test generation
├── browser_automation_agent.py # Browser automation
├── bdd_test_generator.py       # BDD/Gherkin generation
├── browser_controller.py       # Browser control layer
├── test_orchestration_agent.py # Test orchestration
└── sample_implementations/     # Example implementations
    ├── __init__.py
    ├── ecommerce_checkout_automation.py
    ├── financial_security_validation.py
    ├── social_platform_automation.py
    ├── api_contract_validation.py
    ├── wcag_compliance_validation.py
    ├── quick_start_demo.py
    └── validate_samples.py
```

## Environment Variable Names

### Current → Professional
```
OPENAI_API_KEY              → OPENAI_API_KEY (keep as is - industry standard)
ANTHROPIC_API_KEY           → ANTHROPIC_API_KEY (keep as is)
GOOGLE_API_KEY              → GOOGLE_API_KEY (keep as is)
PREFERRED_LLM_PROVIDER      → PREFERRED_AI_PROVIDER
LLM_TIMEOUT                 → AI_REQUEST_TIMEOUT
LLM_MAX_RETRIES            → AI_MAX_RETRY_ATTEMPTS
LLM_TEMPERATURE            → AI_RESPONSE_TEMPERATURE
```