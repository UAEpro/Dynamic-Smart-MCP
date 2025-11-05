# 📖 Database Documentation System

This directory contains documentation templates and examples for different database types.

---

## 🎯 **Why Document Your Database?**

Adding context about your database **dramatically improves** query quality:

### **Without Documentation:**
```
User: "Show me popular anime"
LLM: *Guesses* → SELECT * FROM anime ORDER BY id DESC
❌ Wrong ordering, unclear what "popular" means
```

### **With Documentation:**
```
Database Context: "popularity measured by rating and view count"

User: "Show me popular anime"
LLM: *Understands* → SELECT * FROM anime ORDER BY rating DESC, episodes DESC
✅ Correct interpretation of "popular"
```

---

## ✅ **Benefits**

1. **Better Query Understanding** - LLM knows your domain
2. **Accurate Terminology** - Understands business terms
3. **Proper Relationships** - Knows how tables connect
4. **Smart Defaults** - Makes better assumptions
5. **Fewer Errors** - Reduces misinterpretations
6. **Faster Results** - Less trial and error

---

## 📝 **How to Document**

### **In `config.yaml`:**

```yaml
database_context:
  description: "What your database contains"
  domain: "Your industry/domain"
  business_concepts: [...]
  tables: {...}
  common_queries: [...]
  conventions: {...}
```

See examples in this directory for your database type!

---

## 📚 **Available Templates**

- `e-commerce.yaml` - Online stores, products, orders
- `anime.yaml` - Anime/manga database
- `crm.yaml` - Customer relationship management
- `healthcare.yaml` - Medical records (HIPAA-compliant)
- `finance.yaml` - Financial transactions
- `education.yaml` - Schools, students, courses
- `social-media.yaml` - Users, posts, interactions

---

## 🚀 **Quick Start**

1. Copy the template for your database type
2. Paste into your `config.yaml` under `database_context:`
3. Customize descriptions for your specific schema
4. Restart the server
5. Try natural language queries - they'll work much better!

---

## 💡 **Best Practices**

### ✅ **DO:**
- Describe business concepts clearly
- Explain table relationships
- Note data conventions
- List common use cases
- Mention special statuses/values

### ❌ **DON'T:**
- Expose sensitive security details
- Document internal implementation
- Include credentials or secrets
- Over-complicate simple concepts

---

## 📖 **Example: Anime Database**

```yaml
database_context:
  description: "Anime catalog with ratings, genres, and studio information"
  domain: "Entertainment / Anime"
  
  business_concepts:
    - "Anime are produced by studios"
    - "Each anime can have multiple genres"
    - "Ratings indicate popularity (higher is better)"
    - "Episodes count the series length"
  
  tables:
    anime:
      description: "Anime titles with metadata"
      notes: "Rating is 0-10 scale, status shows if series is ongoing"
    
    studios:
      description: "Animation studios that produce anime"
      
    genres:
      description: "Genre classifications (Action, Romance, etc.)"
```

**Result:** Users can ask "Show me highly rated action anime" and the LLM will:
- Know "highly rated" means `rating > 8.0`
- Understand "action" is a genre requiring a JOIN
- Generate perfect SQL automatically

---

## 🎯 **Impact on Query Quality**

### **Before Documentation:**
```
Query: "Show me top customers"
SQL: SELECT * FROM customers ORDER BY id DESC LIMIT 10
❌ Orders by ID (arbitrary), not by value
```

### **After Documentation:**
```yaml
business_concepts:
  - "Top customers are those with highest total order value"
  
tables:
  customers:
    notes: "Customer value measured by total_spent or order count"
```

```
Query: "Show me top customers"
SQL: SELECT c.*, SUM(o.total_amount) as total_spent 
     FROM customers c 
     JOIN orders o ON c.id = o.customer_id 
     GROUP BY c.id 
     ORDER BY total_spent DESC 
     LIMIT 10
✅ Correct business logic applied!
```

---

**Documentation is the secret to high-quality NL2SQL! 🎯**

