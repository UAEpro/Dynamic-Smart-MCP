"""
Smart MCP Server - Main Entry Point
FastMCP 2 server with intelligent database querying and API interaction.
"""

import os
import sys
import logging
import yaml
from dotenv import load_dotenv
from fastmcp import FastMCP

# Import our modules
from db.adapter import DatabaseAdapter
from nlp.query_parser import QueryParser
from mcp_server.tools import register_tools

from api.adapter import APIAdapter
from nlp.api_request_parser import APIRequestParser
from mcp_server.api_tools import register_api_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        # logging.FileHandler('smart-mcp.log')
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file with .env overrides."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Make config_path absolute if it's relative
        if not os.path.isabs(config_path):
            config_path = os.path.join(script_dir, config_path)

        # Load main config (or create empty if not exists)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"Configuration loaded from {config_path}")
        else:
            logger.warning(f"Config file not found: {config_path}, using .env only")
            config = {}

        # Apply .env overrides for top-level settings
        # Priority: .env -> config.yaml
        config["mode"] = os.getenv("MODE") or config.get("mode", "database")
        
        # Database config overrides
        if "database" not in config:
            config["database"] = {}
        config["database"]["connection_string"] = os.getenv("DATABASE_URL") or config["database"].get("connection_string")
        config["database"]["max_rows"] = int(os.getenv("DATABASE_MAX_ROWS") or config["database"].get("max_rows", 1000))
        
        # API config overrides
        if "api" not in config:
            config["api"] = {}
        config["api"]["spec_source"] = os.getenv("API_SPEC_URL") or config["api"].get("spec_source")
        config["api"]["unsafe_mode"] = os.getenv("API_UNSAFE_MODE", "").lower() == "true" or config["api"].get("unsafe_mode", False)
        
        # Safety config overrides
        if "safety" not in config:
            config["safety"] = {}
        if os.getenv("SAFETY_READ_ONLY"):
            config["safety"]["read_only"] = os.getenv("SAFETY_READ_ONLY").lower() == "true"
        
        # Security config overrides
        if "security" not in config:
            config["security"] = {}
        if os.getenv("SECURITY_HIDE_DATABASE_DETAILS"):
            config["security"]["hide_database_details"] = os.getenv("SECURITY_HIDE_DATABASE_DETAILS").lower() == "true"
        if os.getenv("SECURITY_EXPOSE_SQL"):
            config["security"]["expose_sql"] = os.getenv("SECURITY_EXPOSE_SQL").lower() == "true"
        if os.getenv("SECURITY_EXPOSE_COLUMN_NAMES"):
            config["security"]["expose_column_names"] = os.getenv("SECURITY_EXPOSE_COLUMN_NAMES").lower() == "true"
        if os.getenv("SECURITY_EXPOSE_TABLE_NAMES"):
            config["security"]["expose_table_names"] = os.getenv("SECURITY_EXPOSE_TABLE_NAMES").lower() == "true"
        if os.getenv("SECURITY_LOG_DETAILED_ERRORS"):
            config["security"]["log_detailed_errors"] = os.getenv("SECURITY_LOG_DETAILED_ERRORS").lower() == "true"
        
        # Determine Schema File to load based on Mode
        mode = config.get("mode", "database")
        schema_file = "database_schema.yaml" if mode == "database" else "api_schema.yaml"
        schema_path = os.path.join(script_dir, schema_file)

        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r') as f:
                    schema_context = yaml.safe_load(f)

                # Merge into config
                if schema_context:
                    # We store it under a generic key 'context' but keep legacy support for 'database_context'
                    config["database_context"] = schema_context # Legacy support
                    config["schema_context"] = schema_context   # New generic key
                    logger.info(f"Loaded external schema from {schema_path}")
            except Exception as e:
                logger.warning(f"Failed to load {schema_path}: {e}")

        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        raise


def initialize_database(config: dict) -> DatabaseAdapter:
    """Initialize and connect to database."""
    db_config = config.get("database", {})
    
    connection_string = db_config.get("connection_string")
    
    if not connection_string:
        raise ValueError("No database connection string provided (DATABASE_URL or database.connection_string)")
    
    max_rows = db_config.get("max_rows", 1000)
    
    logger.info(f"Connecting to database: {connection_string.split('://')[0]}://...")
    
    adapter = DatabaseAdapter(connection_string, max_rows)
    adapter.connect()
    
    return adapter

