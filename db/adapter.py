"""
Universal Database Adapter
Connects to any SQL database via SQLAlchemy and provides schema introspection.
"""

from sqlalchemy import (
    create_engine, MetaData, inspect, text, 
    Table, Column, Integer, String, Float, DateTime, Boolean
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DatabaseAdapter:
    """Universal SQL database adapter with auto-schema detection."""
    
    def __init__(self, connection_string: str, max_rows: int = 1000):
        """
        Initialize database connection.
        
        Args:
            connection_string: SQLAlchemy connection URL
            max_rows: Maximum rows to return per query (safety limit)
        """
        self.connection_string = connection_string
        self.max_rows = max_rows
        self.engine: Optional[Engine] = None
        self.metadata: Optional[MetaData] = None
        self.schema_cache: Dict[str, Any] = {}
        self.last_schema_refresh: Optional[datetime] = None
        
    def connect(self) -> None:
        """Establish database connection and load schema."""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,  # Verify connections before use
                echo=False  # Set True for SQL debugging
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Connected to database: {self.engine.dialect.name}")
            
            # Load schema
            self.refresh_schema()
            
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def refresh_schema(self) -> None:
        """Scan and cache complete database schema."""
        if not self.engine:
            raise RuntimeError("Database not connected")
        
        logger.info("Refreshing database schema...")
        
        # Reflect all tables
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        
        # Build schema cache
        inspector = inspect(self.engine)
        self.schema_cache = {
            "tables": {},
            "relationships": [],
            "database_type": self.engine.dialect.name
        }
        
        # Extract table details
        for table_name in inspector.get_table_names():
            columns = []
            
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "primary_key": col.get("primary_key", False),
                    "default": str(col.get("default", ""))
                })
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Get sample data (first 3 rows)
            sample_data = self._get_sample_data(table_name, limit=3)
            
            self.schema_cache["tables"][table_name] = {
                "columns": columns,
                "foreign_keys": foreign_keys,
                "sample_data": sample_data,
                "row_count": self._get_row_count(table_name)
            }
        
        self.last_schema_refresh = datetime.now()
        logger.info(f"Schema loaded: {len(self.schema_cache['tables'])} tables")
    
    def _get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample rows from a table."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT * FROM {table_name} LIMIT {limit}")
                )
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.warning(f"Could not fetch sample data from {table_name}: {e}")
            return []
    
    def _get_row_count(self, table_name: str) -> int:
        """Get approximate row count for a table."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar() or 0
        except Exception:
            return 0
    
    def execute_query(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.
        
        Args:
            sql: SQL query string
            
        Returns:
            Dict with 'columns', 'rows', 'row_count', and 'query' keys
        """
        if not self.engine:
            raise RuntimeError("Database not connected")
        
        try:
            with self.engine.connect() as conn:
                # Add LIMIT if not present (safety)
                sql_upper = sql.upper().strip()
                if "LIMIT" not in sql_upper:
                    sql = f"{sql.rstrip(';')} LIMIT {self.max_rows}"
                
                result = conn.execute(text(sql))
                
                # Fetch results
                rows = result.fetchall()
                columns = list(result.keys()) if rows else []
                
                # Convert to list of dicts
                data = [dict(zip(columns, row)) for row in rows]
                
                return {
                    "columns": columns,
                    "rows": data,
                    "row_count": len(data),
                    "query": sql,
                    "success": True
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": sql
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """Return cached schema information."""
        return self.schema_cache
    
    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

