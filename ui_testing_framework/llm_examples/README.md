# LLM Examples for QA Engineers

This directory contains comprehensive, working examples demonstrating how QA Engineers can use the LLM framework for test automation, analysis, and workflow optimization.

## 🚀 Quick Start

Run all examples at once:
```bash
python run_all_examples.py --all
```

Or run interactively:
```bash
python run_all_examples.py
```

## 📁 Example Categories

### 01. Basic Test Generation (`01_basic_test_generation.py`)
**Duration**: 2-3 minutes

Demonstrates fundamental test case generation for common QA scenarios:
- Login form testing
- Shopping cart functionality
- API endpoint testing
- Form validation
- Security testing (safe payloads only)

**What you'll learn**:
- Basic LLM query patterns for test generation
- Different test categories and approaches
- Structured test case formatting
- JSON output handling

**Run individually**:
```bash
python 01_basic_test_generation.py
```

### 02. Daily QA Workflows (`02_daily_qa_workflows.py`)
**Duration**: 3-4 minutes

Real-world QA scenarios that happen every day:
- Morning standup test coverage analysis
- Bug triage and rapid analysis
- Sprint planning test estimation
- Code review test gap identification
- Production incident response planning

**What you'll learn**:
- Time-pressured QA decision making
- Rapid analysis techniques
- Meeting preparation automation
- Cross-team communication templates

**Run individually**:
```bash
python 02_daily_qa_workflows.py
```

### 03. Advanced Strategies (`03_advanced_strategies.py`)
**Duration**: 4-5 minutes

Demonstrates 10 key master prompt strategies with QA examples:
- Chain of Thought - Systematic test breakdown
- Tree of Thoughts - Edge case discovery
- ReAct - Bug investigation
- Self-Consistency - Reliable test data
- Constitutional AI - Safe security testing
- Least-to-Most - Complex test planning
- Self-Refine - Test case improvement
- Generated Knowledge - Domain-specific testing
- Chain of Verification - Result validation
- Meta-Prompting - Strategy optimization

**What you'll learn**:
- When to use each strategy
- Performance vs quality trade-offs
- Strategy selection for different QA tasks
- Advanced prompting techniques

**Run individually**:
```bash
python 03_advanced_strategies.py
```

### 04. Automated Test Code Generation (`04_automated_test_code_generation.py`)
**Duration**: 3-4 minutes

Generate executable test code for multiple frameworks:
- **Playwright** (Python) - E-commerce login flow
- **Selenium** (Python) - Product search functionality
- **Cypress** (JavaScript) - Shopping cart operations
- **REST API** (Python) - User management system
- **Performance** (Locust) - Load testing scenarios
- **Mobile** (Appium) - Banking app testing
- **Utilities** - Reusable helper functions

**What you'll learn**:
- Framework-specific code generation
- Best practices implementation
- Page Object Model patterns
- Production-ready test structure

**Run individually**:
```bash
python 04_automated_test_code_generation.py
```

### 05. Batch Processing (`05_batch_processing.py`)
**Duration**: 4-5 minutes

Efficient processing of multiple QA tasks:
- Sequential batch feature testing
- Parallel async test generation
- Bulk test data creation
- Mass bug report analysis
- Multi-epic sprint planning
- Threaded CPU-bound processing

**What you'll learn**:
- Sequential vs parallel processing
- Async/await patterns for LLM calls
- ThreadPoolExecutor usage
- Performance optimization techniques

**Run individually**:
```bash
python 05_batch_processing.py
```

### 06. Production Utilities (`06_production_utilities.py`)
**Duration**: 2-3 minutes

Production-ready QA utilities and management tools:
- Test case management with SQLite database
- Automated metrics analysis
- QA reporting for management
- Test data generation and cleanup
- CSV export functionality
- Coverage analysis

**What you'll learn**:
- Database integration patterns
- Production-ready code structure
- Management reporting
- Data persistence strategies

**Run individually**:
```bash
python 06_production_utilities.py
```

## 🎯 Example Runner (`run_all_examples.py`)

The main runner provides multiple execution modes:

### Interactive Mode (Default)
```bash
python run_all_examples.py
```

### Run All Examples
```bash
python run_all_examples.py --all
```

### Run Specific Example
```bash
python run_all_examples.py --example 01
```

