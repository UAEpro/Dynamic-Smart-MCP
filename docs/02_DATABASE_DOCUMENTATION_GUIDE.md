# 📖 Database Documentation Guide

## Why Database Documentation Makes Your MCP Server Smarter

**TL;DR:** Adding context about your database **dramatically improves** query quality and accuracy!

---

## 🎯 **The Problem Without Documentation**

### Example: Vague Query

**User asks:** "Show me popular items"

**LLM without context:**
```sql
-- Guesses "popular" means recent or random
SELECT * FROM products ORDER BY id DESC LIMIT 10
```
❌ **Wrong!** This just shows newest products, not popular ones.

---

## ✅ **The Solution: Add Database Context**

### In `config.yaml`:

```yaml
database_context:
  description: "E-commerce database with customer orders"
  
  business_concepts:
    - "Popularity measured by total quantity sold"
    - "Best-selling products have highest order counts"
  
  tables:
    products:
      description: "Product catalog"
      notes: "Popularity = SUM(order_items.quantity) for each product"
```

**LLM with context:**
```sql
-- Understands "popular" = most sold
SELECT p.*, SUM(oi.quantity) as total_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id
ORDER BY total_sold DESC
LIMIT 10
```
✅ **Perfect!** Correct business logic applied.

---

## 📊 **Real-World Impact**

### Test Case: "Show me top customers"

#### ❌ **Without Documentation**

**Query:** "Show me top customers"

**Generated SQL:**
```sql
SELECT * FROM customers ORDER BY id DESC LIMIT 10
```

**Problems:**
- Orders by ID (arbitrary number)
- Doesn't consider purchase history
- "Top" interpretation is wrong

**Result:** Shows recently registered customers, not high-value customers ❌

---

#### ✅ **With Documentation**

**Config:**
```yaml
database_context:
  business_concepts:
    - "Top customers ranked by total order value"
    - "Customer lifetime value = SUM of all order totals"
```

**Generated SQL:**
```sql
SELECT c.*, SUM(o.total_amount) as lifetime_value
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id
ORDER BY lifetime_value DESC
LIMIT 10
```

**Result:** Shows actual high-value customers! ✅

---

## 🌍 **Multilingual Benefit**

### Arabic Query Example

**Without documentation:**
```
"أظهر لي الأنمي الشعبية" (Show me popular anime)
↓
SELECT * FROM anime ORDER BY id DESC LIMIT 10
❌ Just shows newest, not popular
```

**With documentation:**
```yaml
database_context:
  conventions:
    popularity: "Measured by rating (8.0+ is popular)"
```
```
"أظهر لي الأنمي الشعبية" (Show me popular anime)
↓
SELECT * FROM anime WHERE rating >= 8.0 ORDER BY rating DESC LIMIT 10
✅ Shows highly rated anime!
```

---

## 📝 **What to Document**

### 1. **Database Description**
```yaml
description: "What your database contains"
```

**Examples:**
- "Anime catalog with ratings and studio information"
- "E-commerce platform with customer orders"
- "Healthcare records system (HIPAA compliant)"
- "Social media platform with user interactions"

---

### 2. **Domain/Industry**
```yaml
domain: "Your industry/field"
```

**Why:** Helps LLM understand terminology and context

**Examples:**
- "Entertainment / Anime & Manga"
- "E-commerce / Online Retail"
- "Healthcare / Medical Records"
- "Finance / Banking & Transactions"

---

### 3. **Business Concepts**
```yaml
business_concepts:
  - "How your data relates"
  - "Key business rules"
  - "Important relationships"
```

**Examples for E-commerce:**
```yaml
business_concepts:
  - "Customers place orders for products"
  - "Orders contain multiple items"
  - "Top customers ranked by total spending"
  - "Revenue = SUM of completed order totals"
```

**Examples for Anime:**
```yaml
business_concepts:
  - "Anime produced by studios"
  - "Each anime has multiple genres"
  - "Rating scale 0-10 (8+ is excellent)"
  - "Episodes indicate series length"
```

---

### 4. **Table Descriptions**
```yaml
tables:
  table_name:
    description: "What this table represents"
    notes: "Important details"
```