def initialize_api(config: dict) -> APIAdapter:
    """Initialize and connect to API."""
    api_config = config.get("api", {})

    spec_source = api_config.get("spec_source")

    if not spec_source:
        raise ValueError("No API spec source provided (API_SPEC_URL or api.spec_source)")

    logger.info(f"Loading API Spec from: {spec_source}")

    adapter = APIAdapter(spec_source, api_config.get("auth"))
    adapter.load_spec()

    return adapter


def initialize_llm(config: dict) -> dict:
    """Prepare LLM configuration. Priority: .env -> config.yaml"""
    llm_config = config.get("llm", {})
    
    # Priority: .env -> config.yaml
    api_key = os.getenv("LLM_API_KEY") or llm_config.get("api_key_env")
    
    if not api_key:
        logger.warning("No API key found in .env (LLM_API_KEY) or config.yaml (llm.api_key_env)")
        api_key = "dummy-key"  # Some providers don't require auth
    
    llm_config["api_key"] = api_key
    llm_config["api_key_env"] = api_key  # Keep for compatibility
    
    # Priority: .env -> config.yaml for all settings
    llm_config["model"] = os.getenv("LLM_MODEL") or llm_config.get("model") or "gpt-3.5-turbo"
    llm_config["api_base"] = os.getenv("LLM_API_BASE") or llm_config.get("api_base")
    
    if os.getenv("LLM_TEMPERATURE"):
        llm_config["temperature"] = float(os.getenv("LLM_TEMPERATURE"))
    
    # Add context to LLM config
    if "schema_context" in config:
        llm_config["database_context"] = config["schema_context"] # Using legacy key for compatibility
        logger.info("Schema context loaded")
    elif "database_context" in config:
        llm_config["database_context"] = config["database_context"]
        logger.info("Database context loaded")
    
    logger.info(f"LLM configured: {llm_config.get('provider')} / {llm_config.get('model')}")
    
    return llm_config


def create_server(config: dict, adapter, parser) -> FastMCP:
    """Create and configure FastMCP server."""
    server_config = config.get("server", {})
    mode = config.get("mode", "database")
    
    # Initialize FastMCP server
    mcp = FastMCP(
        name=server_config.get("name", "smart-mcp-server"),
        version=server_config.get("version", "1.0.0"),
    )
    
    logger.info(f"FastMCP server created: {mcp.name} v{mcp.version} (Mode: {mode.upper()})")
    
    # Register tools based on mode
    if mode == "database":
        register_tools(mcp, adapter, parser, config)
    elif mode == "api":
        register_api_tools(mcp, adapter, parser, config)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    logger.info("Tools registered successfully")
    
    return mcp


def main():
    """Main entry point for Smart MCP Server."""
    adapter = None
    try:
        logger.info("=" * 80)
        logger.info("Starting Smart MCP Server")
        logger.info("=" * 80)
        
        # Load configuration
        config = load_config()
        mode = config.get("mode", "database")
        
        # Initialize LLM configuration
        llm_config = initialize_llm(config)
        
        if mode == "database":
            # Database Mode
            adapter = initialize_database(config)
            schema = adapter.get_schema()
            parser = QueryParser(llm_config, schema)

            logger.info(f"Connected to: {adapter.schema_cache.get('database_type', 'Unknown')}")
            logger.info(f"Tables found: {len(adapter.schema_cache.get('tables', {}))}")

        elif mode == "api":
            # API Mode
            adapter = initialize_api(config)
            schema = adapter.get_schema()
            unsafe_mode = config.get("api", {}).get("unsafe_mode", False)
            parser = APIRequestParser(llm_config, schema, unsafe_mode=unsafe_mode)

            logger.info(f"Loaded API: {schema.get('info', {}).get('title', 'Unknown')}")
            logger.info(f"Endpoints found: {len(schema.get('paths', {}))}")

        else:
            logger.error(f"Invalid mode specified in config: {mode}")
            sys.exit(1)
        
        # Create MCP server
        mcp = create_server(config, adapter, parser)
        
        logger.info("=" * 80)
        logger.info("Smart MCP Server is ready!")
        logger.info("=" * 80)
        
        # Run the server
        mcp.run()
        # or run the server as http server
        # mcp.run_http_server(host="0.0.0.0", port=8000) 

    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        if adapter and hasattr(adapter, 'close'):
            try:
                adapter.close()
            except:
                pass


if __name__ == "__main__":
    main()
