"""
Core Infrastructure Audit System
Database management, component registry, and audit engine
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, date
from decimal import Decimal
from contextlib import contextmanager
import json
import logging
import hashlib
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import tempfile
import shutil

from pydantic import ValidationError
from models import (
    Layer, Category, Component, ComponentDependency, Alternative,
    Profile, ProfileComponent, ProfileRule, ValidationRule,
    AuditSession, AuditResult, CostEstimate, CompatibilityMatrix,
    ProfileSummary, DependencyGraph,
    ProfileType, LLMProvider, InclusionType, AuditStatus, Severity,
    CostType, DependencyType, TargetScale
)
from profiles import ProfileFactory, ComponentSelectionRules


# ============================================
# Configuration
# ============================================

class AuditSystemConfig:
    """Configuration for the audit system"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("infra_audit.db")
        self.schema_path = Path(__file__).parent / "schema.sql"
        self.cache_size = 1000
        self.cache_ttl = 3600  # 1 hour
        self.max_workers = 4
        self.backup_retention_days = 30
        self.enable_wal_mode = True
        self.enable_foreign_keys = True
        self.vacuum_threshold = 1000  # Operations before VACUUM


# ============================================
# Database Manager
# ============================================

class DatabaseManager:
    """SQLite database manager with connection pooling and migrations"""

    def __init__(self, config: AuditSystemConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._operations_count = 0

    def initialize_database(self) -> None:
        """Initialize database with schema"""
        try:
            with self.get_connection() as conn:
                # Read and execute schema
                with open(self.config.schema_path, 'r') as f:
                    schema_sql = f.read()

                conn.executescript(schema_sql)
                conn.commit()

                # Initialize schema version
                conn.execute(
                    "INSERT OR REPLACE INTO schema_versions (version, description) VALUES (?, ?)",
                    ("1.0.0", "Initial schema")
                )
                conn.commit()

                self.logger.info(f"Database initialized: {self.config.db_path}")

        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get database connection with proper configuration"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.config.db_path,
                timeout=30.0,
                check_same_thread=False
            )

            # Configure connection
            conn.row_factory = sqlite3.Row

            if self.config.enable_foreign_keys:
                conn.execute("PRAGMA foreign_keys = ON")

            if self.config.enable_wal_mode:
                conn.execute("PRAGMA journal_mode = WAL")

            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            conn.execute("PRAGMA temp_store = memory")

            yield conn

        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                self._operations_count += 1

                # Periodic maintenance
                if self._operations_count % self.config.vacuum_threshold == 0:
                    self._vacuum_database()

    def _vacuum_database(self) -> None:
        """Perform database maintenance"""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
            self.logger.info("Database maintenance completed")
        except Exception as e:
            self.logger.error(f"Database maintenance failed: {e}")

    def backup_database(self, backup_path: Optional[Path] = None) -> Path:
        """Create database backup"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.config.db_path.parent / f"backup_{timestamp}.db"

        try:
            shutil.copy2(self.config.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise

    def cleanup_old_backups(self) -> None:
        """Remove old backup files"""
        backup_dir = self.config.db_path.parent
        cutoff_date = datetime.now().timestamp() - (self.config.backup_retention_days * 86400)

        for backup_file in backup_dir.glob("backup_*.db"):
            if backup_file.stat().st_mtime < cutoff_date:
                backup_file.unlink()
                self.logger.info(f"Removed old backup: {backup_file}")


# ============================================
# Component Registry
# ============================================

class ComponentRegistry:
    """Registry for infrastructure components with metadata"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, Any] = {}

    def register_component(self, component: Component) -> int:
        """Register a new component"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO components (
                        code, name, category_id, layer_id, description,
                        version_min, version_recommended, version_latest,
                        is_required, is_ai_component, is_opensource, license_type,
                        documentation_url, repository_url, cost_type,
                        estimated_monthly_cost_min, estimated_monthly_cost_max,
                        setup_complexity, setup_time_minutes,
                        resource_requirements, tags, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    component.code, component.name, component.category_id, component.layer_id,
                    component.description, component.version_min, component.version_recommended,
                    component.version_latest, component.is_required, component.is_ai_component,
                    component.is_opensource, component.license_type,
                    str(component.documentation_url) if component.documentation_url else None,
                    str(component.repository_url) if component.repository_url else None,
                    component.cost_type, float(component.estimated_monthly_cost_min),
                    float(component.estimated_monthly_cost_max), component.setup_complexity,
                    component.setup_time_minutes,
                    json.dumps(component.resource_requirements.model_dump()) if component.resource_requirements else None,
                    json.dumps(component.tags), json.dumps(component.metadata)
                ))

                component_id = cursor.lastrowid
                conn.commit()

                # Clear cache
                self._cache.clear()

                self.logger.info(f"Registered component: {component.code} (ID: {component_id})")
                return component_id

        except sqlite3.IntegrityError as e:
            self.logger.error(f"Component registration failed - duplicate code: {component.code}")
            raise ValueError(f"Component code already exists: {component.code}")
        except Exception as e:
            self.logger.error(f"Component registration failed: {e}")
            raise

    def get_component(self, code: str) -> Optional[Component]:
        """Get component by code"""
        cache_key = f"component:{code}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            with self.db.get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM components WHERE code = ?", (code,)
                ).fetchone()

                if not row:
                    return None

                component = self._row_to_component(row)
                self._cache[cache_key] = component
                return component

        except Exception as e:
            self.logger.error(f"Failed to get component {code}: {e}")
            return None

    def search_components(self,
                         layer_id: Optional[int] = None,
                         category_id: Optional[int] = None,
                         is_ai_component: Optional[bool] = None,
                         cost_type: Optional[CostType] = None,
                         tags: Optional[List[str]] = None) -> List[Component]:
        """Search components with filters"""
        try:
            sql = "SELECT * FROM components WHERE 1=1"
            params = []

            if layer_id is not None:
                sql += " AND layer_id = ?"
                params.append(layer_id)

            if category_id is not None:
                sql += " AND category_id = ?"
                params.append(category_id)

            if is_ai_component is not None:
                sql += " AND is_ai_component = ?"
                params.append(is_ai_component)

            if cost_type is not None:
                sql += " AND cost_type = ?"
                params.append(cost_type)

            # Tag filtering with JSON search
            if tags:
                tag_conditions = " AND " + " AND ".join(
                    "JSON_EXTRACT(tags, '$') LIKE ?" for _ in tags
                )
                sql += tag_conditions
                params.extend([f'%"{tag}"%' for tag in tags])

            with self.db.get_connection() as conn:
                rows = conn.execute(sql, params).fetchall()
                return [self._row_to_component(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Component search failed: {e}")
            return []

    def _row_to_component(self, row: sqlite3.Row) -> Component:
        """Convert database row to Component model"""
        data = dict(row)

        # Parse JSON fields
        if data.get('resource_requirements'):
            data['resource_requirements'] = json.loads(data['resource_requirements'])
        if data.get('tags'):
            data['tags'] = json.loads(data['tags'])
        if data.get('metadata'):
            data['metadata'] = json.loads(data['metadata'])

        # Convert cost amounts to Decimal
        data['estimated_monthly_cost_min'] = Decimal(str(data['estimated_monthly_cost_min']))
        data['estimated_monthly_cost_max'] = Decimal(str(data['estimated_monthly_cost_max']))

        return Component(**data)


# ============================================
# Profile Manager
# ============================================

class ProfileManager:
    """Manager for infrastructure profiles with inheritance"""

    def __init__(self, db_manager: DatabaseManager, component_registry: ComponentRegistry):
        self.db = db_manager
        self.registry = component_registry
        self.logger = logging.getLogger(__name__)
        self._profile_cache: Dict[str, Profile] = {}

    def create_profile(self, profile_type: ProfileType, **overrides) -> Profile:
        """Create profile from template with overrides"""
        try:
            # Create profile using factory
            profile = ProfileFactory.create_profile(profile_type, **overrides)

            # Save to database
            profile_id = self._save_profile_to_db(profile)
            profile.id = profile_id

            # Save profile components
            components = profile.metadata.get("components", {})
            self._save_profile_components(profile_id, components)

            # Cache the profile
            self._profile_cache[profile.code] = profile

            self.logger.info(f"Created profile: {profile.code} (ID: {profile_id})")
            return profile

        except Exception as e:
            self.logger.error(f"Profile creation failed: {e}")
            raise

    def get_profile(self, code: str) -> Optional[Profile]:
        """Get profile by code"""
        if code in self._profile_cache:
            return self._profile_cache[code]

        try:
            with self.db.get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM profiles WHERE code = ?", (code,)
                ).fetchone()

                if not row:
                    return None

                profile = self._row_to_profile(row)
                self._profile_cache[code] = profile
                return profile

        except Exception as e:
            self.logger.error(f"Failed to get profile {code}: {e}")
            return None

    def get_profile_summary(self, profile_code: str) -> Optional[ProfileSummary]:
        """Get comprehensive profile summary with statistics"""
        profile = self.get_profile(profile_code)
        if not profile:
            return None

        try:
            with self.db.get_connection() as conn:
                # Get component statistics
                stats_row = conn.execute("""
                    SELECT
                        COUNT(*) as total_components,
                        SUM(CASE WHEN pc.inclusion_type = 'required' THEN 1 ELSE 0 END) as required_components,
                        SUM(CASE WHEN pc.inclusion_type = 'optional' THEN 1 ELSE 0 END) as optional_components,
                        SUM(CASE WHEN c.cost_type = 'free' THEN 1 ELSE 0 END) as free_components,
                        SUM(CASE WHEN c.cost_type != 'free' THEN 1 ELSE 0 END) as paid_components,
                        SUM(c.estimated_monthly_cost_min) as min_monthly_cost,
                        SUM(c.estimated_monthly_cost_max) as max_monthly_cost,
                        SUM(c.setup_time_minutes) / 60.0 as total_setup_hours,
                        AVG(c.setup_complexity) as average_complexity
                    FROM profile_components pc
                    JOIN components c ON pc.component_id = c.id
                    WHERE pc.profile_id = ?
                """, (profile.id,)).fetchone()

                if stats_row:
                    return ProfileSummary(
                        profile=profile,
                        total_components=stats_row['total_components'] or 0,
                        required_components=stats_row['required_components'] or 0,
                        optional_components=stats_row['optional_components'] or 0,
                        free_components=stats_row['free_components'] or 0,
                        paid_components=stats_row['paid_components'] or 0,
                        min_monthly_cost=Decimal(str(stats_row['min_monthly_cost'] or 0)),
                        max_monthly_cost=Decimal(str(stats_row['max_monthly_cost'] or 0)),
                        total_setup_hours=float(stats_row['total_setup_hours'] or 0),
                        average_complexity=float(stats_row['average_complexity'] or 0),
                        total_min_ram_gb=profile.min_ram_gb,
                        total_min_storage_gb=profile.min_storage_gb,
                        requires_gpu=profile.requires_gpu,
                        compliance_coverage=profile.compliance_requirements,
                    )

                return ProfileSummary(profile=profile)

        except Exception as e:
            self.logger.error(f"Failed to get profile summary for {profile_code}: {e}")
            return ProfileSummary(profile=profile)

    def _save_profile_to_db(self, profile: Profile) -> int:
        """Save profile to database"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO profiles (
                    code, name, description, profile_type, parent_profile_id,
                    is_ai_first, default_llm_provider, target_users, target_scale,
                    max_monthly_budget, requires_internet, requires_gpu,
                    min_ram_gb, min_storage_gb, min_cpu_cores,
                    compliance_requirements, metadata, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.code, profile.name, profile.description,
                profile.profile_type, profile.parent_profile_id,
                profile.is_ai_first, profile.default_llm_provider,
                profile.target_users, profile.target_scale,
                float(profile.max_monthly_budget) if profile.max_monthly_budget else None,
                profile.requires_internet, profile.requires_gpu,
                profile.min_ram_gb, profile.min_storage_gb, profile.min_cpu_cores,
                json.dumps(profile.compliance_requirements),
                json.dumps(profile.metadata), profile.is_active
            ))

            profile_id = cursor.lastrowid
            conn.commit()
            return profile_id

    def _save_profile_components(self, profile_id: int, components: Dict[str, Any]) -> None:
        """Save profile component associations"""
        with self.db.get_connection() as conn:
            for comp_code, comp_config in components.items():
                # Get component ID
                component = self.registry.get_component(comp_code)
                if not component:
                    self.logger.warning(f"Component not found: {comp_code}")
                    continue

                inclusion_type = comp_config.get("inclusion", InclusionType.REQUIRED)
                priority = comp_config.get("priority", 1)
                config = comp_config.get("config", {})

                conn.execute("""
                    INSERT OR REPLACE INTO profile_components (
                        profile_id, component_id, inclusion_type, priority, configuration
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    profile_id, component.id, inclusion_type,
                    priority, json.dumps(config)
                ))

            conn.commit()

    def _row_to_profile(self, row: sqlite3.Row) -> Profile:
        """Convert database row to Profile model"""
        data = dict(row)

        # Parse JSON fields
        if data.get('compliance_requirements'):
            data['compliance_requirements'] = json.loads(data['compliance_requirements'])
        if data.get('metadata'):
            data['metadata'] = json.loads(data['metadata'])

        # Convert budget to Decimal
        if data.get('max_monthly_budget'):
            data['max_monthly_budget'] = Decimal(str(data['max_monthly_budget']))

        return Profile(**data)


# ============================================
# Audit Engine
# ============================================

class AuditEngine:
    """Infrastructure audit execution engine"""

    def __init__(self, db_manager: DatabaseManager, profile_manager: ProfileManager):
        self.db = db_manager
        self.profile_manager = profile_manager
        self.logger = logging.getLogger(__name__)

    async def run_audit(self, profile_code: str, environment: TargetScale = TargetScale.DEVELOPMENT,
                       user_email: Optional[str] = None) -> AuditSession:
        """Run complete infrastructure audit"""
        profile = self.profile_manager.get_profile(profile_code)
        if not profile:
            raise ValueError(f"Profile not found: {profile_code}")

        # Create audit session
        session = AuditSession(
            profile_id=profile.id,
            user_email=user_email,
            environment=environment,
            overall_status="running"
        )

        session_id = self._save_session(session)
        session.id = session_id

        try:
            # Get components to audit
            components = self._get_profile_components(profile.id)
            session.total_components = len(components)

            # Run audits in parallel
            results = await self._run_parallel_audits(session, components)

            # Update session with results
            session.passed_components = sum(1 for r in results if r.status == AuditStatus.PASSED)
            session.failed_components = sum(1 for r in results if r.status == AuditStatus.FAILED)
            session.skipped_components = sum(1 for r in results if r.status == AuditStatus.SKIPPED)
            session.end_time = datetime.now()
            session.overall_status = "completed"

            # Generate report
            session.report = self._generate_audit_report(session, results)

            # Update in database
            self._update_session(session)

            self.logger.info(f"Audit completed: {session.session_id} ({session.success_rate:.1f}% success)")
            return session

        except Exception as e:
            session.overall_status = "failed"
            session.end_time = datetime.now()
            session.metadata["error"] = str(e)
            self._update_session(session)
            self.logger.error(f"Audit failed: {e}")
            raise

    async def _run_parallel_audits(self, session: AuditSession,
                                  components: List[Tuple[Component, Dict]]) -> List[AuditResult]:
        """Run component audits in parallel"""
        results = []

        # Use thread pool for blocking operations
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all audit tasks
            future_to_component = {
                executor.submit(self._audit_component, session.id, comp, config): (comp, config)
                for comp, config in components
            }

            # Collect results as they complete
            for future in as_completed(future_to_component):
                comp, config = future_to_component[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.logger.debug(f"Audited {comp.code}: {result.status}")
                except Exception as e:
                    # Create failed result
                    result = AuditResult(
                        session_id=session.id,
                        component_id=comp.id,
                        status=AuditStatus.FAILED,
                        error_message=str(e)
                    )
                    results.append(result)
                    self.logger.error(f"Audit failed for {comp.code}: {e}")

        return results

    def _audit_component(self, session_id: int, component: Component,
                        config: Dict[str, Any]) -> AuditResult:
        """Audit individual component"""
        start_time = datetime.now()

        result = AuditResult(
            session_id=session_id,
            component_id=component.id,
            status=AuditStatus.PENDING
        )

        try:
            # AI components get special handling
            if component.is_ai_component:
                result = self._audit_ai_component(result, component, config)
            else:
                result = self._audit_standard_component(result, component, config)

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds() * 1000
            result.duration_ms = int(duration)

            # Save result to database
            self._save_audit_result(result)

            return result

        except Exception as e:
            result.status = AuditStatus.FAILED
            result.error_message = str(e)
            result.duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self._save_audit_result(result)
            return result

    def _audit_ai_component(self, result: AuditResult, component: Component,
                           config: Dict[str, Any]) -> AuditResult:
        """Audit AI/LLM components"""
        # Check API key availability
        if "api_key" in config:
            result.check_type = "connectivity"
            result.expected_value = "API key configured"
            result.actual_value = "API key present"
            result.status = AuditStatus.PASSED
        else:
            result.status = AuditStatus.FAILED
            result.error_message = "API key not configured"

        return result

    def _audit_standard_component(self, result: AuditResult, component: Component,
                                 config: Dict[str, Any]) -> AuditResult:
        """Audit standard infrastructure components"""
        # Simulate component checks
        result.check_type = "installation"
        result.expected_value = f"{component.code} installed"

        # Mock installation check (in real implementation, this would check actual installation)
        if component.code in ["python_3.13", "vscode", "git"]:
            result.actual_value = f"{component.code} found"
            result.status = AuditStatus.PASSED
        else:
            result.actual_value = f"{component.code} not found"
            result.status = AuditStatus.FAILED
            result.error_message = f"{component.code} is not installed"

        return result

    def _get_profile_components(self, profile_id: int) -> List[Tuple[Component, Dict]]:
        """Get all components for a profile"""
        try:
            with self.db.get_connection() as conn:
                rows = conn.execute("""
                    SELECT c.*, pc.configuration, pc.inclusion_type, pc.priority
                    FROM components c
                    JOIN profile_components pc ON c.id = pc.component_id
                    WHERE pc.profile_id = ? AND pc.inclusion_type != 'excluded'
                    ORDER BY pc.priority
                """, (profile_id,)).fetchall()

                components = []
                for row in rows:
                    # Convert row to component
                    comp_data = dict(row)
                    config = json.loads(comp_data.pop('configuration', '{}'))
                    comp_data.pop('inclusion_type', None)
                    comp_data.pop('priority', None)

                    # Parse JSON fields
                    if comp_data.get('resource_requirements'):
                        comp_data['resource_requirements'] = json.loads(comp_data['resource_requirements'])
                    if comp_data.get('tags'):
                        comp_data['tags'] = json.loads(comp_data['tags'])
                    if comp_data.get('metadata'):
                        comp_data['metadata'] = json.loads(comp_data['metadata'])

                    # Convert decimals
                    comp_data['estimated_monthly_cost_min'] = Decimal(str(comp_data['estimated_monthly_cost_min']))
                    comp_data['estimated_monthly_cost_max'] = Decimal(str(comp_data['estimated_monthly_cost_max']))

                    component = Component(**comp_data)
                    components.append((component, config))

                return components

        except Exception as e:
            self.logger.error(f"Failed to get profile components: {e}")
            return []

    def _generate_audit_report(self, session: AuditSession,
                              results: List[AuditResult]) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        failed_components = [r for r in results if r.status == AuditStatus.FAILED]
        passed_components = [r for r in results if r.status == AuditStatus.PASSED]

        return {
            "summary": {
                "total_components": session.total_components,
                "passed": session.passed_components,
                "failed": session.failed_components,
                "skipped": session.skipped_components,
                "success_rate": session.success_rate,
                "duration_seconds": session.duration_seconds,
            },
            "failed_components": [
                {
                    "component_id": r.component_id,
                    "error": r.error_message,
                    "check_type": r.check_type
                } for r in failed_components
            ],
            "recommendations": self._generate_recommendations(failed_components),
            "next_steps": self._generate_next_steps(session, failed_components),
            "generated_at": datetime.now().isoformat(),
        }

    def _generate_recommendations(self, failed_results: List[AuditResult]) -> List[str]:
        """Generate recommendations based on failed audits"""
        recommendations = []

        if any(r.check_type == "installation" for r in failed_results):
            recommendations.append("Install missing components using the provided setup guide")

        if any("api_key" in (r.error_message or "") for r in failed_results):
            recommendations.append("Configure API keys for AI services")

        recommendations.append("Review the detailed audit results for specific failure reasons")

        return recommendations

    def _generate_next_steps(self, session: AuditSession,
                           failed_results: List[AuditResult]) -> List[str]:
        """Generate next steps based on audit results"""
        steps = []

        if failed_results:
            steps.append("Address failed components before proceeding")
            steps.append("Re-run audit after fixes")
        else:
            steps.append("Infrastructure audit passed - ready for development")
            steps.append("Consider running periodic audits to maintain compliance")

        return steps

    def _save_session(self, session: AuditSession) -> int:
        """Save audit session to database"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO audit_sessions (
                    session_id, profile_id, user_email, environment,
                    total_components, passed_components, failed_components, skipped_components,
                    overall_status, report, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.profile_id, session.user_email,
                session.environment, session.total_components,
                session.passed_components, session.failed_components, session.skipped_components,
                session.overall_status, json.dumps(session.report), json.dumps(session.metadata)
            ))

            session_id = cursor.lastrowid
            conn.commit()
            return session_id

    def _update_session(self, session: AuditSession) -> None:
        """Update audit session in database"""
        with self.db.get_connection() as conn:
            conn.execute("""
                UPDATE audit_sessions SET
                    end_time = ?, passed_components = ?, failed_components = ?,
                    skipped_components = ?, overall_status = ?, report = ?, metadata = ?
                WHERE id = ?
            """, (
                session.end_time, session.passed_components, session.failed_components,
                session.skipped_components, session.overall_status,
                json.dumps(session.report), json.dumps(session.metadata), session.id
            ))
            conn.commit()

    def _save_audit_result(self, result: AuditResult) -> None:
        """Save individual audit result"""
        with self.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO audit_results (
                    session_id, component_id, status, check_type,
                    expected_value, actual_value, error_message,
                    duration_ms, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.session_id, result.component_id, result.status,
                result.check_type, result.expected_value, result.actual_value,
                result.error_message, result.duration_ms, json.dumps(result.metadata)
            ))
            conn.commit()


