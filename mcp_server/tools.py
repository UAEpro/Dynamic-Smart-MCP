"""
MCP Tool Definitions
Defines FastMCP tools for database querying and schema exploration.
"""

import json
from typing import Dict, Any
from fastmcp import FastMCP
from utils.security import ResponseSanitizer, create_user_friendly_response


def register_tools(mcp: FastMCP, db_adapter, query_parser, config: Dict[str, Any]) -> None:
    """
    Register all MCP tools with the server.
    
    Args:
        mcp: FastMCP server instance
        db_adapter: DatabaseAdapter instance
        query_parser: QueryParser instance
        config: Server configuration
    """
    
    # Initialize response sanitizer for security
    sanitizer = ResponseSanitizer(config)
    
    @mcp.tool()
    def query_database(natural_language: str) -> str:
        """
        Execute a read-only SQL query generated from natural language.
        
        This tool converts natural language questions into SQL queries and executes them
        against the connected database. It supports filtering, aggregation, joins, 
        sorting, date operations, and complex analytics.
        
        Safety: Only SELECT queries are allowed. No data modifications possible.
        
        Args:
            natural_language: A question in plain English about your data
            
        Returns:
            JSON string with query results or error message
            
        Examples:
            - "Show me all customers"
            - "What is the total revenue by product category?"
            - "List the top 5 customers by order count"
            - "Show me orders placed in the last 30 days"
        """
        try:
            # Parse natural language to SQL
            parse_result = query_parser.parse(natural_language)
            
            if not parse_result.get("success"):
                # Sanitize error response (hide DB details in production)
                error_response = {
                    "success": False,
                    "error": parse_result.get("error", "Failed to parse query"),
                    "natural_language": natural_language
                }
                sanitized = sanitizer.sanitize_error(error_response, natural_language)
                return json.dumps(sanitized, indent=2)
            
            sql = parse_result["sql"]
            
            # Execute query
            query_result = db_adapter.execute_query(sql)
            
            if not query_result.get("success"):
                # Sanitize error response (hide SQL and DB details)
                error_response = {
                    "success": False,
                    "error": query_result.get("error", "Query execution failed"),
                    "sql": sql,
                    "natural_language": natural_language
                }
                sanitized = sanitizer.sanitize_error(error_response, natural_language)
                return json.dumps(sanitized, indent=2)
            
            # Create user-friendly success response
            if sanitizer.hide_db_details:
                # Production mode: Clean response without technical details
                response = create_user_friendly_response(
                    query_result["rows"],
                    query_result["row_count"],
                    natural_language
                )
            else:
                # Development mode: Full details
                response = {
                    "success": True,
                    "natural_language": natural_language,
                    "sql": sql,
                    "columns": query_result["columns"],
                    "rows": query_result["rows"],
                    "row_count": query_result["row_count"]
                }
            
            # Sanitize (removes SQL if configured)
            sanitized = sanitizer.sanitize_success(response)
            return json.dumps(sanitized, indent=2, default=str)
            
        except Exception as e:
            # Sanitize exception
            error_response = {
                "success": False,
                "error": str(e),
                "natural_language": natural_language
            }
            sanitized = sanitizer.sanitize_error(error_response, natural_language)
            return json.dumps(sanitized, indent=2)
    
    @mcp.tool()
    def get_database_schema() -> str:
        """
        Get database schema information.
        
        Note: In production mode (security.hide_database_details = true),
        this tool will return a generic message instead of actual schema.
        
        Returns:
            JSON string with schema information (or generic message)
        """
        try:
            schema = db_adapter.get_schema()
            
            # Sanitize schema based on security settings
            sanitized = sanitizer.sanitize_schema(schema)
            return json.dumps(sanitized, indent=2, default=str)
        except Exception as e:
            error_response = {"success": False, "error": str(e)}
            sanitized = sanitizer.sanitize_error(error_response, "get_database_schema")
            return json.dumps(sanitized, indent=2)
    
    @mcp.tool()
    def refresh_database_schema() -> str:
        """
        Refresh the cached database schema.
        
        Use this after making schema changes (adding/removing tables or columns)
        to update the tool's understanding of your database structure.
        
        Returns:
            Success message with table count
        """
        try:
            db_adapter.refresh_schema()
            query_parser.update_schema(db_adapter.get_schema())
            
            table_count = len(db_adapter.schema_cache.get("tables", {}))
            
            return json.dumps({
                "success": True,
                "message": f"Schema refreshed successfully. Found {table_count} tables.",
                "table_count": table_count,
                "timestamp": str(db_adapter.last_schema_refresh)
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    @mcp.tool()
    def get_query_examples() -> str:
        """
        Get example natural language queries supported by this tool.
        
        Returns a list of example questions you can ask, organized by category
        (basic queries, filtering, aggregation, joins, complex analytics, etc.)
        
        Returns:
            JSON string with categorized example queries
        """
        examples = {
            "basic": [
                "Show me all customers",
                "List all products",
                "What are all the orders?"
            ],
            "filtering": [
                "Show me customers from USA",
                "List products in the Electronics category",
                "What orders were placed in October 2023?"
            ],
            "aggregation": [
                "What is the total number of customers?",
                "How many products do we have in each category?",
                "What is the average order value?",
                "Show me total sales per customer"
            ],
            "sorting_and_top": [
                "Show me the top 5 most expensive products",
                "List customers by registration date, newest first",
                "What are the top 3 customers by order count?"
            ],
            "joins": [
                "Show me all orders with customer names",
                "List all orders with product details",
                "What products have been ordered?"
            ],
            "complex": [
                "What are the products with the highest sales?",
                "Show me customers who haven't placed any orders",
                "What is the revenue by product category?",
                "List inactive customers"
            ],
            "dates": [
                "What orders were placed last month?",
                "Show me customers registered in 2023",
                "What is the monthly order trend?"
            ]
        }
        
        return json.dumps({
            "success": True,
            "examples": examples,
            "note": "Adapt these examples to match your actual database schema"
        }, indent=2)

