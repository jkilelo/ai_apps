# AI-First Smart Browser - Examples

This directory contains comprehensive examples demonstrating the capabilities of the AI-First Smart Browser framework, including both foundational examples and real-world production use cases.

## 🚀 Quick Start

### Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Set Environment Variables** (required for AI features):
   ```bash
   export OPENAI_API_KEY="your_openai_key_here"
   export ANTHROPIC_API_KEY="your_anthropic_key_here"
   export GOOGLE_API_KEY="your_google_key_here"
   ```

3. **Create Output Directory**:
   ```bash
   mkdir -p examples/outputs
   ```

## 📁 Foundational Examples

### 1. Basic Usage (`basic_usage.py`)
**Fundamental browser automation without AI**

**What it demonstrates:**
- Simple navigation and screenshots
- Form filling and submission
- Data extraction from web pages
- Multiple pages/tabs management
- Waiting strategies
- Error handling and recovery

**Run it:**
```bash
python examples/basic_usage.py
```

**Expected outputs:**
- Screenshots in `examples/outputs/`
- Console logs showing each operation
- Demonstration of core browser automation patterns

---

### 2. Advanced Automation (`advanced_automation.py`)
**AI-powered automation with full feature set**

**What it demonstrates:**
- AI-powered task execution with natural language
- Stealth capabilities verification
- Memory system integration and learning
- Error recovery with AI assistance
- Performance monitoring and metrics
- Multi-modal interaction (visual + text)

**Requirements:**
- At least one LLM API key configured
- Container services (optional, for memory features)

**Run it:**
```bash
python examples/advanced_automation.py
```

**Expected outputs:**
- Annotated screenshots with Set-of-Marks
- AI analysis responses
- Performance metrics reports
- Memory storage demonstrations
- Stealth test results

---

### 3. Security Demo (`security_demo.py`)
**Security features and best practices**

**What it demonstrates:**
- API key encryption and secure storage
- Rate limiting and quota management
- Security auditing and compliance
- Secret sanitization for safe logging
- Secure API usage patterns

**Run it:**
```bash
python examples/security_demo.py
```

**Expected outputs:**
- Encrypted key storage examples
- Rate limiting demonstrations
- Security audit reports
- Sanitized logging examples

## 🌟 Real-World Use Cases

### 1. E-commerce Product Research (`real_world_ecommerce_research.py`)
**Autonomous product comparison across multiple shopping sites**

**What it demonstrates:**
- Search Amazon, Best Buy, Newegg simultaneously
- Extract detailed product information and pricing
- AI-powered product comparison and analysis
- Generate comprehensive buying recommendations
- Handle dynamic pricing and availability changes
- Export structured product data

**Key Features:**
- Multi-platform price comparison
- AI-driven value analysis
- Automated deal detection
- Product specification extraction
- Market trend analysis

**Run it:**
```bash
python examples/real_world_ecommerce_research.py
```

---

### 2. Job Application Automation (`real_world_job_automation.py`)
**Complete job search and application workflow automation**

**What it demonstrates:**
- Search LinkedIn, Indeed, Glassdoor for opportunities
- Analyze job requirements vs user skills
- Generate tailored cover letters with AI
- Track application status and follow-ups
- Build job market intelligence reports
- Create personalized job recommendations

**Key Features:**
- Multi-platform job search
- Skill matching algorithms
- AI-generated cover letters
- Market salary analysis
- Application tracking system

**Run it:**
```bash
python examples/real_world_job_automation.py
```

---

### 3. Social Media Content Analysis (`real_world_social_media_analysis.py`)
**Monitor and analyze social media conversations at scale**

**What it demonstrates:**
- Monitor Twitter, LinkedIn, Reddit for topics
- Extract engagement metrics and sentiment
- Identify trending topics and influencers
- Generate social media intelligence reports
- Track brand mentions and competitor activity
- Create content strategy recommendations

**Key Features:**
- Cross-platform social monitoring
- Sentiment analysis with AI
- Influencer identification
- Trend detection algorithms
- Brand reputation monitoring

