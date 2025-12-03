"""
Smart MCP Server - Main Entry Point
FastMCP 2 server with intelligent database querying via natural language.
"""

import os
import sys
import logging
from pathlib import Path
import yaml
from dotenv import load_dotenv
from fastmcp import FastMCP

# Import our modules
from db.adapter import DatabaseAdapter
from nlp.query_parser import QueryParser
from mcp_server.tools import register_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('smart-mcp.log')
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:

        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Make config_path absolute if it's relative
        if not os.path.isabs(config_path):
            config_path = os.path.join(script_dir, config_path)

        # Load main config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")

        # Check for external schema file
        schema_path = os.path.join(script_dir, "database_schema.yaml")
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r') as f:
                    schema_context = yaml.safe_load(f)

                # Merge into config
                if schema_context:
                    config["database_context"] = schema_context
                    logger.info(f"Loaded external database schema from {schema_path}")
            except Exception as e:
                logger.warning(f"Failed to load {schema_path}: {e}")

        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        raise


def initialize_database(config: dict) -> DatabaseAdapter:
    """Initialize and connect to database."""
    db_config = config.get("database", {})
    
    # Allow environment variable override
    connection_string = os.getenv("DATABASE_URL") or db_config.get("connection_string")
    
    if not connection_string:
        raise ValueError("No database connection string provided")
    
    max_rows = db_config.get("max_rows", 1000)
    
    logger.info(f"Connecting to database: {connection_string.split('://')[0]}://...")
    
    adapter = DatabaseAdapter(connection_string, max_rows)
    adapter.connect()
    
    return adapter


def initialize_llm(config: dict) -> dict:
    """Prepare LLM configuration with API key from environment."""
    llm_config = config.get("llm", {})
    
    # Get API key from environment
    api_key_env = llm_config.get("api_key_env", "LLM_API_KEY")
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        logger.warning(f"No API key found in environment variable {api_key_env}")
        api_key = "dummy-key"  # Some providers don't require auth
    
    llm_config["api_key"] = api_key
    
    # Allow environment overrides
    if os.getenv("LLM_MODEL"):
        llm_config["model"] = os.getenv("LLM_MODEL")
    if os.getenv("LLM_TEMPERATURE"):
        llm_config["temperature"] = float(os.getenv("LLM_TEMPERATURE"))
    
    # Add database context to LLM config (improves query quality)
    if "database_context" in config:
        llm_config["database_context"] = config["database_context"]
        logger.info("Database context loaded - queries will be more accurate")
    
    logger.info(f"LLM configured: {llm_config.get('provider')} / {llm_config.get('model')}")
    
    return llm_config


def create_server(config: dict, db_adapter: DatabaseAdapter, query_parser: QueryParser) -> FastMCP:
    """Create and configure FastMCP server."""
    server_config = config.get("server", {})
    
    # Initialize FastMCP server
    mcp = FastMCP(
        name=server_config.get("name", "smart-mcp-server"),
        version=server_config.get("version", "1.0.0"),
    )
    
    logger.info(f"FastMCP server created: {mcp.name} v{mcp.version}")
    
    # Register tools
    register_tools(mcp, db_adapter, query_parser, config)
    logger.info("All tools registered successfully")
    
    return mcp


def main():
    """Main entry point for Smart MCP Server."""
    try:
        logger.info("=" * 80)
        logger.info("Starting Smart MCP Server")
        logger.info("=" * 80)
        
        # Load configuration
        config = load_config()
        
        # Initialize database
        db_adapter = initialize_database(config)
        
        # Initialize LLM configuration
        llm_config = initialize_llm(config)
        
        # Initialize query parser
        schema = db_adapter.get_schema()
        query_parser = QueryParser(llm_config, schema)
        
        # Create MCP server
        mcp = create_server(config, db_adapter, query_parser)
        
        logger.info("=" * 80)
        logger.info("Smart MCP Server is ready!")
        logger.info(f"Connected to: {db_adapter.schema_cache.get('database_type', 'Unknown')}")
        logger.info(f"Tables found: {len(db_adapter.schema_cache.get('tables', {}))}")
        logger.info("=" * 80)
        
        # Run the server
        mcp.run()
        # mcp.run(transport='http', port=8765)

    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        try:
            db_adapter.close()
        except:
            pass


if __name__ == "__main__":
    main()

