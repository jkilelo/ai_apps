"""
Infrastructure Profile Definitions
AI-First profiles for different use cases: POC, Local, Open Source, Enterprise
"""

from typing import Dict, List, Any
from decimal import Decimal
from models import (
    Profile,
    ProfileType,
    LLMProvider,
    TargetScale,
    CostType,
    InclusionType,
    DependencyType,
)


# ============================================
# Profile Templates (AI-First by Design)
# ============================================

class ProfileTemplates:
    """Pre-configured infrastructure profiles for different use cases"""

    @staticmethod
    def poc_profile() -> Dict[str, Any]:
        """
        POC Profile: Leanest configuration for quick proof-of-concept
        - Minimal infrastructure
        - Single developer
        - Gemini AI for cost-effectiveness
        - Local SQLite, no containers
        - < 2 hours setup time
        """
        return {
            "code": "poc_minimal",
            "name": "POC Minimal - Quick Prototype",
            "description": "Absolute minimum setup for rapid prototyping and demos. AI-first with Gemini, local databases, no containers.",
            "profile_type": ProfileType.POC,
            "is_ai_first": True,
            "default_llm_provider": LLMProvider.GEMINI,
            "target_users": 1,
            "target_scale": TargetScale.DEVELOPMENT,
            "max_monthly_budget": Decimal("50.00"),
            "requires_internet": True,
            "requires_gpu": False,
            "min_ram_gb": 8,
            "min_storage_gb": 50,
            "min_cpu_cores": 2,
            "compliance_requirements": [],
            "metadata": {
                "setup_time_estimate": "1-2 hours",
                "maintenance_level": "minimal",
                "suitable_for": ["demos", "hackathons", "learning", "experiments"],
                "not_suitable_for": ["production", "team_development", "customer_data"],
            },
            "components": {
                # Core Runtime (Essential Only)
                "python_3.13": {"inclusion": InclusionType.REQUIRED, "priority": 1},
                "uv_package_manager": {"inclusion": InclusionType.REQUIRED, "priority": 2},
                "vscode": {"inclusion": InclusionType.REQUIRED, "priority": 3},
                "git": {"inclusion": InclusionType.REQUIRED, "priority": 4},

                # AI Components (Gemini Only)
                "gemini_api": {
                    "inclusion": InclusionType.REQUIRED,
                    "priority": 5,
                    "config": {"model": "gemini-2.5-flash", "free_tier": True}
                },
                "langchain_core": {"inclusion": InclusionType.REQUIRED, "priority": 6},

                # Minimal Backend
                "fastapi": {"inclusion": InclusionType.REQUIRED, "priority": 7},
                "pydantic_v2": {"inclusion": InclusionType.REQUIRED, "priority": 8},
                "sqlite3": {"inclusion": InclusionType.REQUIRED, "priority": 9},

                # Minimal Frontend
                "html5_css3_vanilla": {"inclusion": InclusionType.REQUIRED, "priority": 10},

                # Testing (Minimal)
                "pytest": {"inclusion": InclusionType.OPTIONAL, "priority": 11},

                # Explicitly Excluded for POC
                "docker": {"inclusion": InclusionType.EXCLUDED},
                "kubernetes": {"inclusion": InclusionType.EXCLUDED},
                "postgresql": {"inclusion": InclusionType.EXCLUDED},
                "redis": {"inclusion": InclusionType.EXCLUDED},
                "react": {"inclusion": InclusionType.EXCLUDED},
            }
        }

    @staticmethod
    def local_development_profile() -> Dict[str, Any]:
        """
        Local Development Profile: Single developer, full-featured local setup
        - Complete development environment
        - Local containers with Podman
        - Gemini + optional local LLM
        - Local databases
        - < 8 hours setup time
        """
        return {
            "code": "local_dev",
            "name": "Local Development - Single Developer",
            "description": "Complete local development environment for individual developers. AI-first with Gemini, local databases, containerized services.",
            "profile_type": ProfileType.LOCAL,
            "parent_profile_id": None,  # Can inherit from POC
            "is_ai_first": True,
            "default_llm_provider": LLMProvider.GEMINI,
            "target_users": 1,
            "target_scale": TargetScale.DEVELOPMENT,
            "max_monthly_budget": Decimal("100.00"),
            "requires_internet": True,
            "requires_gpu": False,
            "min_ram_gb": 16,
            "min_storage_gb": 100,
            "min_cpu_cores": 4,
            "compliance_requirements": [],
            "metadata": {
                "setup_time_estimate": "4-8 hours",
                "maintenance_level": "moderate",
                "suitable_for": ["development", "testing", "learning", "small_projects"],
                "features": ["hot_reload", "debugging", "local_testing", "containerization"],
                "optional_enhancements": ["local_llm", "gpu_acceleration"],
            },
            "components": {
                # Core Runtime
                "python_3.13": {"inclusion": InclusionType.REQUIRED, "priority": 1},
                "nodejs_22_lts": {"inclusion": InclusionType.REQUIRED, "priority": 2},
                "uv_package_manager": {"inclusion": InclusionType.REQUIRED, "priority": 3},
                "pnpm": {"inclusion": InclusionType.REQUIRED, "priority": 4},

                # Development Tools
                "vscode": {"inclusion": InclusionType.REQUIRED, "priority": 5},
                "vscode_extensions": {"inclusion": InclusionType.REQUIRED, "priority": 6},
                "git": {"inclusion": InclusionType.REQUIRED, "priority": 7},
                "github_cli": {"inclusion": InclusionType.OPTIONAL, "priority": 8},

                # Containers
                "podman": {"inclusion": InclusionType.REQUIRED, "priority": 9},
                "podman_compose": {"inclusion": InclusionType.REQUIRED, "priority": 10},

                # AI Components
                "gemini_api": {
                    "inclusion": InclusionType.REQUIRED,
                    "priority": 11,
                    "config": {"model": "gemini-2.5-pro", "free_tier": False}
                },
                "ollama": {
                    "inclusion": InclusionType.ALTERNATIVE,
                    "priority": 12,
                    "config": {"models": ["llama3.2", "codellama"], "gpu": False}
                },
                "langchain": {"inclusion": InclusionType.REQUIRED, "priority": 13},
                "langgraph": {"inclusion": InclusionType.REQUIRED, "priority": 14},
                "mcp_sdk": {"inclusion": InclusionType.REQUIRED, "priority": 15},

                # Databases
                "postgresql_17": {"inclusion": InclusionType.REQUIRED, "priority": 16},
                "falkordb": {"inclusion": InclusionType.REQUIRED, "priority": 17},
                "redis": {"inclusion": InclusionType.REQUIRED, "priority": 18},
                "meilisearch": {"inclusion": InclusionType.OPTIONAL, "priority": 19},

                # Backend
                "fastapi": {"inclusion": InclusionType.REQUIRED, "priority": 20},
                "pydantic_v2": {"inclusion": InclusionType.REQUIRED, "priority": 21},
                "sqlalchemy_2": {"inclusion": InclusionType.REQUIRED, "priority": 22},
                "alembic": {"inclusion": InclusionType.REQUIRED, "priority": 23},

                # Frontend
                "react_19": {"inclusion": InclusionType.REQUIRED, "priority": 24},
                "typescript": {"inclusion": InclusionType.REQUIRED, "priority": 25},
                "tailwind_css_4": {"inclusion": InclusionType.REQUIRED, "priority": 26},
                "vite": {"inclusion": InclusionType.REQUIRED, "priority": 27},

                # Testing & Quality
                "pytest": {"inclusion": InclusionType.REQUIRED, "priority": 28},
                "playwright": {"inclusion": InclusionType.OPTIONAL, "priority": 29},
                "ruff": {"inclusion": InclusionType.REQUIRED, "priority": 30},
                "mypy": {"inclusion": InclusionType.REQUIRED, "priority": 31},

                # Monitoring (Local)
                "prometheus": {"inclusion": InclusionType.OPTIONAL, "priority": 32},
                "grafana": {"inclusion": InclusionType.OPTIONAL, "priority": 33},
            }
        }

    @staticmethod
    def opensource_profile() -> Dict[str, Any]:
        """
        Open Source Profile: 100% open source, no proprietary APIs
        - All components open source
        - Local/self-hosted LLMs only
        - Self-hosted services
        - Community-driven tools
        - < 16 hours setup time
        """
        return {
            "code": "opensource_pure",
            "name": "100% Open Source Stack",
            "description": "Completely open source infrastructure with no proprietary dependencies. Self-hosted AI with Ollama or open models.",
            "profile_type": ProfileType.OPENSOURCE,
            "is_ai_first": True,
            "default_llm_provider": LLMProvider.OLLAMA,
            "target_users": 10,
            "target_scale": TargetScale.STAGING,
            "max_monthly_budget": Decimal("200.00"),  # Infrastructure costs only
            "requires_internet": True,
            "requires_gpu": True,  # Recommended for local LLMs
            "min_ram_gb": 32,
            "min_storage_gb": 500,
            "min_cpu_cores": 8,
            "compliance_requirements": ["open_source_only"],
            "metadata": {
                "setup_time_estimate": "8-16 hours",
                "maintenance_level": "high",
                "suitable_for": ["privacy_focused", "air_gapped", "research", "education"],
                "license_requirements": ["MIT", "Apache-2.0", "GPL", "BSD"],
                "gpu_recommendations": {
                    "minimum": "NVIDIA GTX 1660 (6GB)",
                    "recommended": "NVIDIA RTX 3090 (24GB)",
                    "optimal": "NVIDIA A100 (40GB)",
                },
            },
            "components": {
                # Core Runtime (Open Source)
                "python_3.13": {"inclusion": InclusionType.REQUIRED, "priority": 1},
                "nodejs_22_lts": {"inclusion": InclusionType.REQUIRED, "priority": 2},
                "uv_package_manager": {"inclusion": InclusionType.REQUIRED, "priority": 3},
                "rust": {"inclusion": InclusionType.OPTIONAL, "priority": 4},

                # Development Tools (Open Source)
                "vscodium": {"inclusion": InclusionType.REQUIRED, "priority": 5},
                "git": {"inclusion": InclusionType.REQUIRED, "priority": 6},
                "lazygit": {"inclusion": InclusionType.OPTIONAL, "priority": 7},

                # Containers (Open Source)
                "podman": {"inclusion": InclusionType.REQUIRED, "priority": 8},
                "podman_compose": {"inclusion": InclusionType.REQUIRED, "priority": 9},
                "kubernetes_k3s": {"inclusion": InclusionType.OPTIONAL, "priority": 10},

                # AI Components (Open Source Only)
                "ollama": {
                    "inclusion": InclusionType.REQUIRED,
                    "priority": 11,
                    "config": {
                        "models": ["llama3.2:70b", "mixtral:8x7b", "codellama:34b"],
                        "gpu": True,
                        "parallel_models": 2,
                    }
                },
                "localai": {
                    "inclusion": InclusionType.ALTERNATIVE,
                    "priority": 11,
                    "config": {"models": ["vicuna", "wizardlm"]}
                },
                "huggingface_transformers": {"inclusion": InclusionType.OPTIONAL, "priority": 12},
                "langchain_community": {"inclusion": InclusionType.REQUIRED, "priority": 13},
                "llamaindex": {"inclusion": InclusionType.OPTIONAL, "priority": 14},

                # Databases (Open Source)
                "postgresql_17": {"inclusion": InclusionType.REQUIRED, "priority": 15},
                "falkordb": {"inclusion": InclusionType.REQUIRED, "priority": 16},
                "redis": {"inclusion": InclusionType.REQUIRED, "priority": 17},
                "qdrant": {"inclusion": InclusionType.REQUIRED, "priority": 18},
                "meilisearch": {"inclusion": InclusionType.REQUIRED, "priority": 19},
                "mongodb_community": {"inclusion": InclusionType.OPTIONAL, "priority": 20},

                # Backend (Open Source)
                "fastapi": {"inclusion": InclusionType.REQUIRED, "priority": 21},
                "django": {"inclusion": InclusionType.ALTERNATIVE, "priority": 21},
                "pydantic_v2": {"inclusion": InclusionType.REQUIRED, "priority": 22},
                "sqlalchemy_2": {"inclusion": InclusionType.REQUIRED, "priority": 23},

                # Frontend (Open Source)
                "react_19": {"inclusion": InclusionType.REQUIRED, "priority": 24},
                "vue_3": {"inclusion": InclusionType.ALTERNATIVE, "priority": 24},
                "typescript": {"inclusion": InclusionType.REQUIRED, "priority": 25},
                "tailwind_css_4": {"inclusion": InclusionType.REQUIRED, "priority": 26},
                "vite": {"inclusion": InclusionType.REQUIRED, "priority": 27},

                # Workflow & Automation (Open Source)
                "n8n_selfhosted": {"inclusion": InclusionType.REQUIRED, "priority": 28},
                "apache_airflow": {"inclusion": InclusionType.ALTERNATIVE, "priority": 28},

                # Monitoring (Open Source)
                "prometheus": {"inclusion": InclusionType.REQUIRED, "priority": 29},
                "grafana": {"inclusion": InclusionType.REQUIRED, "priority": 30},
                "opentelemetry": {"inclusion": InclusionType.REQUIRED, "priority": 31},
                "jaeger": {"inclusion": InclusionType.OPTIONAL, "priority": 32},

                # Security (Open Source)
                "hashicorp_vault": {"inclusion": InclusionType.OPTIONAL, "priority": 33},
                "keycloak": {"inclusion": InclusionType.OPTIONAL, "priority": 34},

                # Explicitly Excluded (Proprietary)
                "gemini_api": {"inclusion": InclusionType.EXCLUDED},
                "openai_api": {"inclusion": InclusionType.EXCLUDED},
                "anthropic_api": {"inclusion": InclusionType.EXCLUDED},
                "azure_services": {"inclusion": InclusionType.EXCLUDED},
                "aws_services": {"inclusion": InclusionType.EXCLUDED},
                "gcp_services": {"inclusion": InclusionType.EXCLUDED},
            }
        }

    @staticmethod
    def enterprise_profile() -> Dict[str, Any]:
        """
        Enterprise Profile: Production-ready, scalable, compliant
        - Full security and compliance
        - Multi-LLM support with fallbacks
        - Kubernetes orchestration
        - Complete observability
        - < 40 hours setup time
        """
        return {
            "code": "enterprise_production",
            "name": "Enterprise Production Stack",
            "description": "Production-grade infrastructure with full security, compliance, and scalability. Multi-LLM support, Kubernetes, complete observability.",
            "profile_type": ProfileType.ENTERPRISE,
            "is_ai_first": True,
            "default_llm_provider": LLMProvider.GEMINI,  # Primary with fallbacks
            "target_users": 1000,
            "target_scale": TargetScale.PRODUCTION,
            "max_monthly_budget": Decimal("10000.00"),
            "requires_internet": True,
            "requires_gpu": True,
            "min_ram_gb": 64,
            "min_storage_gb": 1000,
            "min_cpu_cores": 16,
            "compliance_requirements": ["SOC2", "GDPR", "HIPAA", "ISO27001"],
            "metadata": {
                "setup_time_estimate": "20-40 hours",
                "maintenance_level": "managed",
                "suitable_for": ["production", "enterprise", "saas", "regulated_industries"],
                "sla_requirements": {
                    "uptime": "99.99%",
                    "response_time_p99": "100ms",
                    "data_retention": "7_years",
                    "backup_frequency": "hourly",
                    "disaster_recovery": "multi_region",
                },
                "team_requirements": {
                    "devops": 2,
                    "security": 1,
                    "developers": 5,
                    "ai_engineers": 2,
                },
            },
            "components": {
                # Core Runtime
                "python_3.13": {"inclusion": InclusionType.REQUIRED, "priority": 1},
                "nodejs_22_lts": {"inclusion": InclusionType.REQUIRED, "priority": 2},
                "java_21_lts": {"inclusion": InclusionType.OPTIONAL, "priority": 3},
                "go_1.22": {"inclusion": InclusionType.OPTIONAL, "priority": 4},

                # Package Management
                "uv_package_manager": {"inclusion": InclusionType.REQUIRED, "priority": 5},
                "npm_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 6},
                "artifactory": {"inclusion": InclusionType.OPTIONAL, "priority": 7},

                # Development Tools
                "vscode": {"inclusion": InclusionType.REQUIRED, "priority": 8},
                "github_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 9},
                "gitlab_ee": {"inclusion": InclusionType.ALTERNATIVE, "priority": 9},

                # Container Orchestration
                "docker_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 10},
                "kubernetes_eks": {"inclusion": InclusionType.REQUIRED, "priority": 11},
                "helm": {"inclusion": InclusionType.REQUIRED, "priority": 12},
                "istio": {"inclusion": InclusionType.OPTIONAL, "priority": 13},

                # AI Components (Multi-Provider)
                "gemini_api": {
                    "inclusion": InclusionType.REQUIRED,
                    "priority": 14,
                    "config": {"model": "gemini-2.5-pro", "enterprise_agreement": True}
                },
                "openai_api": {
                    "inclusion": InclusionType.REQUIRED,
                    "priority": 15,
                    "config": {"model": "gpt-5", "azure_openai": True}
                },
                "anthropic_api": {
                    "inclusion": InclusionType.ALTERNATIVE,
                    "priority": 16,
                    "config": {"model": "claude-4-opus"}
                },
                "bedrock": {
                    "inclusion": InclusionType.ALTERNATIVE,
                    "priority": 17,
                    "config": {"region": "us-east-1"}
                },

                # AI Infrastructure
                "langchain": {"inclusion": InclusionType.REQUIRED, "priority": 18},
                "langgraph_platform": {"inclusion": InclusionType.REQUIRED, "priority": 19},
                "langsmith": {"inclusion": InclusionType.REQUIRED, "priority": 20},
                "mcp_sdk": {"inclusion": InclusionType.REQUIRED, "priority": 21},
                "mcp_security": {"inclusion": InclusionType.REQUIRED, "priority": 22},

                # Databases (High Availability)
                "postgresql_17_ha": {"inclusion": InclusionType.REQUIRED, "priority": 23},
                "falkordb_cluster": {"inclusion": InclusionType.REQUIRED, "priority": 24},
                "redis_cluster": {"inclusion": InclusionType.REQUIRED, "priority": 25},
                "qdrant_cloud": {"inclusion": InclusionType.REQUIRED, "priority": 26},
                "elasticsearch": {"inclusion": InclusionType.REQUIRED, "priority": 27},
                "mongodb_atlas": {"inclusion": InclusionType.OPTIONAL, "priority": 28},

                # Backend
                "fastapi": {"inclusion": InclusionType.REQUIRED, "priority": 29},
                "pydantic_v2": {"inclusion": InclusionType.REQUIRED, "priority": 30},
                "sqlalchemy_2": {"inclusion": InclusionType.REQUIRED, "priority": 31},
                "alembic": {"inclusion": InclusionType.REQUIRED, "priority": 32},
                "celery": {"inclusion": InclusionType.REQUIRED, "priority": 33},

                # API Gateway
                "kong_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 34},
                "nginx_plus": {"inclusion": InclusionType.ALTERNATIVE, "priority": 34},

                # Frontend
                "react_19": {"inclusion": InclusionType.REQUIRED, "priority": 35},
                "nextjs_14": {"inclusion": InclusionType.OPTIONAL, "priority": 36},
                "typescript": {"inclusion": InclusionType.REQUIRED, "priority": 37},
                "tailwind_css_4": {"inclusion": InclusionType.REQUIRED, "priority": 38},

                # CDN & Edge
                "cloudflare_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 39},
                "fastly": {"inclusion": InclusionType.ALTERNATIVE, "priority": 39},

                # Workflow & Automation
                "n8n_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 40},
                "github_actions": {"inclusion": InclusionType.REQUIRED, "priority": 41},
                "argo_workflows": {"inclusion": InclusionType.OPTIONAL, "priority": 42},

                # Testing & Quality
                "pytest": {"inclusion": InclusionType.REQUIRED, "priority": 43},
                "playwright": {"inclusion": InclusionType.REQUIRED, "priority": 44},
                "selenium_grid": {"inclusion": InclusionType.OPTIONAL, "priority": 45},
                "sonarqube": {"inclusion": InclusionType.REQUIRED, "priority": 46},
                "snyk": {"inclusion": InclusionType.REQUIRED, "priority": 47},

                # Monitoring & Observability
                "datadog": {"inclusion": InclusionType.REQUIRED, "priority": 48},
                "new_relic": {"inclusion": InclusionType.ALTERNATIVE, "priority": 48},
                "prometheus": {"inclusion": InclusionType.REQUIRED, "priority": 49},
                "grafana_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 50},
                "opentelemetry": {"inclusion": InclusionType.REQUIRED, "priority": 51},
                "sentry": {"inclusion": InclusionType.REQUIRED, "priority": 52},

                # Security & Compliance
                "hashicorp_vault_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 53},
                "okta": {"inclusion": InclusionType.REQUIRED, "priority": 54},
                "auth0": {"inclusion": InclusionType.ALTERNATIVE, "priority": 54},
                "cloudflare_waf": {"inclusion": InclusionType.REQUIRED, "priority": 55},
                "veracode": {"inclusion": InclusionType.REQUIRED, "priority": 56},
                "crowdstrike": {"inclusion": InclusionType.OPTIONAL, "priority": 57},

                # Backup & Disaster Recovery
                "velero": {"inclusion": InclusionType.REQUIRED, "priority": 58},
                "aws_backup": {"inclusion": InclusionType.REQUIRED, "priority": 59},
                "veeam": {"inclusion": InclusionType.ALTERNATIVE, "priority": 59},

                # Communication & Incident Management
                "slack_enterprise": {"inclusion": InclusionType.REQUIRED, "priority": 60},
                "pagerduty": {"inclusion": InclusionType.REQUIRED, "priority": 61},
                "jira": {"inclusion": InclusionType.REQUIRED, "priority": 62},
            }
        }

    @staticmethod
    def hybrid_profile() -> Dict[str, Any]:
        """
        Hybrid Profile: Balance between open source and commercial
        - Mix of open source and commercial tools
        - Gemini primary with Ollama fallback
        - Partial self-hosting
        - < 12 hours setup time
        """
        return {
            "code": "hybrid_balanced",
            "name": "Hybrid Balanced Stack",
            "description": "Balanced mix of open source and commercial tools. Gemini for primary AI with local fallback options.",
            "profile_type": ProfileType.HYBRID,
            "is_ai_first": True,
            "default_llm_provider": LLMProvider.GEMINI,
            "target_users": 50,
            "target_scale": TargetScale.STAGING,
            "max_monthly_budget": Decimal("500.00"),
            "requires_internet": True,
            "requires_gpu": False,  # Optional
            "min_ram_gb": 24,
            "min_storage_gb": 250,
            "min_cpu_cores": 6,
            "compliance_requirements": [],
            "metadata": {
                "setup_time_estimate": "6-12 hours",
                "maintenance_level": "moderate",
                "suitable_for": ["small_teams", "startups", "mvp", "pilot_projects"],
                "cost_optimization": {
                    "strategy": "use_free_tiers",
                    "fallback_to_opensource": True,
                    "auto_scaling": True,
                },
            },
            "components": {
                # Inherit most from local_dev but add:
                "parent_profile": "local_dev",

                # Additional AI Options
                "groq_api": {
                    "inclusion": InclusionType.ALTERNATIVE,
                    "priority": 20,
                    "config": {"model": "mixtral-8x7b", "for": "fast_inference"}
                },

                # Cloud Services (Limited)
                "vercel": {"inclusion": InclusionType.OPTIONAL, "priority": 30},
                "supabase": {"inclusion": InclusionType.OPTIONAL, "priority": 31},
                "railway": {"inclusion": InclusionType.OPTIONAL, "priority": 32},

                # Monitoring (Free Tier)
                "sentry_free": {"inclusion": InclusionType.REQUIRED, "priority": 40},
                "posthog": {"inclusion": InclusionType.OPTIONAL, "priority": 41},
            }
        }