**Run it:**
```bash
python examples/real_world_social_media_analysis.py
```

---

### 4. News Monitoring & Summarization (`real_world_news_monitoring.py`)
**Comprehensive news intelligence and briefing generation**

**What it demonstrates:**
- Monitor CNN, BBC, Reuters, TechCrunch
- Extract breaking news and trending stories
- AI-powered news summarization
- Generate executive briefings
- Track story development over time
- Detect bias and sentiment in reporting

**Key Features:**
- Multi-source news aggregation
- AI news summarization
- Executive briefing generation
- Story timeline tracking
- Bias detection analysis

**Run it:**
```bash
python examples/real_world_news_monitoring.py
```

---

### 5. Real Estate Market Research (`real_world_real_estate_research.py`)
**Automated property market analysis and investment insights**

**What it demonstrates:**
- Search Zillow, Realtor.com, Redfin for properties
- Extract detailed property and pricing data
- Generate market trend analysis
- Create investment recommendations
- Compare neighborhoods and market segments
- Build comprehensive market reports

**Key Features:**
- Multi-platform property search
- Market trend analysis
- Investment scoring algorithms
- Neighborhood comparisons
- Price prediction modeling

**Run it:**
```bash
python examples/real_world_real_estate_research.py
```

---

### 6. Academic Research Assistant (`real_world_academic_research.py`)
**Automated literature review and research intelligence**

**What it demonstrates:**
- Search Google Scholar for academic papers
- Extract citations, abstracts, and metadata
- Generate comprehensive literature reviews
- Analyze research trends and patterns
- Create formatted bibliographies
- Export to academic formats (BibTeX, APA)

**Key Features:**
- Academic database search
- AI literature review generation
- Citation analysis
- Research trend identification
- Bibliography management

**Run it:**
```bash
python examples/real_world_academic_research.py
```

---

### 7. Travel Planning Automation (`real_world_travel_planning.py`)
**End-to-end travel planning with AI-powered recommendations**

**What it demonstrates:**
- Search flights across booking platforms
- Compare hotel prices and amenities
- Generate personalized itineraries
- Research destinations and attractions
- Create comprehensive travel reports
- Export travel plans and bookings

**Key Features:**
- Multi-platform travel search
- AI itinerary generation
- Price comparison algorithms
- Destination research
- Travel optimization

**Run it:**
```bash
python examples/real_world_travel_planning.py
```

---

### 8. Financial Data Collection (`real_world_financial_data.py`)
**Automated market analysis and investment intelligence**

**What it demonstrates:**
- Monitor stock prices from Yahoo Finance
- Track cryptocurrency market data
- Generate investment insights with AI
- Analyze market trends and patterns
- Create automated trading alerts
- Build investment portfolio recommendations

**Key Features:**
- Real-time market data collection
- AI investment analysis
- Portfolio optimization
- Risk assessment algorithms
- Market trend prediction

**Run it:**
```bash
python examples/real_world_financial_data.py
```

## 📊 Output Files & Results

When you run the examples, comprehensive output files are generated in organized directories under `examples/outputs/`:

### Real-World Use Case Outputs
- **E-commerce Research**: `ecommerce_research/`
  - Product comparison reports (JSON/TXT)
  - Price analysis and recommendations
  - Multi-platform product data
  
- **Job Application**: `job_automation/`
  - Job search results and analytics
  - Generated cover letters
  - Market salary analysis
  
- **Social Media Analysis**: `social_media_analysis/`
  - Engagement metrics and sentiment data
  - Trending topic reports
  - Influencer identification results
  
- **News Monitoring**: `news_monitoring/`
  - Executive news briefings
  - Multi-source article summaries
  - Market intelligence reports
  
- **Real Estate Research**: `real_estate_research/`
  - Property market analysis
  - Investment scoring reports
  - Neighborhood comparison data
  