### List Available Examples
```bash
python run_all_examples.py --list
```

### Skip on Error
```bash
python run_all_examples.py --all --skip-on-error
```

## 📊 Generated Outputs

Each example creates specific outputs:

### Files Created
- `basic_test_generation_results.json` - Comprehensive test cases
- `daily_qa_workflows_results.json` - Workflow analysis results
- `advanced_strategies_results.json` - Strategy execution results
- `automated_test_generation_results.json` - Generated code metadata
- `batch_processing_results.json` - Batch operation results
- `qa_report_YYYYMMDD.md` - Management QA report
- `generated_test_cases.csv` - Exportable test cases
- `test_cases.db` - SQLite database with test cases

### Generated Code Directory
- `generated_code/playwright_login_tests.py` - Executable Playwright tests
- `generated_code/selenium_search_tests.py` - Selenium WebDriver tests
- `generated_code/api_user_management_tests.py` - REST API tests
- `generated_code/cypress_shopping_cart.spec.js` - Cypress JavaScript tests
- `generated_code/locust_performance_tests.py` - Load testing scripts
- `generated_code/appium_banking_tests.py` - Mobile app tests
- `generated_code/test_utilities.py` - Reusable utility functions

### Test Data Directory
- `test_data/user_profiles.json` - Generated user test data
- `test_data/product_data.json` - E-commerce product data
- `test_data/transaction_data.json` - Financial transaction data

## ⚙️ Requirements

All examples require:
- Python 3.8+
- LLM module (from parent directory)
- Valid API keys in `.env` file
- Internet connection for LLM API calls

## 🎨 Customization

### Modify Examples
Each example is self-contained and can be customized:
1. Edit the example file directly
2. Modify prompts and scenarios
3. Adjust output formats
4. Change strategy selections

### Add New Examples
To add new examples:
1. Create new Python file following naming pattern
2. Add entry to `run_all_examples.py` examples dictionary
3. Follow existing patterns for structure and output

## 📈 Performance Metrics

Typical execution times (with real LLM APIs):
- **Basic Test Generation**: 2-3 minutes
- **Daily QA Workflows**: 3-4 minutes
- **Advanced Strategies**: 4-5 minutes (10 strategies)
- **Test Code Generation**: 3-4 minutes
- **Batch Processing**: 4-5 minutes (includes parallel execution)
- **Production Utilities**: 2-3 minutes

**Total Runtime**: ~18-24 minutes for all examples

## 🔧 Troubleshooting

### Common Issues

**API Key Not Found**:
```
ERROR: API key not found
```
- Ensure `.env` file exists in parent directory
- Check API key format and validity

**Import Errors**:
```
ModuleNotFoundError: No module named 'llm'
```
- Run from the `llm_examples` directory
- Ensure parent directory contains `llm.py`

**Long Response Times**:
- Normal for real LLM calls (2-5 seconds each)
- Use `--skip-on-error` to stop on failures
- Check network connectivity

**Permission Errors**:
- Ensure write permissions for output files
- Check database file permissions

### Debug Mode

Add debug output to any example:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Best Practices

### When Using Examples in Production

1. **API Rate Limiting**: Add delays between calls for production
2. **Error Handling**: Enhance error handling for production use
3. **Logging**: Add comprehensive logging
4. **Configuration**: Move hardcoded values to config files
5. **Security**: Review generated content before execution
6. **Testing**: Add unit tests for production utilities

### Optimization Tips

1. **Batch Processing**: Use parallel execution for multiple items
2. **Caching**: Cache LLM responses for repeated queries
3. **Strategy Selection**: Choose appropriate strategies for speed vs quality
4. **Token Limits**: Optimize prompts to stay within token limits

## 💡 Next Steps

After running the examples:

1. **Integration**: Integrate patterns into your QA workflow
2. **Customization**: Adapt examples to your specific needs  
3. **Automation**: Build CI/CD integration using the patterns
4. **Training**: Use examples to train team members
5. **Scaling**: Implement batch processing for larger test suites

## 📞 Support

For issues with examples:
1. Check the troubleshooting section
2. Review individual example documentation
3. Verify API key configuration
4. Test with simple examples first

---

**Happy Testing with AI! 🚀**

*These examples demonstrate the full power of LLM-driven QA automation. Start with basic examples and progress to advanced patterns as you become comfortable with the framework.*