# 🔒 Production Security Guide

Complete guide to securing your Smart MCP Server for production deployment.

---

## ⚠️ **Critical Security Principle**

**NEVER expose database internals to end users!**

This includes:
- ❌ Table names
- ❌ Column names  
- ❌ SQL queries
- ❌ Database structure
- ❌ Error details
- ❌ Schema information

---

## 🛡️ **Production vs Development Mode**

### **Development Mode** (hide_database_details: false)
```json
{
  "success": false,
  "error": "no such column: country",
  "sql": "SELECT * FROM customers WHERE country = 'USA'",
  "available_columns": ["id", "name", "email"]
}
```
**🔴 DANGEROUS - Shows database structure!**

### **Production Mode** (hide_database_details: true)
```json
{
  "success": false,
  "message": "Sorry, I couldn't find the information you requested. Please try asking in a different way."
}
```
**🟢 SAFE - Generic, user-friendly message**

---

## ⚙️ **Configuration**

### `config.yaml` - Security Section

```yaml
security:
  # Hide database structure from end users (PRODUCTION: true)
  hide_database_details: true
  
  # Show SQL queries in responses (PRODUCTION: false)
  expose_sql: false
  
  # Show column names in errors (PRODUCTION: false)
  expose_column_names: false
  
  # Show table names in errors (PRODUCTION: false)
  expose_table_names: false
  
  # Log detailed errors server-side (always: true)
  log_detailed_errors: true
```

### **Recommended Settings**

#### **Production (Customer-Facing)**
```yaml
security:
  hide_database_details: true    # ✅ MUST BE TRUE
  expose_sql: false              # ✅ MUST BE FALSE
  expose_column_names: false     # ✅ MUST BE FALSE
  expose_table_names: false      # ✅ MUST BE FALSE
  log_detailed_errors: true      # ✅ Keep for debugging
```

#### **Development (Internal Testing)**
```yaml
security:
  hide_database_details: false   # See all details
  expose_sql: true               # See generated SQL
  expose_column_names: true      # See column info
  expose_table_names: true       # See table info
  log_detailed_errors: true      # Full logging
```

---

## 📊 **Response Examples**

### Scenario: User asks for non-existent column

**User Query (Arabic):**
```
"أظهر لي جميع العملاء من الولايات المتحدة"
(Show me all customers from USA)
```

**Problem:** No `country` column exists

---

### ❌ **INSECURE Response** (Development Mode)

```json
{
  "success": false,
  "error": "no such column: country",
  "sql": "SELECT * FROM customers WHERE country = 'USA' LIMIT 1000",
  "available_columns": ["id", "name", "email", "phone", "registration_date"],
  "table": "customers",
  "natural_language": "أظهر لي جميع العملاء من الولايات المتحدة"
}
```

**🔴 Security Issues:**
- Reveals table name (`customers`)
- Shows all column names
- Exposes SQL query
- Reveals database structure

**🚨 Attackers can learn:**
- Your schema design
- Column naming conventions
- What data you store
- How to craft SQL injection attempts

---

### ✅ **SECURE Response** (Production Mode)

```json
{
  "success": false,
  "message": "عذراً، لم أتمكن من العثور على البيانات المطلوبة. يرجى المحاولة بسؤال مختلف أو التحقق من المعلومات المدخلة.",
  "natural_language": "أظهر لي جميع العملاء من الولايات المتحدة"
}
```

**🟢 Security Benefits:**
- No database details exposed
- Generic, helpful message
- Maintains user experience
- Language-appropriate response (Arabic)

**Server-Side Log (Only visible to admins):**
```
ERROR [2025-01-15 10:23:45] Query error: {
  "error": "no such column: country",
  "sql": "SELECT * FROM customers WHERE country = 'USA'",
  "table": "customers"
}
```
✅ **Detailed logs for debugging, hidden from users**

---

## 🌍 **Multilingual Error Messages**

The system automatically detects language and returns appropriate messages:

### **Arabic**
```json
{
  "message": "عذراً، لم أتمكن من العثور على البيانات المطلوبة. يرجى المحاولة بسؤال مختلف."
}
```

### **English**
```json
{
  "message": "Sorry, I couldn't find the information you requested. Please try asking in a different way."
}
```

