"""FalkorDB-based knowledge graph for relationship storage"""
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import redis
    from falkordb import FalkorDB
    FALKORDB_AVAILABLE = True
except ImportError:
    FALKORDB_AVAILABLE = False

from loguru import logger


@dataclass
class GraphNode:
    """Graph node representation"""
    id: str
    label: str
    properties: Dict[str, Any]


@dataclass
class GraphRelationship:
    """Graph relationship representation"""
    from_node: str
    to_node: str
    relationship_type: str
    properties: Dict[str, Any]


class KnowledgeGraph:
    """Manages knowledge graph using FalkorDB"""
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6379,
        graph_name: str = "browser_knowledge"
    ):
        if not FALKORDB_AVAILABLE:
            logger.warning("FalkorDB client not available. Install with: pip install falkordb")
            self.db = None
            self.graph = None
            return
        
        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.db = None
        self.graph = None
    
    async def initialize(self) -> bool:
        """Initialize connection to FalkorDB"""
        if not FALKORDB_AVAILABLE:
            logger.error("Cannot initialize KnowledgeGraph: FalkorDB client not available")
            return False
        
        try:
            self.db = FalkorDB(host=self.host, port=self.port)
            self.graph = self.db.select_graph(self.graph_name)
            
            # Test connection
            await self._run_sync(self._test_connection)
            
            # Create indexes for better performance
            await self._create_indexes()
            
            logger.info(f"Knowledge graph initialized: {self.graph_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge graph: {e}")
            self.db = None
            self.graph = None
            return False
    
    async def _run_sync(self, func, *args, **kwargs):
        """Run synchronous function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    
    def _test_connection(self):
        """Test database connection"""
        result = self.graph.query("RETURN 1 as test")
        return result.result_set[0][0] == 1
    
    async def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Create index on Page nodes
            await self._run_sync(
                self.graph.query,
                "CREATE INDEX ON :Page(url)"
            )
            
            # Create index on Element nodes
            await self._run_sync(
                self.graph.query,
                "CREATE INDEX ON :Element(selector)"
            )
            
            # Create index on Action nodes
            await self._run_sync(
                self.graph.query,
                "CREATE INDEX ON :Action(type)"
            )
            
            logger.debug("Created graph indexes")
            
        except Exception as e:
            # Indexes might already exist, which is fine
            logger.debug(f"Index creation note: {e}")
    
    async def create_page_node(self, url: str, title: str, metadata: Optional[Dict] = None) -> bool:
        """Create or update page node"""
        if not self.graph:
            logger.warning("Knowledge graph not available")
            return False
        
        try:
            properties = {
                "url": url,
                "title": title,
                "last_visited": datetime.now().isoformat(),
                "visit_count": 1,
                **(metadata or {})
            }
            
            # Use MERGE to create or update
            query = """
            MERGE (p:Page {url: $url})
            ON CREATE SET p += $props, p.created_at = timestamp()
            ON MATCH SET p.title = $title, p.last_visited = $timestamp, p.visit_count = p.visit_count + 1
            RETURN p
            """
            
            params = {
                "url": url,
                "title": title,
                "timestamp": datetime.now().isoformat(),
                "props": properties
            }
            
            await self._run_sync(self.graph.query, query, params)
            logger.debug(f"Created/updated page node: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create page node: {e}")
            return False
    
    async def create_element_node(self, selector: str, element_type: str, page_url: str, metadata: Optional[Dict] = None) -> bool:
        """Create element node and link to page"""
        if not self.graph:
            return False
        
        try:
            properties = {
                "selector": selector,
                "type": element_type,
                "interaction_count": 0,
                "success_count": 0,
                "created_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            query = """
            MATCH (p:Page {url: $page_url})
            MERGE (e:Element {selector: $selector, page_url: $page_url})
            ON CREATE SET e += $props
            MERGE (p)-[:CONTAINS]->(e)
            RETURN e
            """
            
            params = {
                "selector": selector,
                "page_url": page_url,
                "props": properties
            }
            
            await self._run_sync(self.graph.query, query, params)
            logger.debug(f"Created element node: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create element node: {e}")
            return False
    
    async def record_action(self, action_type: str, element_selector: str, page_url: str, success: bool, metadata: Optional[Dict] = None) -> bool:
        """Record an action and its outcome"""
        if not self.graph:
            return False
        
        try:
            properties = {
                "type": action_type,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            query = """
            MATCH (p:Page {url: $page_url})
            MATCH (e:Element {selector: $selector, page_url: $page_url})
            CREATE (a:Action $props)
            CREATE (a)-[:PERFORMED_ON]->(e)
            CREATE (p)-[:ACTION_OCCURRED]->(a)
            SET e.interaction_count = e.interaction_count + 1
            SET e.success_count = e.success_count + CASE WHEN $success THEN 1 ELSE 0 END
            RETURN a
            """
            
            params = {
                "page_url": page_url,
                "selector": element_selector,
                "success": success,
                "props": properties
            }
            
            await self._run_sync(self.graph.query, query, params)
            logger.debug(f"Recorded action: {action_type} on {element_selector}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record action: {e}")
            return False
    
    async def create_navigation_path(self, from_url: str, to_url: str, action_type: str = "navigate") -> bool:
        """Create navigation relationship between pages"""
        if not self.graph:
            return False
        
        try:
            query = """
            MATCH (from:Page {url: $from_url})
            MATCH (to:Page {url: $to_url})
            MERGE (from)-[nav:NAVIGATED_TO {type: $action_type}]->(to)
            ON CREATE SET nav.count = 1, nav.created_at = timestamp()
            ON MATCH SET nav.count = nav.count + 1, nav.last_used = timestamp()
            RETURN nav
            """
            
            params = {
                "from_url": from_url,
                "to_url": to_url,
                "action_type": action_type
            }
            
            await self._run_sync(self.graph.query, query, params)
            logger.debug(f"Created navigation path: {from_url} -> {to_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create navigation path: {e}")
            return False
    
    async def get_successful_elements(self, page_url: str, action_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get elements with high success rates for actions"""
        if not self.graph:
            return []
        
        try:
            if action_type:
                query = """
                MATCH (p:Page {url: $page_url})-[:CONTAINS]->(e:Element)<-[:PERFORMED_ON]-(a:Action {type: $action_type, success: true})
                WITH e, COUNT(a) as success_count
                WHERE e.interaction_count > 0
                RETURN e.selector, e.type, success_count, 
                       (success_count * 100.0 / e.interaction_count) as success_rate
                ORDER BY success_rate DESC, success_count DESC
                LIMIT 10
                """
                params = {"page_url": page_url, "action_type": action_type}
            else:
                query = """
                MATCH (p:Page {url: $page_url})-[:CONTAINS]->(e:Element)
                WHERE e.interaction_count > 0 AND e.success_count > 0
                RETURN e.selector, e.type, e.success_count, 
                       (e.success_count * 100.0 / e.interaction_count) as success_rate
                ORDER BY success_rate DESC, e.success_count DESC
                LIMIT 10
                """
                params = {"page_url": page_url}
            
            result = await self._run_sync(self.graph.query, query, params)
            
            elements = []
            for row in result.result_set:
                elements.append({
                    "selector": row[0],
                    "type": row[1],
                    "success_count": row[2],
                    "success_rate": row[3]
                })
            
            logger.debug(f"Found {len(elements)} successful elements for {page_url}")
            return elements
            
        except Exception as e:
            logger.error(f"Failed to get successful elements: {e}")
            return []
    
    async def get_navigation_patterns(self, from_url: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get common navigation patterns"""
        if not self.graph:
            return []
        
        try:
            if from_url:
                query = """
                MATCH (from:Page {url: $from_url})-[nav:NAVIGATED_TO]->(to:Page)
                RETURN from.url, to.url, nav.type, nav.count, to.title
                ORDER BY nav.count DESC
                LIMIT $limit
                """
                params = {"from_url": from_url, "limit": limit}
            else:
                query = """
                MATCH (from:Page)-[nav:NAVIGATED_TO]->(to:Page)
                RETURN from.url, to.url, nav.type, nav.count, to.title
                ORDER BY nav.count DESC
                LIMIT $limit
                """
                params = {"limit": limit}
            
            result = await self._run_sync(self.graph.query, query, params)
            
            patterns = []
            for row in result.result_set:
                patterns.append({
                    "from_url": row[0],
                    "to_url": row[1],
                    "navigation_type": row[2],
                    "count": row[3],
                    "to_title": row[4]
                })
            
            logger.debug(f"Found {len(patterns)} navigation patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get navigation patterns: {e}")
            return []
    
    async def find_shortest_path(self, from_url: str, to_url: str) -> Optional[List[str]]:
        """Find shortest navigation path between pages"""
        if not self.graph:
            return None
        
        try:
            query = """
            MATCH (from:Page {url: $from_url}), (to:Page {url: $to_url}),
                  path = shortestPath((from)-[:NAVIGATED_TO*]->(to))
            RETURN [node in nodes(path) | node.url] as path
            """
            
            params = {"from_url": from_url, "to_url": to_url}
            result = await self._run_sync(self.graph.query, query, params)
            
            if result.result_set:
                path = result.result_set[0][0]
                logger.debug(f"Found path: {' -> '.join(path)}")
                return path
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find shortest path: {e}")
            return None
    
    async def get_page_statistics(self, url: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific page"""
        if not self.graph:
            return None
        
        try:
            query = """
            MATCH (p:Page {url: $url})
            OPTIONAL MATCH (p)-[:CONTAINS]->(e:Element)
            OPTIONAL MATCH (p)-[:ACTION_OCCURRED]->(a:Action)
            RETURN p.title, p.visit_count, p.last_visited,
                   COUNT(DISTINCT e) as element_count,
                   COUNT(DISTINCT a) as action_count,
                   COUNT(DISTINCT CASE WHEN a.success THEN a END) as successful_actions
            """
            
            params = {"url": url}
            result = await self._run_sync(self.graph.query, query, params)
            
            if result.result_set:
                row = result.result_set[0]
                return {
                    "title": row[0],
                    "visit_count": row[1],
                    "last_visited": row[2],
                    "element_count": row[3],
                    "action_count": row[4],
                    "successful_actions": row[5],
                    "success_rate": (row[5] / max(row[4], 1)) * 100 if row[4] > 0 else 0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get page statistics: {e}")
            return None
    
    async def cleanup_old_data(self, days: int = 90):
        """Clean up old graph data"""
        if not self.graph:
            return
        
        try:
            # Remove old actions
            query = """
            MATCH (a:Action)
            WHERE datetime(a.timestamp) < datetime() - duration({days: $days})
            DETACH DELETE a
            """
            
            result = await self._run_sync(self.graph.query, query, {"days": days})
            logger.info(f"Cleaned up old graph data older than {days} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get overall graph statistics"""
        if not self.graph:
            return {}
        
        try:
            query = """
            MATCH (n)
            WITH labels(n) as node_labels
            UNWIND node_labels as label
            RETURN label, COUNT(*) as count
            """
            
            result = await self._run_sync(self.graph.query, query)
            
            stats = {"nodes": {}}
            for row in result.result_set:
                stats["nodes"][row[0]] = row[1]
            
            # Get relationship counts
            rel_query = "MATCH ()-[r]->() RETURN type(r) as rel_type, COUNT(r) as count"
            rel_result = await self._run_sync(self.graph.query, rel_query)
            
            stats["relationships"] = {}
            for row in rel_result.result_set:
                stats["relationships"][row[0]] = row[1]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            return {}
    
    def is_available(self) -> bool:
        """Check if knowledge graph is available"""
        return self.graph is not None
    
    async def close(self):
        """Close connection"""
        if self.db:
            # FalkorDB client doesn't need explicit closing
            self.db = None
            self.graph = None
            logger.debug("Knowledge graph connection closed")