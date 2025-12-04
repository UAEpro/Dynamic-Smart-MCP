"""
API Schema Generator
Inspects the OpenAPI spec and uses LLM to generate a rich schema description YAML.
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

from api.adapter import APIAdapter

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

    load_dotenv()
    api_key_env = llm_config.get("api_key_env", "LLM_API_KEY")
    api_key = os.getenv(api_key_env)

    # if not api_key:
    #     logger.error(f"No API key found in {api_key_env}")
    #     sys.exit(1)

    api_base = llm_config.get("api_base")
    client_kwargs = {"api_key": api_key}
    if api_base:
        client_kwargs["base_url"] = api_base

    client = OpenAI(**client_kwargs)
    model = llm_config.get("model", "gpt-3.5-turbo")

    return client, model

def generate_api_description(client, model, api_spec: dict) -> str:
    """Generate YAML schema description using LLM."""

    # Simplify spec for prompt (remove heavy schemas/definitions if too large)
    # Ideally, we want the paths and summaries.
    simple_spec = {
        "info": api_spec.get("info"),
        "paths": {}
    }

    # Copy paths but remove deep details to save context
    for path, methods in api_spec.get("paths", {}).items():
        simple_spec["paths"][path] = {}
        for method, details in methods.items():
            simple_spec["paths"][path][method] = {
                "summary": details.get("summary"),
                "description": details.get("description"),
                "operationId": details.get("operationId")
            }

    prompt = f"""
You are an expert API architect. I will provide you with an OpenAPI specification summary.
Your task is to analyze this API and generate a high-quality, documentation-style YAML description.

The output YAML must follow this exact structure:

description: "A short summary of what this API does."
domain: "The industry or domain (e.g., E-commerce, Weather, Finance)."
business_concepts:
  - "Key concept 1"
  - "Key concept 2"
endpoints:
  /path/example:
    description: "What this endpoint does."
    usage: "When to use this endpoint."
common_tasks:
  - "Example natural language task 1"
  - "Example natural language task 2"

RAW SPECIFICATION:
{json.dumps(simple_spec, indent=2)}

IMPORTANT:
1. Infer the domain and business concepts.
2. Write clear, human-readable descriptions.
3. Return ONLY the YAML content. Do not include markdown code blocks.
"""

    logger.info("Sending API spec to LLM for analysis...")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful API documentation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )

        content = response.choices[0].message.content.strip()

        # Clean up
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
    print("🤖 Smart API Schema Generator")
    print("=" * 60)

    config = load_config()

    # Get API Config
    api_config = config.get("api", {})
    spec_source = os.getenv("API_SPEC_URL") or api_config.get("spec_source")

    if not spec_source:
        logger.error("No API spec source found (api.spec_source or API_SPEC_URL).")
        sys.exit(1)

    print(f"\n1. Loading API spec from {spec_source}...")
    adapter = APIAdapter(spec_source)
    try:
        adapter.load_spec()
    except Exception:
        sys.exit(1)

    raw_spec = adapter.get_schema()

    print("2. Initializing LLM...")
    client, model = initialize_llm(config)

    print(f"3. Generating documentation using {model}...")
    yaml_content = generate_api_description(client, model, raw_spec)

    # Validate YAML
    try:
        yaml.safe_load(yaml_content)
        print("✅ Generated valid YAML")
    except yaml.YAMLError as e:
        logger.error(f"Generated invalid YAML: {e}")
        print("Raw output:")
        print(yaml_content)
        sys.exit(1)

    output_file = "api_schema.yaml"
    print(f"\n4. Saving to {output_file}...")

    with open(output_file, 'w') as f:
        f.write("# Auto-generated API Schema Documentation\n")
        f.write(f"# Generated at: {os.getenv('start_time', 'now')}\n")
        f.write("# Usage: This file is automatically loaded by Smart MCP Server in API mode\n\n")
        f.write(yaml_content)

    print(f"\n✨ Done! API schema documentation saved to {output_file}")

if __name__ == "__main__":
    main()
