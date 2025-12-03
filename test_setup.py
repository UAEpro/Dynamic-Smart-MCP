"""
Setup Test Script
Run this to verify your Smart MCP Server installation is correct.
"""

import sys
import importlib

def check_import(module_name: str) -> bool:
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("Smart MCP Server - Setup Test")
    print("=" * 60)
    print()
    
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required (you have {sys.version})")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print()
    
    print("Checking required dependencies...")
    required_modules = [
        "fastmcp",
        "sqlalchemy",
        "yaml",
        "dotenv",
        "openai",
        "pydantic",
    ]
    
    all_ok = True
    for module in required_modules:
        if not check_import(module):
            all_ok = False
    print()
    
    print("Checking optional database drivers...")
    optional_modules = [
        "pymysql",
        "psycopg2",
        "pyodbc",
    ]
    
    for module in optional_modules:
        check_import(module)  # Don't fail if optional modules missing
    print()
    
    print("Checking project modules...")
    project_modules = [
        "db.adapter",
        "nlp.query_parser",
        "mcp_server.tools",
        "utils.schema",
    ]
    
    for module in project_modules:
        if not check_import(module):
            all_ok = False
    print()
    
    print("=" * 60)
    if all_ok:
        print("✅ All checks passed! Your setup is ready.")
        print()
        print("Next steps:")
        print("1. Edit config.yaml with your database connection")
        print("2. Create .env file with your LLM_API_KEY")
        print("3. Run: python main.py")
    else:
        print("❌ Some checks failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

