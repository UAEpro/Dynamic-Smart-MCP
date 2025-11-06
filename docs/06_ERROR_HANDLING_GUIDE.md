# 🛡️ Error Handling Guide

Understanding how Smart MCP Server handles invalid queries and missing columns.

---

## ❓ **What If You Query a Non-Existent Column?**

### Scenario:
**You ask:** "أظهر لي جميع العملاء من الولايات المتحدة"  
(Show me all customers from USA)

**But:** Your `customers` table doesn't have a `country` column!

---

## 🔄 **What Happens: 3 Possible Outcomes**

### **Outcome 1: LLM Detects the Issue (Best Case)**

The LLM reviews the schema and realizes there's no `country` column.

**LLM Response:**
```
ERROR: The 'customers' table does not have a 'country' column. 
Available columns are: id, name, email, registration_date
```

**Your Result:**
```json
{
  "success": false,
  "error": "Cannot filter by country - column does not exist in customers table",
  "natural_language": "أظهر لي جميع العملاء من الولايات المتحدة"
}
```

✅ **Clean error message** - No SQL executed

---

### **Outcome 2: SQL Generated, Database Catches Error (Common)**

The LLM generates SQL with the non-existent column, but the database rejects it.

**Generated SQL:**
```sql
SELECT * FROM customers WHERE country = 'USA' LIMIT 1000
```

**Database Error:**
```
SQLAlchemyError: no such column: country
```

**Your Result:**
```json
{
  "success": false,
  "error": "no such column: country",
  "sql": "SELECT * FROM customers WHERE country = 'USA' LIMIT 1000",
  "natural_language": "أظهر لي جميع العملاء من الولايات المتحدة"
}
```

✅ **Safe** - Error caught before any damage
✅ **Informative** - Shows the SQL that failed

---

### **Outcome 3: LLM Suggests Alternatives (Smart)**

Advanced LLMs (like GPT-4) might suggest workarounds.

**LLM Response:**
```sql
-- Note: 'country' column not found in customers table
-- Available columns: id, name, email, registration_date
-- Cannot fulfill this query without country information
SELECT 'ERROR: country column does not exist' as message
```

**Your Result:**
```json
{
  "success": true,
  "rows": [
    {"message": "ERROR: country column does not exist"}
  ]
}
```

---

## 🔍 **How Schema Context Helps**

The system includes **full schema information** in every LLM prompt:

```
DATABASE SCHEMA:
================
TABLE: customers
Rows: ~100
----------------------------------------
COLUMNS:
  - id: INTEGER [PRIMARY KEY]
  - name: TEXT [NOT NULL]
  - email: TEXT
  - registration_date: TEXT

SAMPLE DATA:
  Row 1: id=1, name=John Doe, email=john@example.com
  Row 2: id=2, name=Jane Smith, email=jane@example.com
```

**Because of this:**
- ✅ LLM knows exactly what columns exist
- ✅ LLM can detect missing columns
- ✅ Better error messages
- ✅ Smarter fallback behavior

---

## 💡 **Real-World Examples**

### Example 1: Missing Column

**Question:** "Show me customers from France"
**Problem:** No `country` column

**LLM sees:**
```
Table: customers
Columns: id, name, email, registration_date
(No country column!)
```

**LLM Response:**
```
ERROR: Cannot filter by country. The customers table does not have a country column.
Available columns: id, name, email, registration_date
```

---

### Example 2: Similar Column Name

**Question:** "Show me customers by location"
**Reality:** Column is named `city` not `location`

**LLM sees:**
```
Columns: id, name, email, city, registration_date
```

**LLM Response (Smart):**
```sql
-- Assuming 'location' refers to 'city' column
SELECT * FROM customers WHERE city = 'Paris' LIMIT 1000
```

Or:
```
ERROR: No 'location' column found. Did you mean 'city'?
```

---

### Example 3: Wrong Table

**Question:** "Show me products from category Electronics"
**Problem:** You're connected to a customers database (no products table)

**LLM sees:**
```
Available tables: customers, orders
(No products table!)
```

**LLM Response:**
```
ERROR: No 'products' table found in database.
Available tables: customers, orders
```

---

## 🛡️ **Safety Features**

### 1. **Schema Validation**
Before generating SQL, the LLM reviews:
- ✅ Table names
- ✅ Column names
- ✅ Data types
- ✅ Relationships

### 2. **Error Catching**
Multiple safety layers:
```
Layer 1: LLM validation (checks schema)
   ↓
Layer 2: SQL syntax validation
   ↓
Layer 3: Database execution
   ↓
Layer 4: Result validation
```

### 3. **No Data Corruption**
- ❌ **Never** executes dangerous queries
- ❌ **Never** modifies data (read-only by default)
- ✅ **Always** catches errors safely
- ✅ **Always** returns error details

---

## 🔧 **How to Improve Results**

### Tip 1: Use Specific Column Names

❌ **Vague:**
```
"Show me customers by location"
```

✅ **Specific:**
```
"Show me all customers" (then check what columns exist)
```

### Tip 2: Check Schema First

