# 🏗️ Infrastructure Audit System

**AI-First Infrastructure Management with SQLite3 & Pydantic v2**

A comprehensive, modern infrastructure audit system designed for the AI era. Built once, use forever with minimal updates. Supports multiple deployment profiles from POC to Enterprise scale.

## 🌟 Key Features

### ✨ AI-First by Design
- **Mandatory LLM Integration**: Every profile MUST have at least one live LLM connection
- **Gemini Preferred**: Default to Google Gemini for cost-effectiveness and reliability
- **Multi-Provider Support**: Fallback chains for enterprise environments
- **Local LLM Options**: Ollama, LocalAI for privacy-focused deployments

### 🎯 Smart Profile System
- **POC Profile**: Absolute minimum for demos (< 2 hours setup)
- **Local Dev**: Complete development environment (< 8 hours setup)
- **Open Source**: 100% FOSS stack with local LLMs only
- **Enterprise**: Production-ready with full compliance (< 40 hours setup)
- **Hybrid**: Balanced mix of open source and commercial tools

### 🔧 Modern Architecture
- **Pydantic v2**: Type-safe models with validation and serialization
- **SQLite3**: Normalized schema with proper indexing and triggers
- **Async Support**: Parallel audit execution for performance
- **Rich CLI**: Beautiful command-line interface with progress indicators
- **Extensible**: Plugin architecture for custom components

### 📊 Comprehensive Tracking
- **Cost Estimation**: Per-component and profile-level cost analysis
- **Dependency Tracking**: Smart dependency resolution and conflict detection
- **Audit Trail**: Complete history of all system changes
- **Compatibility Matrix**: Version compatibility checking
- **Performance Metrics**: Setup time and complexity scoring

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install pydantic[email] typer[rich] sqlite3 asyncio

# Initialize system
python cli.py init
```

### Basic Usage

```bash
# List available profiles
python cli.py list-profiles

# Create a POC profile
python cli.py create-profile poc --budget 50 --llm gemini

# Get profile summary
python cli.py profile-summary poc_minimal

# Run infrastructure audit
python cli.py audit poc_minimal --env development

# Export profile configuration
python cli.py export-profile poc_minimal --format json
```

## 📋 Available Profiles

| Profile | Users | Budget/Month | Setup Time | AI Provider | Use Case |
|---------|-------|--------------|------------|-------------|----------|
| **POC** | 1 | $0-50 | 1-2 hours | Gemini Free | Demos, prototypes |
| **Local** | 1 | $20-100 | 4-8 hours | Gemini Pro + Ollama | Development |
| **OpenSource** | 10 | $50-200 | 8-16 hours | Ollama + Local | Privacy-focused |
| **Enterprise** | 1000 | $2000-10000 | 20-40 hours | Multi-provider | Production |
| **Hybrid** | 50 | $100-500 | 6-12 hours | Gemini + Options | Balanced approach |

## 🏗️ System Architecture

### Database Schema (SQLite3)
```sql
-- Core infrastructure hierarchy
layers → categories → components
            ↓
    profiles ← profile_components → components
            ↓
    audit_sessions → audit_results
```

### Pydantic v2 Models
- **Type Safety**: All data validated at runtime
- **Serialization**: JSON/YAML export with proper encoding
- **Computed Fields**: Dynamic calculations for costs and complexity
- **Validation Rules**: Business logic enforcement

### Component Registry
- **Hierarchical Organization**: Layers → Categories → Components
- **Rich Metadata**: Versions, costs, dependencies, documentation
- **Smart Search**: Filter by cost type, AI components, tags
- **Dependency Tracking**: Required, optional, alternative relationships

## 🎯 Profile Design Patterns

### AI-First Enforcement
```python
@field_validator("default_llm_provider")
@classmethod
def validate_ai_first(cls, v: LLMProvider, info) -> LLMProvider:
    if info.data.get("is_ai_first") and v == LLMProvider.LOCAL:
        metadata = info.data.get("metadata", {})
        if not metadata.get("local_llm_config"):
            raise ValueError("Local LLM requires configuration")
    return v
```

### Profile Inheritance
```python
# Hybrid profile inherits from Local Dev
"parent_profile": "local_dev",
"additional_components": {
    "groq_api": {"inclusion": "optional", "for": "fast_inference"}
}
```

### Cost-Aware Selection
```python
def estimate_profile_cost(profile_type: ProfileType, users: int) -> Dict[str, Decimal]:
    base_costs = {...}
    if users > 1:
        multiplier = Decimal(str(1 + (users - 1) * 0.7))
        costs["min"] *= multiplier
        costs["max"] *= multiplier
    return costs
```

## 🔍 Audit Engine

### Parallel Execution
```python
async def _run_parallel_audits(self, session: AuditSession,
                              components: List[Tuple[Component, Dict]]) -> List[AuditResult]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_component = {
            executor.submit(self._audit_component, session.id, comp, config): (comp, config)
            for comp, config in components
        }
        # Process results as they complete...
```

### AI Component Validation
```python
def _audit_ai_component(self, result: AuditResult, component: Component,
                       config: Dict[str, Any]) -> AuditResult:
    if "api_key" in config:
        result.status = AuditStatus.PASSED
    else:
        result.status = AuditStatus.FAILED
        result.error_message = "API key not configured"
    return result
```

## 📊 Example Usage Scenarios

### Scenario 1: Quick Demo Setup
```bash
# Create minimal POC profile
python cli.py create-profile poc --name "Demo Setup" --budget 25

# Audit readiness
python cli.py audit poc_minimal

# Expected output: 95%+ success rate, < 2 hour setup
```

### Scenario 2: Team Development
```bash
# Create local development profile
python cli.py create-profile local --users 5 --llm gemini

