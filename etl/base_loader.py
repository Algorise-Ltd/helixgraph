"""
BaseLoader - Generic ETL Framework for Neo4j Data Loading

Provides common functionality for all domain-specific loaders:
- Connection management
- Schema setup
- Batch loading optimization
- Error handling and logging
- Data validation
- Statistics and reporting
"""
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
from pydantic import BaseModel, ValidationError


class LoadStats:
    """Track loading statistics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.end_time = None
        self.nodes_created = {}  # {label: count}
        self.relationships_created = {}  # {type: count}
        self.records_processed = 0
        self.records_failed = 0
        self.errors = []
        
    def add_nodes(self, label: str, count: int):
        """Add node count for a specific label"""
        self.nodes_created[label] = self.nodes_created.get(label, 0) + count
        
    def add_relationships(self, rel_type: str, count: int):
        """Add relationship count for a specific type"""
        self.relationships_created[rel_type] = self.relationships_created.get(rel_type, 0) + count
        
    def add_error(self, error: str):
        """Record an error"""
        self.errors.append(error)
        self.records_failed += 1
        
    def finalize(self):
        """Mark loading as complete"""
        self.end_time = time.time()
        
    @property
    def duration(self) -> float:
        """Get loading duration in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def total_nodes(self) -> int:
        """Get total nodes created"""
        return sum(self.nodes_created.values())
    
    @property
    def total_relationships(self) -> int:
        """Get total relationships created"""
        return sum(self.relationships_created.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        return {
            'duration': self.duration,
            'nodes_created': self.nodes_created,
            'total_nodes': self.total_nodes,
            'relationships_created': self.relationships_created,
            'total_relationships': self.total_relationships,
            'records_processed': self.records_processed,
            'records_failed': self.records_failed,
            'error_count': len(self.errors)
        }


class BaseLoader:
    """
    Base class for all domain-specific loaders.
    
    Provides common ETL functionality:
    - Connection management
    - Schema setup
    - Batch loading
    - Error handling
    - Logging
    - Statistics tracking
    """
    
    def __init__(
        self, 
        uri: str, 
        user: str, 
        password: str,
        database: str = "neo4j",
        batch_size: int = 100,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the loader.
        
        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
            database: Neo4j database name (default: "neo4j")
            batch_size: Default batch size for bulk operations
            logger: Optional logger instance
        """
        self.uri = uri
        self.user = user
        self.database = database
        self.batch_size = batch_size
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.stats = LoadStats()
        
        # Setup logger
        self.logger = logger or self._setup_logger()
        
        self.logger.info(f"Initialized {self.__class__.__name__}")
        self.logger.info(f"Connected to Neo4j at {uri}")
        
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()
            self.logger.info("Neo4j connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        
    def test_connection(self) -> bool:
        """Test Neo4j connection"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as test")
                result.single()
            self.logger.info("✓ Connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"✗ Connection test failed: {e}")
            return False
    
    def clear_database(self):
        """
        Clear all nodes and relationships in the database.
        WARNING: This is destructive!
        """
        self.logger.warning("Clearing database...")
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
        self.logger.info("✓ Database cleared")
    
    def execute_cypher(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            Query result
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return result
        except Neo4jError as e:
            self.logger.error(f"Cypher execution error: {e}")
            self.stats.add_error(str(e))
            raise
    
    def create_constraint(self, constraint_query: str):
        """Create a constraint"""
        try:
            self.execute_cypher(constraint_query)
            self.logger.debug(f"Created constraint: {constraint_query[:50]}...")
        except Neo4jError as e:
            # Constraint might already exist, log but don't fail
            self.logger.debug(f"Constraint creation: {e}")
    
    def create_index(self, index_query: str):
        """Create an index"""
        try:
            self.execute_cypher(index_query)
            self.logger.debug(f"Created index: {index_query[:50]}...")
        except Neo4jError as e:
            # Index might already exist, log but don't fail
            self.logger.debug(f"Index creation: {e}")
    
    def setup_schema(self):
        """
        Setup database schema (constraints and indexes).
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement setup_schema()")
    
    def validate_data(self, data: List[Dict], model: BaseModel) -> tuple[List[Dict], List[str]]:
        """
        Validate data using a Pydantic model.
        
        Args:
            data: List of data dictionaries
            model: Pydantic model class for validation
            
        Returns:
            Tuple of (valid_records, error_messages)
        """
        valid_records = []
        errors = []
        
        for i, record in enumerate(data):
            try:
                validated = model(**record)
                valid_records.append(validated.model_dump())
            except ValidationError as e:
                error_msg = f"Record {i}: {e}"
                errors.append(error_msg)
                self.logger.warning(error_msg)
                self.stats.add_error(error_msg)
        
        self.logger.info(f"Validated {len(valid_records)}/{len(data)} records")
        return valid_records, errors
    
    def batch_load(
        self,
        data: List[Dict],
        cypher_query: str,
        batch_size: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> int:
        """
        Load data in batches using UNWIND.
        
        Args:
            data: List of data dictionaries
            cypher_query: Cypher query with $batch parameter
            batch_size: Batch size (uses default if not specified)
            progress_callback: Optional callback function(current, total)
            
        Returns:
            Number of records processed
        """
        batch_size = batch_size or self.batch_size
        total = len(data)
        processed = 0
        
        self.logger.info(f"Loading {total} records in batches of {batch_size}")
        
        with self.driver.session(database=self.database) as session:
            for i in range(0, total, batch_size):
                batch = data[i:i + batch_size]
                
                try:
                    session.run(cypher_query, batch=batch)
                    processed += len(batch)
                    self.stats.records_processed += len(batch)
                    
                    if progress_callback:
                        progress_callback(processed, total)
                    else:
                        self.logger.debug(f"  Processed {processed}/{total} records")
                        
                except Neo4jError as e:
                    error_msg = f"Batch {i//batch_size + 1} failed: {e}"
                    self.logger.error(error_msg)
                    self.stats.add_error(error_msg)
                    # Continue with next batch
        
        self.logger.info(f"✓ Loaded {processed} records")
        return processed
    
    def get_node_count(self, label: str) -> int:
        """Get count of nodes with a specific label"""
        with self.driver.session(database=self.database) as session:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            return result.single()['count']
    
    def get_relationship_count(self, rel_type: str) -> int:
        """Get count of relationships with a specific type"""
        with self.driver.session(database=self.database) as session:
            result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
            return result.single()['count']
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics.
        
        Returns:
            Dictionary with node counts, relationship counts, etc.
        """
        stats = {}
        
        with self.driver.session(database=self.database) as session:
            # Total nodes
            result = session.run("MATCH (n) RETURN count(n) as count")
            stats['total_nodes'] = result.single()['count']
            
            # Total relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats['total_relationships'] = result.single()['count']
            
            # Node counts by label
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)
            stats['nodes_by_label'] = {record['label']: record['count'] for record in result}
            
            # Relationship counts by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC
            """)
            stats['relationships_by_type'] = {record['type']: record['count'] for record in result}
        
        return stats
    
    def load(self):
        """
        Main loading method.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement load()")
    
    def print_statistics(self):
        """Print loading statistics"""
        self.stats.finalize()
        
        print("\n" + "=" * 70)
        print(f"{self.__class__.__name__} - Loading Statistics")
        print("=" * 70)
        
        print(f"\n⏱️  Duration: {self.stats.duration:.2f} seconds")
        
        print(f"\n📊 Nodes Created:")
        for label, count in self.stats.nodes_created.items():
            print(f"  {label:20} {count:>6,}")
        print(f"  {'─' * 30}")
        print(f"  {'Total':20} {self.stats.total_nodes:>6,}")
        
        print(f"\n🔗 Relationships Created:")
        for rel_type, count in self.stats.relationships_created.items():
            print(f"  {rel_type:20} {count:>6,}")
        print(f"  {'─' * 30}")
        print(f"  {'Total':20} {self.stats.total_relationships:>6,}")
        
        print(f"\n📈 Records:")
        print(f"  Processed:  {self.stats.records_processed:>6,}")
        print(f"  Failed:     {self.stats.records_failed:>6,}")
        
        if self.stats.errors:
            print(f"\n⚠️  Errors: {len(self.stats.errors)}")
            for i, error in enumerate(self.stats.errors[:5], 1):
                print(f"  {i}. {error[:100]}...")
            if len(self.stats.errors) > 5:
                print(f"  ... and {len(self.stats.errors) - 5} more errors")
        else:
            print(f"\n✅ No errors")
        
        print("\n" + "=" * 70)