**Example:**
```yaml
tables:
  anime:
    description: "Anime titles with metadata"
    notes: "rating is 0-10 scale, status shows if ongoing"
  
  studios:
    description: "Animation studios"
    notes: "Famous studios: Ghibli, Madhouse, KyoAni"
```

---

### 5. **Data Conventions**
```yaml
conventions:
  dates: "Format and meaning"
  currency: "What currency"
  status_values: "Possible values"
  null_handling: "What NULL means"
```

**Example:**
```yaml
conventions:
  dates: "YYYY-MM-DD format (ISO 8601)"
  currency: "USD dollars"
  status_values: "Lowercase: 'completed', 'pending', 'cancelled'"
  ratings: "Scale 0.0-10.0, 8.0+ is excellent"
  null_handling: "NULL age = unknown/not applicable"
```

---

### 6. **Common Queries**
```yaml
common_queries:
  - "Typical questions users ask"
  - "Common use cases"
```

**Example:**
```yaml
common_queries:
  - "Find top-rated anime"
  - "Show anime by studio"
  - "List ongoing series"
  - "Calculate average rating by genre"
```

---

## 🚀 **Quick Setup**

### Step 1: Choose Your Template

```bash
# We provide templates for:
database_docs/
  ├── e-commerce.yaml    # Online stores
  ├── anime.yaml         # Anime/entertainment
  ├── crm.yaml          # Customer management (coming soon)
  ├── healthcare.yaml   # Medical records (coming soon)
  └── finance.yaml      # Financial data (coming soon)
```

### Step 2: Copy Template to config.yaml

```yaml
# In config.yaml, add this section:
database_context:
  description: "..."
  domain: "..."
  business_concepts: [...]
  tables: {...}
  common_queries: [...]
  conventions: {...}
```

### Step 3: Customize for Your Schema

Edit the descriptions to match your actual tables and business logic.

### Step 4: Restart Server

```bash
python main.py
```

**Output:**
```
INFO: Database context loaded - queries will be more accurate
```

### Step 5: Test Improved Queries!

---

## 📈 **Before/After Comparison**

### Case Study: Anime Database

#### Query: "Show me highly rated action anime"

**Before (No Documentation):**
```sql
-- LLM guesses what "highly rated" means
SELECT * FROM anime WHERE genre = 'Action' LIMIT 10
```

