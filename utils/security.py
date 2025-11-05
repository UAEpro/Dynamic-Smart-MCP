"""
Security utilities for sanitizing responses and hiding database details.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ResponseSanitizer:
    """Sanitizes responses to hide database internals from end users."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize sanitizer with security configuration.
        
        Args:
            config: Security configuration from config.yaml
        """
        security_config = config.get("security", {})
        
        self.hide_db_details = security_config.get("hide_database_details", True)
        self.expose_sql = security_config.get("expose_sql", False)
        self.expose_columns = security_config.get("expose_column_names", False)
        self.expose_tables = security_config.get("expose_table_names", False)
        self.log_detailed = security_config.get("log_detailed_errors", True)
    
    def sanitize_error(self, error_response: Dict[str, Any], 
                      natural_language: str) -> Dict[str, Any]:
        """
        Sanitize error response to hide database details.
        
        Args:
            error_response: Original error response with technical details
            natural_language: User's original question
            
        Returns:
            Sanitized response safe for end users
        """
        if not self.hide_db_details:
            # Development mode - return full details
            return error_response
        
        # Log detailed error server-side for debugging
        if self.log_detailed:
            logger.error(f"Query error: {error_response}")
        
        # Build generic user-friendly error
        generic_error = {
            "success": False,
            "message": self._get_generic_error_message(natural_language),
            "natural_language": natural_language
        }
        
        return generic_error
    
    def sanitize_success(self, success_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize success response to optionally hide SQL.
        
        Args:
            success_response: Original success response
            
        Returns:
            Sanitized response
        """
        if self.expose_sql:
            # Show SQL query in response
            return success_response
        
        # Remove SQL from response
        sanitized = success_response.copy()
        if "sql" in sanitized:
            # Log SQL server-side
            if self.log_detailed:
                logger.info(f"Executed SQL: {sanitized['sql']}")
            
            # Remove from user response
            del sanitized["sql"]
        
        return sanitized
    
    def _get_generic_error_message(self, natural_language: str) -> str:
        """
        Generate generic, user-friendly error message.
        
        Args:
            natural_language: User's original question
            
        Returns:
            Generic error message
        """
        # Detect language (simple heuristic)
        if self._is_arabic(natural_language):
            return ("عذراً، لم أتمكن من العثور على البيانات المطلوبة. "
                   "يرجى المحاولة بسؤال مختلف أو التحقق من المعلومات المدخلة.")
        elif self._is_chinese(natural_language):
            return "抱歉，无法找到您请求的数据。请尝试不同的问题或检查输入信息。"
        elif self._is_spanish(natural_language):
            return ("Lo siento, no pude encontrar los datos solicitados. "
                   "Por favor, intente con una pregunta diferente.")
        elif self._is_french(natural_language):
            return ("Désolé, je n'ai pas pu trouver les données demandées. "
                   "Veuillez essayer avec une question différente.")
        else:
            # Default: English
            return ("Sorry, I couldn't find the information you requested. "
                   "Please try asking in a different way or check your query.")
    
    def _is_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters."""
        return any('\u0600' <= c <= '\u06FF' for c in text)
    
    def _is_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters."""
        return any('\u4e00' <= c <= '\u9fff' for c in text)
    
    def _is_spanish(self, text: str) -> bool:
        """Simple Spanish detection (has Spanish-specific words)."""
        spanish_words = ['qué', 'cuál', 'cómo', 'muéstrame', 'dame']
        return any(word in text.lower() for word in spanish_words)
    
    def _is_french(self, text: str) -> bool:
        """Simple French detection."""
        french_words = ['montre', 'donne', 'quel', 'quelle', 'combien']
        return any(word in text.lower() for word in french_words)
    
    def sanitize_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize schema response for end users.
        
        Args:
            schema: Full database schema
            
        Returns:
            Sanitized schema (or generic message if hiding details)
        """
        if not self.hide_db_details:
            return schema
        
        # Log schema access
        if self.log_detailed:
            logger.warning("Schema access attempted by user (blocked in production mode)")
        
        return {
            "success": False,
            "message": "Schema information is not available."
        }


def create_user_friendly_response(rows: list, row_count: int, 
                                  natural_language: str) -> Dict[str, Any]:
    """
    Create a user-friendly response without technical details.
    
    Args:
        rows: Query result rows
        row_count: Number of rows returned
        natural_language: User's original question
        
    Returns:
        Clean, user-friendly response
    """
    if row_count == 0:
        return {
            "success": True,
            "message": "No results found for your query.",
            "data": [],
            "count": 0
        }
    
    return {
        "success": True,
        "message": f"Found {row_count} result(s).",
        "data": rows,
        "count": row_count
    }

