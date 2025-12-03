# Smart MCP Server 🚀

**Intelligent SQL Database Interface with Natural Language Support**

A production-ready [FastMCP 2](https://github.com/jlowin/fastmcp) server that connects to **any SQL database** (MySQL, PostgreSQL, SQLite, SQL Server, Oracle, etc.) and converts natural language questions into SQL queries using AI.

---

## ✨ Features

- 🔌 **Universal Database Support**: MySQL, PostgreSQL, SQLite, SQL Server, Oracle, MariaDB
- 🧠 **Natural Language to SQL**: Ask questions in plain English, get SQL results
- 🔍 **Auto-Schema Detection**: Automatically scans and understands your database structure
- 🛡️ **Safety First**: Read-only by default, blocks dangerous operations
- ⚡ **FastMCP 2 Powered**: Modern, efficient MCP server implementation
- 🎯 **Zero Configuration**: Works with any schema without prior setup
- 🔧 **Extensible**: Clean, documented code for easy customization

---

## 📚 Documentation

**All documentation is organized in the [docs/](docs/) folder with priority numbers for easy reading order.**

### Quick Links:
- **[docs/00_READ_ME_FIRST.md](docs/00_READ_ME_FIRST.md)** - 📖 **Start here!**
- **[docs/01_QUICKSTART.md](docs/01_QUICKSTART.md)** - 🚀 Get running in 5 minutes
- **[docs/02_DATABASE_DOCUMENTATION_GUIDE.md](docs/02_DATABASE_DOCUMENTATION_GUIDE.md)** - Document your DB for better queries
- **[docs/03_PRODUCTION_SECURITY.md](docs/03_PRODUCTION_SECURITY.md)** - 🔒 **Security guide (CRITICAL)**

**→ See [docs/00_READ_ME_FIRST.md](docs/00_READ_ME_FIRST.md) for complete reading order**

---

## 🚀 Quick Start

### 1. Crate Environment
```bash
python3 -m venv .venv
```
#### On Linux/Mac:
```bash
source .venv/bin/activate
```
##### On Windows:

```bash
.venv\Scripts\activate
```


### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Edit config.yaml with LLM connector and Database Connector
you can also setup the key from .env file

### 4. Run the automatic database Schema generator
```bash
python generate_schema.py
```

### 5. Run the Server
```bash
python main.py
```

you might need to edit the main.py in the main function to change the MCP starting protocol


---

## 🎯 Example Queries

Try these natural language questions:

```
"Show me all customers"
"What are the top 5 most expensive products?"
"Show me orders with customer names"
"What is the total revenue by category?"
"List customers who placed orders in the last 30 days"
```

---

## 🛠️ Tech Stack

- **FastMCP 2** - MCP server framework
- **SQLAlchemy 2.x** - Universal database adapter
- **OpenAI API** - Natural language processing
- **Python 3.8+** - Core language

---

## 📦 Project Structure

```
SmartMCP/
├── main.py                  # Server entry point
├── config.yaml              # Configuration
├── requirements.txt         # Dependencies
├── example_database.py      # Sample data generator
├── test_setup.py           # Setup verification
├── db/adapter.py           # Database connector
├── nlp/query_parser.py     # NL to SQL parser
├── mcp/tools.py            # MCP tool definitions
└── utils/schema.py         # Schema utilities
```

---

## 🎓 Learn More

- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design deep dive
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete feature list
- **[README.md](README.md)** - Full documentation with examples

---

## 🔒 Safety Features

- ✅ Read-only by default
- ✅ Keyword blacklist (DROP, DELETE, etc.)
- ✅ SQL injection prevention
- ✅ Row limits (max 1000 per query)
- ✅ Environment variable for secrets

---

## 📝 License

MIT License - Free to use, modify, and distribute!

---

**Built with ❤️ and AI :P for the MCP community**