# ============================================
# Component Selection Rules
# ============================================

class ComponentSelectionRules:
    """Rules for component selection based on profile requirements"""

    @staticmethod
    def get_ai_components_for_profile(profile_type: ProfileType) -> List[Dict[str, Any]]:
        """Get AI components based on profile type"""
        rules = {
            ProfileType.POC: [
                {"provider": "gemini", "required": True, "model": "gemini-2.5-flash"},
            ],
            ProfileType.LOCAL: [
                {"provider": "gemini", "required": True, "model": "gemini-2.5-pro"},
                {"provider": "ollama", "required": False, "model": "llama3.2"},
            ],
            ProfileType.OPENSOURCE: [
                {"provider": "ollama", "required": True, "model": "mixtral:8x7b"},
                {"provider": "localai", "required": False, "model": "vicuna"},
            ],
            ProfileType.ENTERPRISE: [
                {"provider": "gemini", "required": True, "model": "gemini-2.5-pro"},
                {"provider": "openai", "required": True, "model": "gpt-5"},
                {"provider": "anthropic", "required": False, "model": "claude-4-opus"},
            ],
            ProfileType.HYBRID: [
                {"provider": "gemini", "required": True, "model": "gemini-2.5-pro"},
                {"provider": "groq", "required": False, "model": "mixtral-8x7b"},
                {"provider": "ollama", "required": False, "model": "llama3.2"},
            ],
        }
        return rules.get(profile_type, [])

    @staticmethod
    def validate_ai_first_requirement(components: List[str]) -> bool:
        """Validate that at least one AI component is present"""
        ai_components = [
            "gemini_api", "openai_api", "anthropic_api", "groq_api",
            "ollama", "localai", "huggingface_transformers",
            "bedrock", "vertex_ai", "azure_openai"
        ]
        return any(comp in components for comp in ai_components)

    @staticmethod
    def estimate_profile_cost(profile_type: ProfileType, users: int = 1) -> Dict[str, Decimal]:
        """Estimate monthly costs for a profile"""
        base_costs = {
            ProfileType.POC: {"min": Decimal("0"), "max": Decimal("50")},
            ProfileType.LOCAL: {"min": Decimal("20"), "max": Decimal("100")},
            ProfileType.OPENSOURCE: {"min": Decimal("50"), "max": Decimal("200")},
            ProfileType.ENTERPRISE: {"min": Decimal("2000"), "max": Decimal("10000")},
            ProfileType.HYBRID: {"min": Decimal("100"), "max": Decimal("500")},
        }

        costs = base_costs.get(profile_type, {"min": Decimal("0"), "max": Decimal("0")})

        # Scale costs based on users
        if users > 1:
            multiplier = Decimal(str(1 + (users - 1) * 0.7))  # 70% cost increase per additional user
            costs["min"] *= multiplier
            costs["max"] *= multiplier

        return costs

    @staticmethod
    def get_setup_complexity(profile_type: ProfileType) -> int:
        """Get setup complexity score (1-5)"""
        complexity_map = {
            ProfileType.POC: 1,
            ProfileType.LOCAL: 2,
            ProfileType.OPENSOURCE: 4,
            ProfileType.ENTERPRISE: 5,
            ProfileType.HYBRID: 3,
        }
        return complexity_map.get(profile_type, 3)


