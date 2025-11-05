"""
Schema Introspection Utilities
Formats and presents database schema for LLM consumption.
"""

from typing import Dict, List, Any
import json


def format_schema_for_llm(schema: Dict[str, Any]) -> str:
    """
    Format database schema into a clear, LLM-readable string.
    
    Args:
        schema: Schema dictionary from DatabaseAdapter
        
    Returns:
        Formatted schema description
    """
    if not schema or "tables" not in schema:
        return "No schema available"
    
    output = []
    output.append(f"DATABASE TYPE: {schema.get('database_type', 'Unknown')}\n")
    output.append(f"TOTAL TABLES: {len(schema['tables'])}\n")
    output.append("=" * 80)
    
    for table_name, table_info in schema["tables"].items():
        output.append(f"\nTABLE: {table_name}")
        output.append(f"Rows: ~{table_info.get('row_count', 0)}")
        output.append("-" * 40)
        
        # Columns
        output.append("COLUMNS:")
        for col in table_info["columns"]:
            pk = " [PRIMARY KEY]" if col.get("primary_key") else ""
            nullable = "" if col.get("nullable") else " [NOT NULL]"
            output.append(f"  - {col['name']}: {col['type']}{pk}{nullable}")
        
        # Foreign Keys
        if table_info.get("foreign_keys"):
            output.append("\nFOREIGN KEYS:")
            for fk in table_info["foreign_keys"]:
                cols = ", ".join(fk.get("constrained_columns", []))
                ref_table = fk.get("referred_table", "")
                ref_cols = ", ".join(fk.get("referred_columns", []))
                output.append(f"  - {cols} -> {ref_table}({ref_cols})")
        
        # Sample Data
        if table_info.get("sample_data"):
            output.append("\nSAMPLE DATA:")
            for i, row in enumerate(table_info["sample_data"][:2], 1):
                # Show first 2 sample rows
                row_str = ", ".join([f"{k}={v}" for k, v in list(row.items())[:5]])
                if len(row) > 5:
                    row_str += ", ..."
                output.append(f"  Row {i}: {row_str}")
        
        output.append("")
    
    return "\n".join(output)


def get_example_queries() -> List[Dict[str, str]]:
    """
    Return example NL -> SQL query patterns.
    These help the LLM understand expected query types.
    """
    return [
        {
            "natural_language": "Show me all customers",
            "sql_pattern": "SELECT * FROM customers LIMIT 100"
        },
        {
            "natural_language": "List products in Electronics category",
            "sql_pattern": "SELECT * FROM products WHERE category = 'Electronics'"
        },
        {
            "natural_language": "What is the total number of orders?",
            "sql_pattern": "SELECT COUNT(*) as total_orders FROM orders"
        },
        {
            "natural_language": "Show me top 5 most expensive products",
            "sql_pattern": "SELECT * FROM products ORDER BY price DESC LIMIT 5"
        },
        {
            "natural_language": "What is the average order value?",
            "sql_pattern": "SELECT AVG(total_amount) as avg_order_value FROM orders"
        },
        {
            "natural_language": "Show me orders with customer names",
            "sql_pattern": "SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id"
        },
        {
            "natural_language": "What are total sales by category?",
            "sql_pattern": "SELECT category, SUM(price * quantity) as total_sales FROM products GROUP BY category"
        },
        {
            "natural_language": "Show me customers who placed orders in last 30 days",
            "sql_pattern": "SELECT DISTINCT c.* FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.order_date >= DATE('now', '-30 days')"
        },
        {
            "natural_language": "List employees by department with salaries",
            "sql_pattern": "SELECT department, name, salary FROM employees ORDER BY department, salary DESC"
        },
        {
            "natural_language": "What products have never been ordered?",
            "sql_pattern": "SELECT p.* FROM products p LEFT JOIN order_items oi ON p.id = oi.product_id WHERE oi.id IS NULL"
        }
    ]


def format_examples_for_llm() -> str:
    """Format example queries as a prompt section."""
    examples = get_example_queries()
    output = ["EXAMPLE QUERY PATTERNS:", "=" * 80]
    
    for i, ex in enumerate(examples, 1):
        output.append(f"\n{i}. Natural Language: \"{ex['natural_language']}\"")
        output.append(f"   SQL: {ex['sql_pattern']}")
    
    return "\n".join(output)


def get_safety_rules() -> str:
    """Return SQL safety rules for LLM prompt."""
    return """
SQL SAFETY RULES:
=================
1. ONLY generate SELECT queries (read-only)
2. NEVER use DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE
3. Always include LIMIT clause (max 1000 rows)
4. Use table aliases for clarity in JOINs
5. Handle NULL values appropriately
6. Use proper date functions for the database type
7. Validate column and table names exist in schema
8. Return ONLY the SQL query, no explanations or markdown
9. If query is unsafe or impossible, return: ERROR: [reason]
"""


def schema_to_json(schema: Dict[str, Any]) -> str:
    """Convert schema to pretty JSON format."""
    return json.dumps(schema, indent=2, default=str)