**Before asking complex queries:**
```
English: "What columns does the customers table have?"
Arabic: "ما هي الأعمدة في جدول العملاء؟"
```

**Or use the tool:**
```
get_database_schema()
```

### Tip 3: Start Simple

**First query:**
```
"Show me all customers"
→ See what data exists
```

**Then refine:**
```
"Show me customers with email containing gmail"
→ Use columns you know exist
```

---

## 📊 **Common Error Scenarios**

### Scenario 1: Typo in Column Name

**Question:** "Show customers with emayl containing gmail"
(Typo: `emayl` instead of `email`)

**Result:**
```json
{
  "success": false,
  "error": "no such column: emayl",
  "suggestion": "Did you mean: email?"
}
```

---

### Scenario 2: Wrong Data Type

**Question:** "Show customers where id = 'five'"
(String instead of integer)

**Result:**
- SQLite: Might work (auto-converts)
- PostgreSQL: Type error
- LLM: Usually fixes this automatically to `id = 5`

---

### Scenario 3: Missing Relationship

**Question:** "Show customers with their orders"
**Problem:** No foreign key relationship defined

**LLM might:**
1. Try to guess the join: `customers.id = orders.customer_id`
2. Return error: "No relationship found between tables"
3. Ask for clarification

---

## 🎯 **Best Practices**

### 1. **Explore Before Querying**

```bash
# First, see what's in the database
"Show me all table names"
"What columns does the customers table have?"
"Show me sample data from customers"
```

### 2. **Use Schema Tool**

```python
# Get full schema
get_database_schema()

# Returns:
{
  "tables": {
    "customers": {
      "columns": [...],
      "sample_data": [...]
    }
  }
}
```

### 3. **Iterative Refinement**

```
Query 1: "Show me all customers" 
         → See what columns exist

Query 2: "Show me customers with @gmail.com emails"
         → Use column you know exists

Query 3: "Show me the top 10 customers by registration date"
         → More complex, but safe
```

---

## 🔄 **Handling Arabic Queries with Missing Columns**

### Your Specific Example:

**Arabic Query:**
```
"أظهر لي جميع العملاء من الولايات المتحدة"
(Show me all customers from USA)
```

**If `country` column exists:**
```json
{
  "success": true,
  "sql": "SELECT * FROM customers WHERE country = 'USA' LIMIT 1000",
  "rows": [...]
}
```

**If `country` column doesn't exist:**
```json
{
  "success": false,
  "error": "Column 'country' does not exist in table 'customers'",
  "available_columns": ["id", "name", "email", "registration_date"],
  "suggestion": "Try: 'أظهر لي جميع العملاء' (Show me all customers)"
}
```

---

## 🚀 **Improved Error Handling**

The system provides helpful error messages in multiple languages:

### English Error:
```
"Column 'country' not found. Available columns: id, name, email"
```

### Arabic-Friendly Error:
```json
{
  "success": false,
  "error": "Column 'country' not found in 'customers' table",
  "error_ar": "العمود 'country' غير موجود في جدول 'customers'",
  "available_columns": ["id", "name", "email", "registration_date"],
  "suggestion": "Try querying: 'أظهر لي جميع العملاء' (Show all customers first)"
}
```

---

## 📝 **Testing Error Handling**

Try these queries to see error handling:

### Test 1: Missing Column
```bash
# English
"Show me customers from France"

# Arabic  
"أظهر لي العملاء من فرنسا"

# Expected: Error about missing 'country' column
```

### Test 2: Wrong Table
```bash
# English
"Show me all products"

# Arabic
"أظهر لي جميع المنتجات"

# Expected: Error about missing 'products' table
```

### Test 3: Invalid Filter
```bash
# English
"Show me customers where status is active"

# Arabic
"أظهر لي العملاء حيث الحالة نشطة"

# Expected: Error about missing 'status' column
```

---

## ✅ **Summary**

### What Happens When You Query Non-Existent Columns:

1. **LLM Checks Schema** ✅
   - Sees available columns
   - Detects missing column
   - May return error immediately

2. **Or SQL Gets Generated** 
   - LLM generates query anyway
   - Database catches the error
   - Error returned to user

3. **No Data Damage** 🛡️
   - Read-only mode protects data
   - Errors are caught safely
   - Full error details returned

4. **Helpful Error Messages** 💡
   - Shows what went wrong
   - Lists available columns
   - Suggests alternatives

### Your Arabic Query Example:

**"أظهر لي جميع العملاء من الولايات المتحدة"**

**If `country` missing:**
- ✅ Error caught gracefully
- ✅ Message explains the issue
- ✅ Lists available columns
- ✅ No data corruption
- ✅ You can try a different query

**The system is safe and robust!** 🎉

---

## 🎓 **Pro Tips**

1. **Always start with:** "Show me all [table]" to see what's available
2. **Use schema tool** before complex queries
3. **Read error messages** - they're helpful!
4. **Iterate** - start simple, add complexity
5. **LLMs are smart** - they often suggest fixes

---

**Your data is always safe, even with wrong queries! 🛡️**