# ============================================
# Profile Factory
# ============================================

class ProfileFactory:
    """Factory for creating and managing profiles"""

    _templates = {
        ProfileType.POC: ProfileTemplates.poc_profile,
        ProfileType.LOCAL: ProfileTemplates.local_development_profile,
        ProfileType.OPENSOURCE: ProfileTemplates.opensource_profile,
        ProfileType.ENTERPRISE: ProfileTemplates.enterprise_profile,
        ProfileType.HYBRID: ProfileTemplates.hybrid_profile,
    }

    @classmethod
    def create_profile(cls, profile_type: ProfileType, **overrides) -> Profile:
        """Create a profile instance with optional overrides"""
        if profile_type not in cls._templates:
            raise ValueError(f"Unknown profile type: {profile_type}")

        template_func = cls._templates[profile_type]
        template_data = template_func()

        # Extract components before creating Profile
        components = template_data.pop("components", {})

        # Apply overrides
        template_data.update(overrides)

        # Create Profile instance
        profile = Profile(**template_data)

        # Attach components as metadata for now
        profile.metadata["components"] = components

        return profile

    @classmethod
    def list_available_profiles(cls) -> List[str]:
        """List all available profile types"""
        return [pt.value for pt in ProfileType]

    @classmethod
    def get_profile_comparison(cls) -> Dict[str, Dict[str, Any]]:
        """Get comparison matrix of all profiles"""
        comparison = {}
        for profile_type in ProfileType:
            template_func = cls._templates.get(profile_type)
            if template_func:
                template_data = template_func()
                comparison[profile_type.value] = {
                    "name": template_data["name"],
                    "users": template_data["target_users"],
                    "scale": template_data["target_scale"],
                    "budget": float(template_data["max_monthly_budget"]),
                    "ram_gb": template_data["min_ram_gb"],
                    "gpu_required": template_data["requires_gpu"],
                    "setup_hours": template_data["metadata"].get("setup_time_estimate", "Unknown"),
                    "ai_provider": template_data["default_llm_provider"],
                    "components_count": len(template_data.get("components", {})),
                }
        return comparison


# ============================================
# Export Configuration
# ============================================

__all__ = [
    "ProfileTemplates",
    "ComponentSelectionRules",
    "ProfileFactory",
]