# ============================================
# Main Audit System
# ============================================

class InfrastructureAuditSystem:
    """Main audit system orchestrating all components"""

    def __init__(self, config: Optional[AuditSystemConfig] = None):
        self.config = config or AuditSystemConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize subsystems
        self.db_manager = DatabaseManager(self.config)
        self.component_registry = ComponentRegistry(self.db_manager)
        self.profile_manager = ProfileManager(self.db_manager, self.component_registry)
        self.audit_engine = AuditEngine(self.db_manager, self.profile_manager)

        # Initialize database if it doesn't exist
        if not self.config.db_path.exists():
            self.db_manager.initialize_database()
            self._load_initial_data()

    def _load_initial_data(self) -> None:
        """Load initial layers, categories, and components"""
        self.logger.info("Loading initial infrastructure data...")

        # This would be expanded with actual component data
        # For now, creating a minimal set for demonstration

        try:
            with self.db_manager.get_connection() as conn:
                # Create base layers
                layers = [
                    (0, "hardware", "Hardware & OS Foundation", 0, None, True),
                    (1, "runtime", "Core Runtime Environments", 1, None, True),
                    (2, "development", "Development Environment", 2, None, False),
                    (3, "database", "Database Infrastructure", 3, None, True),
                    (4, "ai_ml", "AI/ML Infrastructure", 4, None, True),
                    (5, "backend", "Web Framework & API", 5, None, False),
                    (6, "automation", "Automation & Orchestration", 6, None, False),
                ]

                for layer_data in layers:
                    conn.execute("""
                        INSERT OR IGNORE INTO layers (order_index, code, name, order_index, parent_id, is_critical)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, layer_data)

                conn.commit()
                self.logger.info("Initial data loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load initial data: {e}")
            raise

    # Public API methods
    def create_profile(self, profile_type: ProfileType, **overrides) -> Profile:
        """Create a new infrastructure profile"""
        return self.profile_manager.create_profile(profile_type, **overrides)

    def get_profile(self, code: str) -> Optional[Profile]:
        """Get profile by code"""
        return self.profile_manager.get_profile(code)

    def get_profile_summary(self, code: str) -> Optional[ProfileSummary]:
        """Get profile summary with statistics"""
        return self.profile_manager.get_profile_summary(code)

    async def audit_profile(self, profile_code: str, **kwargs) -> AuditSession:
        """Run infrastructure audit for profile"""
        return await self.audit_engine.run_audit(profile_code, **kwargs)

    def register_component(self, component: Component) -> int:
        """Register new infrastructure component"""
        return self.component_registry.register_component(component)

    def search_components(self, **filters) -> List[Component]:
        """Search components with filters"""
        return self.component_registry.search_components(**filters)

    def backup_system(self) -> Path:
        """Create system backup"""
        return self.db_manager.backup_database()

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            with self.db_manager.get_connection() as conn:
                stats = {}

                # Component stats
                stats['components'] = dict(conn.execute(
                    "SELECT cost_type, COUNT(*) FROM components GROUP BY cost_type"
                ).fetchall())

                # Profile stats
                stats['profiles'] = dict(conn.execute(
                    "SELECT profile_type, COUNT(*) FROM profiles GROUP BY profile_type"
                ).fetchall())

                # Audit stats
                audit_stats = conn.execute("""
                    SELECT
                        COUNT(*) as total_audits,
                        AVG(passed_components * 100.0 / total_components) as avg_success_rate
                    FROM audit_sessions
                    WHERE overall_status = 'completed'
                """).fetchone()

                if audit_stats:
                    stats['audits'] = {
                        'total': audit_stats['total_audits'],
                        'avg_success_rate': round(audit_stats['avg_success_rate'] or 0, 1)
                    }

                return stats

        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            return {}


# ============================================
# Export Configuration
# ============================================

__all__ = [
    "AuditSystemConfig",
    "DatabaseManager",
    "ComponentRegistry",
    "ProfileManager",
    "AuditEngine",
    "InfrastructureAuditSystem",
]