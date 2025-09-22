"""
MCP (Model Context Protocol) Client
For integration with AI-driven PostgreSQL management
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with MCP server"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=30.0,
            headers={"X-API-Key": api_key} if api_key else {}
        )

    async def check_health(self) -> bool:
        """Check MCP server health"""
        try:
            response = await self.client.get("/health")
            data = response.json()
            return data.get("status") == "healthy"
        except Exception as e:
            logger.error(f"MCP health check failed: {e}")
            return False

    async def log_agent_action(
        self,
        action_type: str,
        target: str,
        confidence: float,
        reasoning: str,
        llm_model: str = "gemini-2.5-flash"
    ) -> Optional[str]:
        """Log an AI agent action to MCP server"""
        try:
            action_data = {
                "agent_id": "550e8400-e29b-41d4-a716-446655440000",  # Default agent
                "action_type": action_type,
                "target_database": "ai_control",
                "target_object": target,
                "decision_confidence": confidence,
                "decision_reasoning": reasoning,
                "llm_model": llm_model,
                "timestamp": datetime.utcnow().isoformat()
            }

            response = await self.client.post("/agent/action", json=action_data)
            if response.status_code == 200:
                result = response.json()
                return result.get("action_id")
        except Exception as e:
            logger.error(f"Failed to log agent action: {e}")
        return None

    async def collect_metric(
        self,
        metric_name: str,
        value: float,
        database: str = "ai_control"
    ) -> bool:
        """Collect performance metric"""
        try:
            metric_data = {
                "metric_name": metric_name,
                "database_name": database,
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            }

            response = await self.client.post("/metrics/collect", json=metric_data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to collect metric: {e}")
            return False

    async def get_database_stats(self) -> Optional[Dict[str, Any]]:
        """Get database statistics from MCP"""
        try:
            response = await self.client.get("/stats/database")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
        return None

    async def optimize_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Request query optimization from MCP"""
        try:
            response = await self.client.post(
                "/optimize/query",
                json={"query": query, "database": "ai_control"}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to optimize query: {e}")
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()