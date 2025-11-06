# 🏗️ Architecture Overview

Understanding Smart MCP Server's design and components.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         MCP Client                          │
│                    (Claude, Custom App)                     │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Protocol
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastMCP Server                         │
│                        (main.py)                            │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              MCP Tools (mcp/tools.py)                 │ │
│  │  • query_database()                                   │ │
│  │  • get_database_schema()                              │ │
│  │  • refresh_database_schema()                          │ │
│  │  • get_query_examples()                               │ │
│  └───────────┬───────────────────────────┬───────────────┘ │
└──────────────┼───────────────────────────┼─────────────────┘
               │                           │
               ▼                           ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │   Query Parser       │    │  Database Adapter    │
    │ (nlp/query_parser.py)│    │   (db/adapter.py)    │
    │                      │    │                      │
    │ • NL → SQL           │    │ • Universal DB conn  │
    │ • Schema context     │    │ • Schema scanning    │
    │ • Safety validation  │    │ • Query execution    │
    └──────────┬───────────┘    └──────────┬───────────┘
               │                           │
               ▼                           ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │   LLM Provider       │    │   SQL Database       │
    │  (OpenAI/OpenWebUI)  │    │  (Any SQLAlchemy)    │
    └──────────────────────┘    └──────────────────────┘
```

---

## Component Details

### 1. **main.py** - Server Initialization
**Purpose:** Bootstrap and coordinate all components

**Responsibilities:**
- Load configuration from `config.yaml`
- Initialize database connection
- Set up LLM client
- Create FastMCP server
- Register tools
- Handle graceful shutdown

**Key Functions:**
- `load_config()` - Parse YAML configuration
- `initialize_database()` - Connect to DB and load schema
- `initialize_llm()` - Set up LLM with API credentials
- `create_server()` - Create FastMCP instance and register tools

---

### 2. **db/adapter.py** - Universal Database Adapter
**Purpose:** Abstract database operations across different SQL engines

**Key Features:**
- ✅ Auto-detect database dialect (MySQL, PostgreSQL, SQLite, etc.)
- ✅ Reflect complete schema on connection
- ✅ Cache schema in memory for performance
- ✅ Execute queries with safety limits
- ✅ Handle connection pooling

**Core Class:** `DatabaseAdapter`

**Methods:**
- `connect()` - Establish connection and load schema
- `refresh_schema()` - Rescan database structure
- `execute_query(sql)` - Run SQL and return results
- `get_schema()` - Return cached schema dict
- `_get_sample_data()` - Fetch sample rows for context
- `_get_row_count()` - Count rows per table

**Schema Cache Structure:**
```python
{
    "database_type": "postgresql",
    "tables": {
        "customers": {
            "columns": [...],
            "foreign_keys": [...],
            "sample_data": [...],
            "row_count": 1234
        }
    }
}
```

---

### 3. **nlp/query_parser.py** - Natural Language to SQL
**Purpose:** Convert user questions to safe SQL queries

**Architecture:**
1. **Prompt Engineering**
   - Include full database schema
   - Add example query patterns
   - Specify safety rules
   - Format for LLM understanding

2. **LLM Integration**
   - Use OpenAI-compatible API
   - Support multiple providers (OpenAI, OpenWebUI, etc.)
   - Temperature 0.0 for deterministic output

3. **Safety Validation**
   - Block dangerous keywords (DROP, DELETE, etc.)
   - Enforce SELECT-only mode
   - Detect SQL injection attempts
   - Validate query structure

**Core Class:** `QueryParser`

**Methods:**
- `parse(natural_language)` - Main NL→SQL conversion
- `_build_prompt()` - Construct LLM prompt with schema
- `_clean_sql()` - Remove markdown, normalize whitespace
- `_is_safe_query()` - Validate query safety

**Prompt Template Structure:**
```
SAFETY RULES
→ Read-only, SELECT only
→ No dangerous operations

DATABASE SCHEMA
→ Tables, columns, types
→ Foreign keys
→ Sample data

EXAMPLE QUERIES
→ 10 common patterns

USER QUESTION
→ Natural language input

OUTPUT: SQL query only
```

---

### 4. **mcp/tools.py** - MCP Tool Definitions
**Purpose:** Define the tools exposed via MCP protocol

**Tools:**

#### `query_database(natural_language: str)`
- **Input:** Natural language question
- **Process:** 
  1. Parse NL to SQL
  2. Validate safety
  3. Execute query
  4. Format results
- **Output:** JSON with SQL and results

#### `get_database_schema()`
- **Output:** Complete schema as JSON

#### `refresh_database_schema()`
- **Process:** Trigger schema rescan
- **Output:** Success message with table count

#### `get_query_examples()`
- **Output:** Categorized example queries

**Tool Registration:**
```python
@mcp.tool()
def query_database(natural_language: str) -> str:
    # Implementation
```

---

### 5. **utils/schema.py** - Schema Utilities
**Purpose:** Format and present schema information

**Functions:**

- `format_schema_for_llm(schema)` → Human-readable schema text
- `format_examples_for_llm()` → Example query patterns
- `get_example_queries()` → List of NL/SQL pairs
- `get_safety_rules()` → SQL safety guidelines
- `schema_to_json(schema)` → Pretty JSON output

**Schema Formatting Strategy:**
```
DATABASE TYPE: postgresql
TOTAL TABLES: 5

TABLE: customers
Rows: ~1234
----------------------------------------
COLUMNS:
  - id: INTEGER [PRIMARY KEY]
  - name: TEXT [NOT NULL]
  - email: TEXT
FOREIGN KEYS:
  - customer_id -> orders(id)
SAMPLE DATA:
  Row 1: id=1, name=John, ...
```

---

## Data Flow

### Query Execution Flow

```
1. MCP Client
   ↓ "Show me all customers from USA"
   
