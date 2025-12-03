"""
Database Schema Generator
Inspects the database and uses LLM to generate a rich schema description YAML.
"""

import os
import sys
import yaml
import logging
import json
from dotenv import load_dotenv
from openai import OpenAI

# Ensure we can import from local modules
sys.path.append(os.getcwd())

from db.adapter import DatabaseAdapter
from utils.schema import schema_to_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

def initialize_llm(config: dict) -> tuple:
    """Initialize OpenAI client and get model info."""
    llm_config = config.get("llm", {})

    # Get API key from environment
    load_dotenv()
    api_key_env = llm_config.get("api_key_env", "LLM_API_KEY")
    api_key = os.getenv(api_key_env)

    if not api_key:
        logger.error(f"No API key found in {api_key_env}")
        sys.exit(1)

    api_base = llm_config.get("api_base")
    client_kwargs = {"api_key": api_key}
    if api_base:
        client_kwargs["base_url"] = api_base

    client = OpenAI(**client_kwargs)
    model = llm_config.get("model", "gpt-3.5-turbo")

    return client, model

def generate_schema_description(client, model, db_schema: dict) -> str:
    """Generate YAML schema description using LLM."""

    # Prepare prompt with raw schema
    prompt = f"""
You are an expert database architect. I will provide you with a raw database schema (tables, columns, foreign keys, and sample data).
Your task is to analyze this schema and generate a high-quality, documentation-style YAML description of the database.

The output YAML must follow this exact structure:

description: "A short summary of what this database contains."
domain: "The industry or domain (e.g., E-commerce, Finance, Healthcare)."
business_concepts:
  - "Key concept 1"
  - "Key concept 2"
tables:
  table_name:
    description: "What this table stores."
    notes: "Any specific details, constraints, or usage notes."
common_queries:
  - "Example natural language query 1"
  - "Example natural language query 2"
conventions:
  dates: "Date format used"
  currency: "Currency used (if applicable)"

RAW SCHEMA:
{json.dumps(db_schema, indent=2, default=str)}

IMPORTANT:
1. Infer the domain and business concepts from the table names and data.
2. Write clear, human-readable descriptions.
3. Return ONLY the YAML content. Do not include markdown code blocks (```yaml).
4. Ensure the YAML is valid.
"""

    logger.info("Sending schema to LLM for analysis...")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful database documentation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )

        content = response.choices[0].message.content.strip()

        # Clean up if LLM added markdown blocks
        if content.startswith("```yaml"):
            content = content.replace("```yaml", "", 1)
        if content.startswith("```"):
            content = content.replace("```", "", 1)
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]

        return content.strip()

    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("🤖 Smart Database Schema Generator")
    print("=" * 60)

    # Load config
    config = load_config()

    # Connect to DB
    print("\n1. Connecting to database...")
    db_config = config.get("database", {})
    conn_str = os.getenv("DATABASE_URL") or db_config.get("connection_string")

    if not conn_str:
        logger.error("No connection string found.")
        sys.exit(1)

    adapter = DatabaseAdapter(conn_str)
    try:
        adapter.connect()
    except Exception:
        sys.exit(1)

    # Get schema
    print("2. extracting schema and sample data...")
    raw_schema = adapter.get_schema()

    # Initialize LLM
    print("3. Initializing LLM...")
    client, model = initialize_llm(config)

    # Generate description
    print(f"4. Generating documentation using {model}...")
    yaml_content = generate_schema_description(client, model, raw_schema)

    # Validate YAML
    try:
        parsed_yaml = yaml.safe_load(yaml_content)
        print("✅ Generated valid YAML")
    except yaml.YAMLError as e:
        logger.error(f"Generated invalid YAML: {e}")
        print("Raw output:")
        print(yaml_content)
        sys.exit(1)

    # Save to file
    output_file = "database_schema.yaml"
    print(f"\n5. Saving to {output_file}...")

    with open(output_file, 'w') as f:
        f.write("# Auto-generated Database Schema Documentation\n")
        f.write(f"# Generated at: {raw_schema.get('last_refresh', 'now')}\n")
        f.write("# Usage: This file is automatically loaded by Smart MCP Server\n\n")
        f.write(yaml_content)

    print(f"\n✨ Done! Database schema documentation saved to {output_file}")
    adapter.close()

if __name__ == "__main__":
    main()
