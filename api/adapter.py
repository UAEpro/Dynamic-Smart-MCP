"""
API Adapter for OpenAPI/Swagger
Connects to an API using an OpenAPI specification and handles request execution.
"""

import os
import sys
import yaml
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class APIAdapter:
    """Adapter for interacting with APIs defined by OpenAPI/Swagger specs."""

    def __init__(self, spec_source: str, auth_config: Optional[Dict[str, Any]] = None):
        """
        Initialize API adapter.

        Args:
            spec_source: URL or file path to the OpenAPI specification
            auth_config: Authentication configuration (type, token, key_location, etc.)
        """
        self.spec_source = spec_source
        self.auth_config = auth_config or {}
        self.spec: Dict[str, Any] = {}
        self.base_url: str = ""
        self.paths: Dict[str, Any] = {}
        self.schema_cache: Dict[str, Any] = {}

    def load_spec(self) -> None:
        """Load and parse the OpenAPI specification."""
        try:
            logger.info(f"Loading OpenAPI spec from: {self.spec_source}")

            content = ""
            if self.spec_source.startswith(('http://', 'https://')):
                response = requests.get(self.spec_source)
                response.raise_for_status()
                content = response.text
            else:
                if not os.path.exists(self.spec_source):
                    raise FileNotFoundError(f"Spec file not found: {self.spec_source}")
                with open(self.spec_source, 'r') as f:
                    content = f.read()

            # Try parsing as JSON first, then YAML
            try:
                self.spec = json.loads(content)
            except json.JSONDecodeError:
                self.spec = yaml.safe_load(content)

            self._parse_spec()
            logger.info(f"OpenAPI spec loaded. Found {len(self.paths)} paths.")

        except Exception as e:
            logger.error(f"Failed to load OpenAPI spec: {e}")
            raise

    def _parse_spec(self) -> None:
        """Parse the loaded spec to extract base URL and paths."""
        # Determine Base URL
        if 'servers' in self.spec and self.spec['servers']:
            self.base_url = self.spec['servers'][0]['url']
        elif 'host' in self.spec:
            scheme = self.spec.get('schemes', ['https'])[0]
            self.base_url = f"{scheme}://{self.spec['host']}{self.spec.get('basePath', '')}"
        else:
            # Fallback if spec source was a URL
            if self.spec_source.startswith(('http://', 'https://')):
                 parsed = urlparse(self.spec_source)
                 self.base_url = f"{parsed.scheme}://{parsed.netloc}"
            else:
                self.base_url = "" # Should probably raise warning

        # Ensure base_url doesn't have trailing slash
        self.base_url = self.base_url.rstrip('/')

        self.paths = self.spec.get('paths', {})
        self.schema_cache = {
            "info": self.spec.get('info', {}),
            "paths": self.paths,
            "components": self.spec.get('components', {}) or self.spec.get('definitions', {})
        }

    def execute_request(self, method: str, endpoint: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute an HTTP request against the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., /users)
            params: Query parameters
            body: Request body (JSON)

        Returns:
            Dict containing status_code, headers, data, and success status
        """
        if not self.base_url:
             raise ValueError("Base URL not determined from spec")

        # Normalize endpoint
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint

        url = f"{self.base_url}{endpoint}"

        # Prepare headers and auth
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Inject Auth
        auth_type = self.auth_config.get("type", "none")
        if auth_type == "bearer":
            token = self._get_auth_value("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "api_key":
            key = self._get_auth_value("key")
            key_name = self.auth_config.get("key_name", "X-API-Key")
            location = self.auth_config.get("location", "header")

            if key:
                if location == "header":
                    headers[key_name] = key
                elif location == "query":
                    if params is None:
                        params = {}
                    params[key_name] = key

        try:
            logger.info(f"Executing {method} {url}")
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=body,
                timeout=30
            )

            try:
                data = response.json()
            except:
                data = response.text

            return {
                "success": response.ok,
                "status_code": response.status_code,
                "data": data,
                "url": url,
                "method": method
            }

        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "method": method
            }

    def _get_auth_value(self, key_type: str) -> Optional[str]:
        """Helper to get auth value from env or config."""
        # 1. Check direct value in config
        val = self.auth_config.get(key_type)
        if val and not val.startswith('$'):
            return val

        # 2. Check environment variable ref
        if val and val.startswith('$'):
            env_var = val[1:] # Remove $
            return os.getenv(env_var)

        # 3. Check default env var
        env_var_name = self.auth_config.get(f"{key_type}_env")
        if env_var_name:
            return os.getenv(env_var_name)

        return None

    def get_schema(self) -> Dict[str, Any]:
        """Return cached schema information."""
        return self.schema_cache