# Get detailed summary
python cli.py profile-summary local_dev

# Expected: $50-100/month, 4-8 hours setup, containerized services
```

### Scenario 3: Privacy-Focused Deployment
```bash
# Create open source profile
python cli.py create-profile opensource --llm ollama

# Check requirements
python cli.py profile-summary opensource_pure

# Expected: GPU required, local LLMs only, higher setup complexity
```

### Scenario 4: Enterprise Production
```bash
# Create enterprise profile
python cli.py create-profile enterprise --users 1000 --budget 5000

# Run comprehensive audit
python cli.py audit enterprise_production --env production

# Expected: Multi-provider AI, full observability, compliance ready
```

## 🛠️ Component Examples

### AI Components
```python
Component(
    code="gemini_api",
    name="Google Gemini API",
    is_ai_component=True,
    cost_type=CostType.USAGE_BASED,
    estimated_monthly_cost_min=Decimal("10.00"),
    estimated_monthly_cost_max=Decimal("100.00"),
    metadata={
        "models": ["gemini-1.5-flash", "gemini-1.5-pro"],
        "free_tier": "15 requests/minute",
        "enterprise_features": ["batch_processing", "fine_tuning"]
    }
)
```

### Infrastructure Components
```python
Component(
    code="postgresql_17",
    name="PostgreSQL 17",
    cost_type=CostType.FREE,
    setup_complexity=3,
    setup_time_minutes=120,
    resource_requirements=ResourceRequirements(
        min_ram_gb=4,
        min_storage_gb=20,
        min_cpu_cores=2
    )
)
```

## 📈 Performance & Scalability

### Database Optimization
- **WAL Mode**: Write-ahead logging for concurrency
- **Indexed Queries**: All foreign keys and search fields indexed
- **Automatic Maintenance**: Periodic VACUUM and ANALYZE
- **Connection Pooling**: Efficient resource management

### Caching Strategy
- **LRU Cache**: Component and profile caching
- **TTL**: 1-hour cache expiration
- **Invalidation**: Smart cache clearing on updates

### Audit Performance
- **Parallel Execution**: 4 concurrent component checks
- **Async I/O**: Non-blocking operation execution
- **Progress Tracking**: Real-time status updates

## 🔒 Security & Compliance

### Data Protection
- **No Secrets in DB**: API keys managed externally
- **Audit Trail**: Complete change history
- **Validation**: Pydantic v2 input validation
- **SQL Injection Protection**: Parameterized queries

### Enterprise Features
- **User Attribution**: Track who made changes
- **Environment Isolation**: Development/staging/production
- **Export Controls**: JSON/YAML configuration export
- **Backup System**: Automated database backups

## 🚦 Future Enhancements

### Phase 2 Features
- [ ] **Web UI**: React-based management interface
- [ ] **REST API**: FastAPI-based programmatic access
- [ ] **Real-time Monitoring**: Component health checking
- [ ] **Cost Optimization**: Automatic cost reduction suggestions

### Phase 3 Features
- [ ] **AI-Powered Recommendations**: LLM-based profile optimization
- [ ] **Integration Hub**: Terraform, Kubernetes, Ansible
- [ ] **Compliance Automation**: GDPR, SOC2, HIPAA checking
- [ ] **Multi-tenancy**: Organization and team management

## 📚 Technical Deep Dive

### Why SQLite3?
- **Zero Configuration**: No server setup required
- **ACID Compliance**: Full transaction support
- **Cross-Platform**: Works everywhere Python runs
- **Performance**: Faster than PostgreSQL for single-user scenarios
- **Backup**: Simple file-based backups

### Why Pydantic v2?
- **Type Safety**: Runtime validation with Python typing
- **Performance**: 10x faster than v1, Rust-powered core
- **Serialization**: Native JSON/YAML export
- **Extensibility**: Custom validators and computed fields
- **Modern**: Designed for Python 3.11+ and async workflows

### Design Patterns Used

#### Factory Pattern
```python
class ProfileFactory:
    _templates = {
        ProfileType.POC: ProfileTemplates.poc_profile,
        ProfileType.LOCAL: ProfileTemplates.local_development_profile,
        # ...
    }

    @classmethod
    def create_profile(cls, profile_type: ProfileType, **overrides) -> Profile:
        template_func = cls._templates[profile_type]
        template_data = template_func()
        template_data.update(overrides)
        return Profile(**template_data)
```

#### Repository Pattern
```python
class ComponentRegistry:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._cache: Dict[str, Any] = {}

    def get_component(self, code: str) -> Optional[Component]:
        if cache_key in self._cache:
            return self._cache[cache_key]
        # Database query and caching...
```

#### Observer Pattern
```python
# Database triggers for automatic timestamp updates
CREATE TRIGGER update_components_timestamp
AFTER UPDATE ON components
FOR EACH ROW
BEGIN
    UPDATE components SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone <repo>
cd infra_audit_system

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .

# Type checking
mypy .
```

### Adding New Profiles
1. Create profile template in `profiles.py`
2. Add validation rules if needed
3. Update documentation
4. Add test cases

### Adding New Components
1. Define component in registry
2. Add to appropriate profile templates
3. Create audit check logic
4. Update compatibility matrix

## 📄 License

MIT License - Build amazing AI-first infrastructure!

## 🙏 Acknowledgments

- **Pydantic Team**: For the amazing v2 rewrite
- **SQLite Team**: For the most deployed database engine
- **Rich/Typer**: For beautiful CLI experiences
- **Python Community**: For the incredible ecosystem

---

*Built with ❤️ for the AI-first future*