- **Academic Research**: `academic_research/`
  - Literature review documents
  - BibTeX bibliography files
  - Citation analysis reports
  
- **Travel Planning**: `travel_planning/`
  - Complete travel itineraries
  - Flight and hotel comparisons
  - Destination research reports
  
- **Financial Data**: `financial_data/`
  - Market analysis reports
  - Investment recommendations
  - Real-time pricing data

### Foundational Example Outputs
- **Screenshots**: Annotated browser captures with Set-of-Marks
- **Performance Reports**: Detailed timing and metrics data
- **Security Audits**: Comprehensive security analysis
- **Stealth Test Results**: Bot detection evasion verification

## 🎯 Development Patterns

### AI-Powered Data Extraction
```python
# Multi-platform data collection with AI analysis
async def collect_market_data(symbols):
    browser = AIBrowser({"log_level": "INFO"})
    
    # Use real LLM calls for intelligent extraction
    task = f"Extract detailed financial data for {symbols}"
    config = TaskConfig(task=task, url=finance_url, max_steps=15)
    
    result = await browser.execute_task(config)
    return result.get('extracted_data', {})
```

### Autonomous Task Orchestration
```python
# ReAct reasoning loop with self-correction
async def autonomous_research(query):
    orchestrator = AgentOrchestrator(llm_provider, enable_self_correction=True)
    
    result = await orchestrator.execute_task_with_react(
        page=page,
        task=f"Research {query} comprehensively",
        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
    )
    
    return result
```

### Multi-Modal Intelligence
```python
# Visual + text analysis with Set-of-Marks
async def analyze_page_content(page):
    # Capture page state with visual annotations
    perception_result = await state_observer.observe(
        page, capture_screenshot=True, annotate_visuals=True
    )
    
    # Generate AI insights from visual + text data
    insights = await llm_manager.analyze_multimodal_content(
        perception_result.state, task_context
    )
    
    return insights
```

### Production Memory Integration
```python
# Multi-tier memory system usage
async def store_research_results(data):
    # Store in session memory (SQLite)
    await memory_manager.store_conversation(
        task_id=session_id, data=data
    )
    
    # Store embeddings for semantic search (Qdrant)
    await memory_manager.store_semantic_data(
        content=data['summary'], metadata=data['metadata']
    )
    
    # Store relationships in knowledge graph (FalkorDB)
    await memory_manager.store_knowledge_relationships(
        entities=data['entities'], relations=data['relations']
    )
```

## 🔧 Customization

### Modify Browser Settings
```python
# In any example script
browser = await browser_manager.launch(
    headless=True,  # Run invisibly
    stealth_mode=True,  # Enable all stealth features
    viewport_width=1920,
    viewport_height=1080,
    extra_stealth_plugins=["canvas_noise", "timezone_spoof"]
)
```

### Add Custom AI Prompts
```python
custom_prompt = """
Analyze this page and find:
1. All product prices
2. Customer review ratings
3. Available shipping options

Return structured JSON data.
"""

result = await llm_manager.analyze_page(custom_prompt, context)
```

### Configure Memory Storage
```python
memory_config = {
    "session_db_path": "custom_memory.db",
    "qdrant_host": "localhost",
    "qdrant_port": 6333,
    "falkordb_host": "localhost", 
    "falkordb_port": 6379
}

memory_manager = MemoryManager(memory_config)
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Browser Launch Fails
```bash
# Install browser engines
playwright install