**Issues:**
- Doesn't know what "highly rated" means
- Assumes genre is a column (it's actually a junction table!)
- No rating filter applied

**Result:** Random action anime, not necessarily highly rated ❌

---

**After (With Documentation):**
```yaml
database_context:
  conventions:
    ratings: "Scale 0-10, 8.0+ is highly rated"
  
  tables:
    anime_genres:
      notes: "Links anime to genres (many-to-many)"
  
  business_concepts:
    - "Genres stored in junction table anime_genres"
    - "High ratings = 8.0 or above"
```

```sql
-- LLM understands the structure and conventions
SELECT DISTINCT a.*
FROM anime a
JOIN anime_genres ag ON a.id = ag.anime_id
JOIN genres g ON ag.genre_id = g.id
WHERE g.name = 'Action' AND a.rating >= 8.0
ORDER BY a.rating DESC
LIMIT 10
```

**Result:** Perfectly filtered action anime with ratings 8.0+! ✅

---

## 🎯 **Best Practices**

### ✅ **DO:**

1. **Be Clear and Specific**
   ```yaml
   conventions:
     ratings: "0-10 scale, 8.0+ is excellent, 7.0-7.9 is good"
   ```

2. **Explain Relationships**
   ```yaml
   business_concepts:
     - "Products linked to orders via order_items junction table"
   ```

3. **Document Status Values**
   ```yaml
   tables:
     orders:
       notes: "status: 'pending', 'shipped', 'completed', 'cancelled'"
   ```

4. **Include Business Logic**
   ```yaml
   conventions:
     revenue: "SUM(quantity * unit_price) from order_items"
   ```

5. **Note Special Cases**
   ```yaml
   tables:
     products:
       notes: "stock_quantity 0 = out of stock, NULL = unlimited"
   ```

---

### ❌ **DON'T:**

1. **Don't Expose Sensitive Implementation Details**
   ```yaml
   # ❌ BAD:
   tables:
     users:
       notes: "Password hashed with bcrypt, salt stored in column..."
   ```

2. **Don't Over-Complicate Simple Concepts**
   ```yaml
   # ❌ BAD (too technical):
   conventions:
     dates: "ISO 8601 format with timezone offset in UTC±00:00..."
   
   # ✅ GOOD:
   conventions:
     dates: "YYYY-MM-DD format"
   ```

3. **Don't Document Internal Indexes**
   ```yaml
   # ❌ BAD:
   tables:
     customers:
       notes: "Has B-tree index on email column for performance..."
   ```

4. **Don't Include Security Details**
   ```yaml
   # ❌ BAD:
   description: "User database with admin privileges in role column..."
   ```

---

## 💡 **Pro Tips**

### Tip 1: Start Simple, Iterate

```yaml
# Version 1 (Minimal):
database_context:
  description: "E-commerce database"

# Version 2 (Better):
database_context:
  description: "E-commerce with orders and products"
  domain: "Online Retail"

# Version 3 (Best):
database_context:
  description: "E-commerce platform with customer orders"
  domain: "Online Retail"
  business_concepts:
    - "Customers place orders for products"
  tables:
    orders:
      description: "Purchase orders"
      notes: "Status: pending, shipped, completed"
```

---

### Tip 2: Test and Refine

```bash
# Try a query
"Show me top customers"

# Check the SQL generated
# If wrong, add more context

# Retry
"Show me top customers"

# Check again - should be better!
```

---

### Tip 3: Focus on Common Queries

Document the 80% of queries users will actually ask:

```yaml
common_queries:
  - "Find top customers"          # Most common
  - "Show popular products"       # Very common
  - "Calculate monthly revenue"   # Common
  # Don't document rare edge cases
```

---

### Tip 4: Use Your Domain Language

```yaml
# For Anime database:
conventions:
  popularity: "Measured by rating and episode count"
  
# For E-commerce:
conventions:
  popularity: "Measured by quantity sold and revenue"
  
# For Social Media:
conventions:
  popularity: "Measured by likes, shares, and comments"
```

---

## 🧪 **Testing Impact**

### Test Script:

```python
# test_documentation_impact.py

queries = [
    "Show me top customers",
    "Find popular products",
    "List completed orders",
    "Calculate total revenue"
]

print("WITHOUT documentation:")
for q in queries:
    result = query_database(q)
    print(f"  {q} → {result['sql']}")

# Add documentation to config.yaml

print("\nWITH documentation:")
for q in queries:
    result = query_database(q)
    print(f"  {q} → {result['sql']}")
```

**Expected:** SQL quality improves dramatically!

---

## 📚 **Examples by Database Type**

### E-commerce
```yaml
database_context:
  description: "Online store with orders and inventory"
  domain: "E-commerce"
  conventions:
    revenue: "SUM of completed order totals"
    top_customers: "Ranked by total spending"
```

### Anime
```yaml
database_context:
  description: "Anime catalog with ratings and studios"
  domain: "Entertainment"
  conventions:
    ratings: "0-10 scale, 8+ is excellent"
    popularity: "Based on rating and episode count"
```

### Healthcare
```yaml
database_context:
  description: "Patient medical records (HIPAA compliant)"
  domain: "Healthcare"
  conventions:
    dates: "All timestamps in UTC"
    privacy: "PHI fields require audit logging"
```

### Social Media
```yaml
database_context:
  description: "User profiles, posts, and interactions"
  domain: "Social Media"
  conventions:
    engagement: "likes + comments + shares"
    popularity: "Ranked by engagement rate"
```

---

## ✅ **Summary**

### Without Documentation:
- ❌ LLM guesses meanings
- ❌ Wrong business logic
- ❌ Poor query quality
- ❌ More user frustration

### With Documentation:
- ✅ LLM understands your domain
- ✅ Correct business logic
- ✅ High-quality queries
- ✅ Happy users!

---

## 🚀 **Get Started**

1. **Copy a template** from `database_docs/`
2. **Customize** for your schema
3. **Add to** `config.yaml`
4. **Restart** server
5. **Test** queries - watch them improve!

---

**Database documentation is the secret to amazing NL2SQL! 🎯**

See:
- `database_docs/README.md` - Overview
- `database_docs/anime.yaml` - Anime template
- `database_docs/e-commerce.yaml` - E-commerce template
- `config.yaml` - Your configuration file