2. FastMCP Server (mcp/tools.py)
   ↓ query_database() tool called
   
3. Query Parser (nlp/query_parser.py)
   ↓ Build prompt with schema
   ↓ Call LLM API
   ↓ Parse response
   ↓ Validate safety
   ← "SELECT * FROM customers WHERE country = 'USA' LIMIT 1000"
   
4. Database Adapter (db/adapter.py)
   ↓ Execute SQL
   ↓ Fetch results
   ← [{id: 1, name: "John", country: "USA"}, ...]
   
5. Format Response
   ↓ Convert to JSON
   
6. MCP Client
   ← JSON response with data
```

### Schema Refresh Flow

```
1. Server Start OR Manual Refresh
   ↓
2. Database Adapter
   ↓ Connect to database
   ↓ Use SQLAlchemy inspector
   ↓ Iterate all tables
   ↓ Extract columns, types, keys
   ↓ Fetch sample data
   ↓ Count rows
   ↓ Build schema dict
   ↓ Cache in memory
   
3. Query Parser
   ↓ Update schema reference
   
4. Ready for queries
```

---

## Configuration System

### config.yaml Structure

```yaml
database:          # Database connection
  connection_string
  schema_cache_ttl
  max_rows

llm:              # LLM settings
  provider
  api_base
  model
  temperature
  max_tokens

safety:           # Security rules
  read_only
  allowed_commands
  blocked_keywords

server:           # Server metadata
  name
  version
  log_level
```

### Environment Variables (.env)

```
LLM_API_KEY        # Required
DATABASE_URL       # Optional override
LLM_MODEL          # Optional override
```

---

## Security Architecture

### Multi-Layer Safety

1. **Configuration Layer**
   - `read_only: true` in config.yaml
   - Explicit allowed commands list

2. **Parsing Layer** (nlp/query_parser.py)
   - Keyword blacklist
   - Must start with SELECT
   - No multiple statements (`;` check)

3. **Execution Layer** (db/adapter.py)
   - Auto-add LIMIT if missing
   - SQLAlchemy parameter binding
   - Connection pooling with timeouts

4. **Output Layer**
   - Row count limits
   - Error message sanitization

---

## Extension Points

### Adding New Database Types

**Where:** `db/adapter.py`

**How:**
1. Install SQLAlchemy driver
2. Update connection string
3. No code changes needed (auto-detection)

### Custom LLM Providers

**Where:** `nlp/query_parser.py`

**How:**
1. Update `api_base` in config
2. Ensure OpenAI-compatible API
3. Adjust model name

### New MCP Tools

**Where:** `mcp/tools.py`

**How:**
```python
@mcp.tool()
def your_new_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return json.dumps(result)
```

### Enhanced Prompts

**Where:** `nlp/query_parser.py` → `_build_prompt()`

**How:**
- Add domain-specific examples
- Include business rules
- Add column descriptions

---

## Performance Considerations

### Schema Caching
- ✅ Schema loaded once on startup
- ✅ Manual refresh via tool
- ✅ TTL-based auto-refresh (optional)

### Query Optimization
- ✅ Automatic LIMIT clause addition
- ✅ Connection pooling
- ✅ Result pagination support

### LLM Efficiency
- ✅ Temperature 0.0 (deterministic)
- ✅ Low max_tokens (SQL is short)
- ✅ Streaming not needed

---

## Error Handling

### Database Errors
```python
try:
    result = execute_query(sql)
except SQLAlchemyError as e:
    return {"success": False, "error": str(e)}
```

### LLM Errors
```python
try:
    sql = llm_call()
    if not is_safe(sql):
        return {"error": "Unsafe query"}
except Exception as e:
    return {"error": f"Parsing failed: {e}"}
```

### Graceful Degradation
- Schema refresh failures → Use cached schema
- LLM timeout → Return error to client
- DB connection lost → Attempt reconnect

---

## Testing Strategy

### Unit Tests (TODO)
- `test_adapter.py` - Database operations
- `test_parser.py` - Query parsing
- `test_schema.py` - Schema formatting

### Integration Tests (TODO)
- End-to-end query flow
- Multiple database types
- Error scenarios

### Manual Testing
```bash
python example_database.py  # Create test DB
python main.py              # Start server
# Test with MCP client
```

---

## Future Enhancements

### Short Term
- [ ] Write operation support (with extra safety)
- [ ] Query result caching
- [ ] Multiple database connections
- [ ] Custom date parsing ("last week" → SQL)

### Long Term
- [ ] Query history and learning
- [ ] Smart column name guessing
- [ ] Auto-generated dashboards
- [ ] GraphQL-style query interface

---

## Dependencies

### Core
- **fastmcp** - MCP server framework
- **sqlalchemy** - Database abstraction
- **openai** - LLM API client
- **pyyaml** - Config parsing

### Database Drivers
- **pymysql** - MySQL/MariaDB
- **psycopg2** - PostgreSQL
- **pyodbc** - SQL Server

### Utilities
- **python-dotenv** - Environment variables
- **pydantic** - Data validation

---

## Performance Metrics

### Typical Query Flow Timing
```
Schema Load (startup):     500ms - 2s
NL to SQL (LLM call):      500ms - 3s
SQL Execution:             10ms - 500ms
Result Formatting:         10ms - 100ms
─────────────────────────────────────
Total (first query):       ~1-6 seconds
Total (cached schema):     ~500ms - 4s
```

### Memory Usage
```
Base Python:               ~50MB
SQLAlchemy + Schema:       ~100MB
FastMCP Server:            ~150MB
Per-query overhead:        ~1-5MB
```

---

**Need deeper details on any component?** Check the inline comments in the source code - every file is heavily documented!