### **Spanish**
```json
{
  "message": "Lo siento, no pude encontrar los datos solicitados. Por favor, intente con una pregunta diferente."
}
```

### **French**
```json
{
  "message": "Désolé, je n'ai pas pu trouver les données demandées. Veuillez essayer avec une question différente."
}
```

### **Chinese**
```json
{
  "message": "抱歉，无法找到您请求的数据。请尝试不同的问题。"
}
```

---

## 🎯 **Success Responses**

### ❌ **INSECURE** (Development Mode)

```json
{
  "success": true,
  "sql": "SELECT id, name, email FROM customers LIMIT 10",
  "columns": ["id", "name", "email"],
  "rows": [...],
  "row_count": 10
}
```
**🔴 Exposes:** SQL query, column names, table structure

---

### ✅ **SECURE** (Production Mode)

```json
{
  "success": true,
  "message": "Found 10 result(s).",
  "data": [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
  ],
  "count": 10
}
```
**🟢 Clean:** No SQL, no schema details, just data

---

## 🔐 **Schema Protection**

### Development Mode (`hide_database_details: false`)

```bash
# Tool: get_database_schema()
```

**Response:**
```json
{
  "database_type": "sqlite",
  "tables": {
    "customers": {
      "columns": [
        {"name": "id", "type": "INTEGER"},
        {"name": "name", "type": "TEXT"},
        {"name": "email", "type": "TEXT"}
      ],
      "row_count": 1000
    }
  }
}
```
**🔴 Full schema exposed!**

---

### Production Mode (`hide_database_details: true`)

```bash
# Tool: get_database_schema()
```

**Response:**
```json
{
  "success": false,
  "message": "Schema information is not available."
}
```
**🟢 Schema hidden from users**

**Server Log:**
```
WARNING: Schema access attempted by user (blocked in production mode)
```

---

## 📋 **Security Checklist**

### **Before Going to Production**

- [ ] Set `hide_database_details: true`
- [ ] Set `expose_sql: false`
- [ ] Set `expose_column_names: false`
- [ ] Set `expose_table_names: false`
- [ ] Enable `log_detailed_errors: true`
- [ ] Test with invalid queries
- [ ] Verify no SQL in responses
- [ ] Check error messages are generic
- [ ] Review server logs configuration
- [ ] Set up secure log storage
- [ ] Enable HTTPS/TLS
- [ ] Use strong API keys
- [ ] Implement rate limiting
- [ ] Set up monitoring/alerting

---

## 🧪 **Testing Security**

### Test Script

```python
# test_production_security.py

def test_invalid_column():
    """Test that column names are not exposed."""
    query = "Show me customers from France"
    
    # Should NOT contain:
    assert "country" not in response
    assert "customers" not in response
    assert "SELECT" not in response
    assert "column" not in response.lower()
    
    # Should contain:
    assert response["success"] == False
    assert "message" in response
    assert "couldn't find" in response["message"].lower()

def test_valid_query():
    """Test that SQL is not exposed in success."""
    query = "Show me all customers"
    
    # Should NOT contain:
    assert "sql" not in response
    assert "SELECT" not in response
    assert "FROM" not in response
    
    # Should contain:
    assert response["success"] == True
    assert "data" in response
    assert "count" in response
```

---

## 🚨 **Common Security Mistakes**

### ❌ **DON'T:**

1. **Expose SQL queries**
   ```json
   {"sql": "SELECT * FROM users WHERE..."}  // ❌
   ```

2. **Show column names**
   ```json
   {"available_columns": ["password", "ssn"]}  // ❌
   ```

3. **Reveal table names**
   ```json
   {"error": "Table 'admin_users' not found"}  // ❌
   ```

4. **Display database errors**
   ```json
   {"error": "Syntax error near 'WHERE'"}  // ❌
   ```

5. **Return full schema**
   ```json
   {"schema": {"tables": [...], "relationships": [...]}}  // ❌
   ```

---

### ✅ **DO:**

1. **Generic error messages**
   ```json
   {"message": "Sorry, couldn't find the data."}  // ✅
   ```

2. **Log details server-side**
   ```
   Server log: "SQL error: no such column: country"  // ✅
   ```

3. **Return data only**
   ```json
   {"data": [...], "count": 10}  // ✅
   ```

