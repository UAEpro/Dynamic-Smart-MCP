# 🚀 Quick Start Guide

Get Smart MCP Server running in 5 minutes!

---

## Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

---

## Step 2: Create Sample Database (30 seconds)

```bash
python example_database.py
```

This creates `example.db` with sample customers, products, and orders.

---

## Step 3: Configure LLM API Key (1 min)

Create a `.env` file:

```bash
# Copy the template
cp env.example.txt .env

# Edit .env and add your API key
# For OpenWebUI: get key from Settings → Account → API Keys
# For OpenAI: get from https://platform.openai.com/api-keys
```

Your `.env` should look like:
```env
LLM_API_KEY=sk-your-actual-key-here
```

---

## Step 4: Update Config (optional)

The default `config.yaml` is already set up for the example database.

If using **OpenAI** instead of OpenWebUI, edit `config.yaml`:

```yaml
llm:
  provider: "openai"
  api_base: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
```

---

## Step 5: Run the Server (30 seconds)

```bash
python main.py
```

You should see:
```
================================================================================
Smart MCP Server is ready!
Connected to: sqlite
Tables found: 5
================================================================================
```

---

## Step 6: Test Queries 🎉

Your MCP server is now running! Connect with your MCP client and try these queries:

### Basic
```
"Show me all customers"
"List all products"
```

### Analytics
```
"What are the top 5 most expensive products?"
"Show me total revenue by category"
"What is the average order value?"
```

### Complex
```
"Show me all orders with customer names and order totals"
"Which customers haven't placed any orders?"
"What are the monthly sales trends?"
```

---

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'mcp'"

**Solution:**
```bash
pip install fastmcp>=2.0.0
```

### ❌ "Database connection failed"

**Solution:** The database path in `config.yaml` should be:
```yaml
database:
  connection_string: "sqlite:///example.db"
```

### ❌ "Query parsing failed" or "401 Unauthorized"

**Solution:**
1. Check your `.env` file has the correct API key
2. Verify the key with:
   ```bash
   cat .env
   ```
3. Make sure `api_base` in config.yaml matches your LLM provider

### ❌ "ImportError: No module named 'pymysql'"

**Solution:** This is only needed for MySQL. For SQLite (default), you don't need it.

---

## Using Your Own Database

1. Update `config.yaml` with your connection string:

```yaml
database:
  # PostgreSQL
  connection_string: "postgresql://user:password@localhost:5432/mydb"
  
  # MySQL
  # connection_string: "mysql+pymysql://user:password@localhost:3306/mydb"
  
  # SQL Server
  # connection_string: "mssql+pyodbc://user:password@localhost/mydb?driver=ODBC+Driver+17+for+SQL+Server"
```

2. Install the appropriate driver:
```bash
pip install psycopg2-binary  # PostgreSQL
pip install pymysql          # MySQL
pip install pyodbc           # SQL Server
```

3. Restart the server:
```bash
python main.py
```

---

## Next Steps

- Read documentation in `docs/` folder (start with 01, 02, 03...)
- Check `config.yaml` for all configuration options
- Explore the code in `db/`, `nlp/`, `mcp/`, and `utils/`
- Customize prompts in `nlp/query_parser.py`
- Add new tools in `mcp/tools.py`

---

**Need Help?** Check the logs in `smart-mcp.log` or open an issue on GitHub.

**Happy Querying! 🎉**