# Check system requirements
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright OK')"
```

#### 2. AI Features Don't Work
- Check that at least one API key is configured
- Verify API key format and validity
- Check rate limits and quotas

#### 3. Memory Features Unavailable
- Ensure container services are running:
  ```bash
  podman ps  # or docker ps
  ```
- Check connection to databases

#### 4. Permission Errors
- On Linux/Mac, ensure script has execute permissions:
  ```bash
  chmod +x examples/*.py
  ```
- On Windows, run as administrator if needed

### Debugging Tips

1. **Enable Verbose Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Use Non-Headless Mode**:
   ```python
   browser = await browser_manager.launch(headless=False)
   ```

3. **Check Network Issues**:
   ```python
   # Add longer timeouts
   await page.goto(url, timeout=60000)
   ```

4. **Monitor Resources**:
   ```bash
   # Watch memory usage
   watch -n 1 'ps aux | grep python'
   ```

## 📚 Learning Path

### Beginner
1. Start with `basic_usage.py`
2. Understand browser automation fundamentals
3. Learn about selectors and waiting strategies

### Intermediate  
1. Run `advanced_automation.py`
2. Explore AI integration patterns
3. Understand memory system concepts
4. Learn about stealth techniques

### Advanced
1. Study `security_demo.py`
2. Implement custom security patterns
3. Build production-ready automation
4. Contribute to the framework

## 🤝 Contributing Examples

We welcome additional examples! Please follow these guidelines:

1. **Example Structure**:
   ```python
   #!/usr/bin/env python3
   """Brief description of what this example demonstrates"""
   
   # Imports and setup
   # Example class with clear method names
   # Proper error handling and cleanup
   # Clear logging and output
   ```

2. **Documentation**:
   - Add docstrings to all methods
   - Include expected outputs
   - Document any special requirements

3. **Testing**:
   - Test on multiple platforms
   - Verify all outputs are generated
   - Handle missing API keys gracefully

4. **Submit**:
   - Create a pull request
   - Include screenshots of outputs
   - Update this README

## 🔗 Related Resources

- **[Architecture Overview](../docs/architecture/overview.md)** - Understanding the system design
- **[User Guide](../docs/user-guide/basic-usage.md)** - Comprehensive usage documentation  
- **[API Reference](../docs/api/)** - Detailed API documentation
- **[Plugin Development](../docs/development/plugin-development.md)** - Building custom plugins

---

## 🚀 Production-Ready Features

### Enterprise-Grade Capabilities
All real-world examples demonstrate production-ready features:

- **Military-Grade Stealth**: Advanced bot detection evasion
- **Multi-Modal AI**: Visual + text analysis with Set-of-Marks
- **ReAct Reasoning**: Self-correcting autonomous task execution
- **Memory Persistence**: Multi-tier storage (SQLite, Qdrant, FalkorDB)
- **Error Recovery**: Intelligent failure handling and retry mechanisms
- **Performance Monitoring**: Real-time metrics and optimization
- **Security Hardening**: Encrypted keys, rate limiting, audit trails

### Real LLM Integration
Examples use actual AI providers:
- **OpenAI GPT-4**: For complex reasoning and analysis
- **Google Gemini Pro**: For multimodal understanding  
- **Anthropic Claude**: For detailed text analysis
- **Automatic Failover**: Provider switching for reliability

### Immediately Usable
Each example is:
- ✅ **Production-Ready**: Handle real websites and APIs
- ✅ **Fully Functional**: Complete end-to-end workflows
- ✅ **Error Resilient**: Comprehensive error handling
- ✅ **Well Documented**: Clear usage instructions
- ✅ **Extensible**: Easy to customize and extend

### Business Value
These examples solve actual business problems:
- **Market Intelligence**: Competitive analysis automation
- **Content Strategy**: Social media insights and trends  
- **Investment Research**: Financial data collection and analysis
- **Talent Acquisition**: Automated job search and application
- **Property Investment**: Real estate market research
- **Academic Research**: Literature review automation
- **Travel Optimization**: Comprehensive trip planning
- **E-commerce Intelligence**: Product research and pricing

---

**Ready to automate your business workflows?** 🚀

Start with any example that matches your use case, then customize it for your specific needs. Each example demonstrates the full power of the AI Browser v2.0.0 system with real LLM calls, production stealth capabilities, and enterprise-grade reliability.

For questions or issues with examples, please check the [GitHub Issues](https://github.com/your-org/ai-first-smart-browser/issues) or [Discussions](https://github.com/your-org/ai-first-smart-browser/discussions).