4. **Use status codes**
   ```json
   {"success": true/false}  // ✅
   ```

5. **Language-appropriate messages**
   ```json
   {"message": "عذراً، لم أتمكن..."}  // ✅ (Arabic)
   ```

---

## 🔍 **What Gets Logged**

### Server-Side Logs (Visible to Admins Only)

```
2025-01-15 10:23:45 | ERROR | Query failed
  User query: "أظهر لي جميع العملاء من الولايات المتحدة"
  Generated SQL: SELECT * FROM customers WHERE country = 'USA'
  Error: no such column: country
  Table: customers
  Available columns: id, name, email, phone
  User IP: 192.168.1.100
  Session ID: abc123

2025-01-15 10:24:10 | INFO | Query successful
  User query: "Show me all customers"
  Generated SQL: SELECT * FROM customers LIMIT 1000
  Rows returned: 150
  Execution time: 45ms
  User IP: 192.168.1.100
```

**✅ Full details in logs for debugging**
**✅ Never sent to end users**

---

## 🛠️ **Implementation Details**

### How It Works

```
User Query (Arabic)
      ↓
Query Parser (with schema)
      ↓
SQL Generated
      ↓
Database Execution
      ↓
Result/Error
      ↓
ResponseSanitizer ← 🔒 Security Layer
      ↓
┌─────────────────────┬──────────────────────┐
│  Production Mode    │  Development Mode    │
├─────────────────────┼──────────────────────┤
│  Generic message    │  Detailed error      │
│  No SQL shown       │  SQL query shown     │
│  No schema details  │  Schema info shown   │
│  Clean data only    │  All technical info  │
└─────────────────────┴──────────────────────┘
      ↓
User receives safe response
      ↓
Detailed error logged server-side
```

---

## 📝 **Best Practices**

### 1. **Always Use Production Mode for Customer-Facing Apps**

```yaml
# config.yaml
security:
  hide_database_details: true  # ✅ Always for production
```

### 2. **Keep Development Mode for Internal Tools**

```yaml
# config.dev.yaml (separate config)
security:
  hide_database_details: false  # Only for developers
```

### 3. **Monitor Logs, Not User Responses**

```python
# Admins review logs for issues
# Users see clean, generic messages
```

### 4. **Use Different Configs per Environment**

```bash
# Development
python main.py --config config.dev.yaml

# Production
python main.py --config config.prod.yaml
```

### 5. **Regular Security Audits**

- Review response payloads
- Check for data leaks
- Test with invalid queries
- Verify logs are secure

---

## 🎯 **Summary**

### **Your Arabic Query Example**

**Query:** `"أظهر لي جميع العملاء من الولايات المتحدة"`

**If `country` column doesn't exist:**

#### ❌ **Insecure (Development):**
```json
{
  "error": "no such column: country",
  "sql": "SELECT * FROM customers WHERE country = 'USA'",
  "columns": ["id", "name", "email"]
}
```

#### ✅ **Secure (Production):**
```json
{
  "success": false,
  "message": "عذراً، لم أتمكن من العثور على البيانات المطلوبة. يرجى المحاولة بسؤال مختلف."
}
```

---

## 🚀 **Quick Setup**

### For Production:

```yaml
# config.yaml
security:
  hide_database_details: true
  expose_sql: false
  expose_column_names: false
  expose_table_names: false
  log_detailed_errors: true
```

### Test it:

```bash
# Run server
python main.py

# Try invalid query
"أظهر لي جميع العملاء من الولايات المتحدة"

# Should get generic error, no DB details!
```

---

## ✅ **Benefits**

1. **🔒 Security:** Database structure hidden
2. **👤 UX:** Clean, user-friendly messages
3. **🌍 Multilingual:** Errors in user's language
4. **📊 Monitoring:** Full details in server logs
5. **⚡ Performance:** No difference in speed
6. **🛡️ Protection:** Against SQL injection recon
7. **✨ Professional:** Production-ready responses

---

**Your Smart MCP Server is now production-secure! 🔐**

---

## 📚 **Related Files**

- `utils/security.py` - ResponseSanitizer implementation
- `config.yaml` - Security configuration
- `mcp/tools.py` - Sanitizer integration
- `smart-mcp.log` - Server-side detailed logs

---

**Remember: Never expose database internals in production! 🛡️**

