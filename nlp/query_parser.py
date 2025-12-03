"""
Natural Language to SQL Query Parser
Uses LLM to convert natural language questions into safe SQL queries.
"""

from typing import Dict, Any, Optional
import logging
import re
from openai import OpenAI
from utils.schema import format_schema_for_llm, format_examples_for_llm, get_safety_rules

logger = logging.getLogger(__name__)


class QueryParser:
    """Converts natural language to SQL using LLM with schema context."""
    
    def __init__(self, llm_config: Dict[str, Any], schema: Dict[str, Any]):
        """
        Initialize query parser with LLM configuration.
        
        Args:
            llm_config: LLM settings from config.yaml
            schema: Database schema from DatabaseAdapter
        """
        self.llm_config = llm_config
        self.schema = schema
        
        # Initialize OpenAI client (works with compatible APIs)
        api_key = llm_config.get("api_key_env", "")
        api_base = llm_config.get("api_base")
        
        client_kwargs = {"api_key": api_key}
        if api_base:
            client_kwargs["base_url"] = api_base
        
        self.client = OpenAI(**client_kwargs)
        self.model = llm_config.get("model", "gpt-3.5-turbo")
        self.temperature = llm_config.get("temperature", 0.0)
        self.max_tokens = llm_config.get("max_tokens", 500)
        
        logger.info(f"Query parser initialized with model: {self.model}")
    
    def parse(self, natural_language: str) -> Dict[str, Any]:
        """
        Convert natural language to SQL query.
        
        Args:
            natural_language: User's question in plain English
            
        Returns:
            Dict with 'sql', 'success', and optional 'error' keys
        """
        try:
            # Build prompt with schema context
            prompt = self._build_prompt(natural_language)
            
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL query generator. Return ONLY valid SQL queries, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract SQL from response
            sql = response.choices[0].message.content.strip()
            sql = self._clean_sql(sql)
            
            # Validate safety
            if not self._is_safe_query(sql):
                return {
                    "success": False,
                    "error": "Generated query failed safety validation",
                    "sql": sql
                }
            
            return {
                "success": True,
                "sql": sql,
                "natural_language": natural_language
            }
            
        except Exception as e:
            logger.error(f"Query parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "natural_language": natural_language
            }
    
    def _build_prompt(self, natural_language: str) -> str:
        """Build comprehensive prompt with schema, context, and examples."""
        schema_text = format_schema_for_llm(self.schema)
        examples_text = format_examples_for_llm()
        safety_rules = get_safety_rules()
        
        # Add database context if available (improves query quality!)
        context_text = self._build_database_context()
        
        prompt = f"""Convert the following natural language question into a SQL query.

{safety_rules}

{context_text}

{schema_text}

{examples_text}

NATURAL LANGUAGE QUESTION:
"{natural_language}"

IMPORTANT: Return ONLY the SQL query, nothing else. No markdown, no explanations.
"""
        return prompt
    
    def _build_database_context(self) -> str:
        """Build database context section from config (if available)."""
        db_context = self.llm_config.get("database_context", {})
        
        if not db_context:
            return ""
        
        context_parts = ["DATABASE CONTEXT:", "=" * 80]
        
        # Description
        if "description" in db_context:
            context_parts.append(f"Description: {db_context['description']}")
        
        # Domain
        if "domain" in db_context:
            context_parts.append(f"Domain: {db_context['domain']}")
        
        # Business concepts
        if "business_concepts" in db_context:
            context_parts.append("\nKey Concepts:")
            for concept in db_context["business_concepts"]:
                context_parts.append(f"  • {concept}")
        
        # Table documentation
        if "tables" in db_context:
            context_parts.append("\nTable Descriptions:")
            for table_name, table_info in db_context["tables"].items():
                desc = table_info.get("description", "")
                notes = table_info.get("notes", "")
                context_parts.append(f"  • {table_name}: {desc}")
                if notes:
                    context_parts.append(f"    ({notes})")
        
        # Data conventions
        if "conventions" in db_context:
            context_parts.append("\nData Conventions:")
            for key, value in db_context["conventions"].items():
                context_parts.append(f"  • {key}: {value}")
        
        # Common queries
        if "common_queries" in db_context:
            context_parts.append("\nCommon Use Cases:")
            for query in db_context["common_queries"][:5]:  # Show first 5
                context_parts.append(f"  • {query}")
        
        context_parts.append("=" * 80)
        context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and normalize SQL query."""
        # Remove markdown code blocks
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```\s*', '', sql)
        
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        
        # Remove trailing semicolon if present
        sql = sql.rstrip(';')
        
        return sql.strip()
    
    def _is_safe_query(self, sql: str) -> bool:
        """
        Validate query safety (read-only checks).
        
        Args:
            sql: SQL query string
            
        Returns:
            True if query is safe, False otherwise
        """
        sql_upper = sql.upper()
        
        # Check for dangerous commands
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER',
            'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE', 'EXEC',
            'EXECUTE', 'SCRIPT', '--', '/*', '*/', 'UNION'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                logger.warning(f"Unsafe keyword detected: {keyword}")
                return False
        
        # Must start with SELECT
        if not sql_upper.strip().startswith('SELECT'):
            logger.warning("Query does not start with SELECT")
            return False
        
        # Check for multiple statements (SQL injection attempt)
        if ';' in sql:
            logger.warning("Multiple statements detected")
            return False
        
        return True
    
    def update_schema(self, schema: Dict[str, Any]) -> None:
        """Update schema context for parser."""
        self.schema = schema
        logger.info("Query parser schema updated")

