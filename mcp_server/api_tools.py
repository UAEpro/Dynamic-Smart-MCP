"""
MCP Tool Definitions for API
Defines FastMCP tools for API interaction.
"""

import json
from typing import Dict, Any
from fastmcp import FastMCP
from utils.security import ResponseSanitizer

def register_api_tools(mcp: FastMCP, api_adapter, request_parser, config: Dict[str, Any]) -> None:
    """
    Register API tools with the server.
    """

    # Initialize sanitizer (reusing existing one)
    sanitizer = ResponseSanitizer(config)

    @mcp.tool()
    def call_api(natural_language: str) -> str:
        """
        Execute an API request generated from natural language.

        Args:
            natural_language: A request in plain English (e.g., "Get user 123")

        Returns:
            JSON string with API response or error
        """
        try:
            # Parse NL to Request
            parse_result = request_parser.parse(natural_language)

            if not parse_result.get("success"):
                return json.dumps({
                    "success": False,
                    "error": parse_result.get("error"),
                    "natural_language": natural_language
                }, indent=2)

            # Execute Request
            result = api_adapter.execute_request(
                method=parse_result["method"],
                endpoint=parse_result["endpoint"],
                params=parse_result["params"],
                body=parse_result["body"]
            )

            # Decorate result with metadata
            response = {
                "success": result["success"],
                "data": result.get("data"),
                "status": result.get("status_code"),
                "method": result.get("method"),
                "url": result.get("url")
            }

            if not result["success"]:
                 response["error"] = result.get("error")

            # Sanitize response
            sanitized = sanitizer.sanitize_success(response)
            return json.dumps(sanitized, indent=2, default=str)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)

    @mcp.tool()
    def get_api_schema() -> str:
        """Get the available API endpoints and structure."""
        try:
            schema = api_adapter.get_schema()
            # Depending on size, we might want to truncate or summarize
            # For now, return basic info and path list
            summary = {
                "info": schema.get("info"),
                "paths": list(schema.get("paths", {}).keys())
            }
            return json.dumps(summary, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool()
    def refresh_api_spec() -> str:
        """Reload the OpenAPI specification."""
        try:
            api_adapter.load_spec()
            return json.dumps({"success": True, "message": "API spec reloaded"})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
