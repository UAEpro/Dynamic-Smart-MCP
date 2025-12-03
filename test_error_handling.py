"""
Error Handling Test Script
Demonstrates how the system handles queries for non-existent columns.
"""

import sqlite3
import sys

def create_test_database():
    """Create a simple customers database WITHOUT country column."""
    print("Creating test database WITHOUT country column...")
    print()
    
    conn = sqlite3.connect('customers_no_country.db')
    c = conn.cursor()
    
    # Drop if exists
    c.execute("DROP TABLE IF EXISTS customers")
    
    # Create customers table WITHOUT country column
    c.execute('''CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        registration_date TEXT
    )''')
    
    # Insert sample data
    customers = [
        (1, "John Doe", "john@example.com", "+1-555-0101", "2023-01-15"),
        (2, "Jane Smith", "jane@example.com", "+1-555-0102", "2023-02-20"),
        (3, "Ahmed Hassan", "ahmed@example.com", "+20-555-0103", "2023-03-10"),
        (4, "Maria Garcia", "maria@example.com", "+34-555-0104", "2023-04-05"),
        (5, "Li Wei", "li@example.com", "+86-555-0105", "2023-05-12"),
    ]
    
    c.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)
    
    conn.commit()
    conn.close()
    
    print("✅ Database created: customers_no_country.db")
    print()
    print("📋 Table structure:")
    print("   - id (INTEGER)")
    print("   - name (TEXT)")
    print("   - email (TEXT)")
    print("   - phone (TEXT)")
    print("   - registration_date (TEXT)")
    print()
    print("❌ MISSING: country column")
    print()


def test_column_exists():
    """Test query with existing column."""
    print("=" * 60)
    print("TEST 1: Query with EXISTING column (email)")
    print("=" * 60)
    print()
    print("Query: 'Show me customers with gmail emails'")
    print("SQL:   SELECT * FROM customers WHERE email LIKE '%gmail%'")
    print()
    
    conn = sqlite3.connect('customers_no_country.db')
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM customers WHERE email LIKE '%@gmail%'")
        results = c.fetchall()
        
        print("✅ SUCCESS!")
        print(f"   Found {len(results)} results")
        print()
        
    except sqlite3.Error as e:
        print(f"❌ ERROR: {e}")
        print()
    
    conn.close()


def test_column_missing():
    """Test query with non-existent column."""
    print("=" * 60)
    print("TEST 2: Query with MISSING column (country)")
    print("=" * 60)
    print()
    print("Query: 'أظهر لي جميع العملاء من الولايات المتحدة'")
    print("       (Show me all customers from USA)")
    print()
    print("SQL:   SELECT * FROM customers WHERE country = 'USA'")
    print()
    
    conn = sqlite3.connect('customers_no_country.db')
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM customers WHERE country = 'USA'")
        results = c.fetchall()
        
        print("✅ SUCCESS!")
        print(f"   Found {len(results)} results")
        print()
        
    except sqlite3.Error as e:
        print(f"❌ ERROR CAUGHT: {e}")
        print()
        print("📌 What happened:")
        print("   - SQL tried to use 'country' column")
        print("   - Database checked if column exists")
        print("   - Column not found → Error returned")
        print("   - No data was modified or corrupted")
        print()
        print("💡 How Smart MCP Server handles this:")
        print("   1. LLM sees schema (no 'country' column)")
        print("   2. Either:")
        print("      a) LLM returns error immediately, OR")
        print("      b) LLM generates SQL → Database catches error")
        print("   3. Error message returned to user")
        print("   4. User can try a different query")
        print()
        
    conn.close()


def show_available_columns():
    """Show what columns actually exist."""
    print("=" * 60)
    print("TEST 3: Check available columns")
    print("=" * 60)
    print()
    
    conn = sqlite3.connect('customers_no_country.db')
    c = conn.cursor()
    
    # Get table info
    c.execute("PRAGMA table_info(customers)")
    columns = c.fetchall()
    
    print("📋 Available columns in 'customers' table:")
    print()
    for col in columns:
        col_id, name, type_, not_null, default, pk = col
        pk_marker = " [PRIMARY KEY]" if pk else ""
        null_marker = " [NOT NULL]" if not_null else ""
        print(f"   ✅ {name} ({type_}){pk_marker}{null_marker}")
    
    print()
    print("❌ NOT available:")
    print("   - country")
    print("   - city")
    print("   - address")
    print("   - state")
    print()
    
    conn.close()


def show_correct_queries():
    """Show correct queries that work."""
    print("=" * 60)
    print("TEST 4: Working queries (no country filter)")
    print("=" * 60)
    print()
    
    conn = sqlite3.connect('customers_no_country.db')
    c = conn.cursor()
    
    print("✅ Query 1: Show all customers")
    print("   English: 'Show me all customers'")
    print("   Arabic:  'أرني جميع العملاء'")
    print("   SQL:     SELECT * FROM customers")
    print()
    c.execute("SELECT * FROM customers")
    results = c.fetchall()
    print(f"   Result: {len(results)} customers found")
    print()
    
    print("✅ Query 2: Filter by email domain")
    print("   English: 'Show me customers with gmail email'")
    print("   Arabic:  'أرني العملاء الذين لديهم بريد gmail'")
    print("   SQL:     SELECT * FROM customers WHERE email LIKE '%@gmail%'")
    print()
    c.execute("SELECT * FROM customers WHERE email LIKE '%@gmail%'")
    results = c.fetchall()
    print(f"   Result: {len(results)} customers found")
    print()
    
    print("✅ Query 3: Filter by registration date")
    print("   English: 'Show me customers registered in 2023'")
    print("   Arabic:  'أرني العملاء المسجلين في 2023'")
    print("   SQL:     SELECT * FROM customers WHERE registration_date LIKE '2023%'")
    print()
    c.execute("SELECT * FROM customers WHERE registration_date LIKE '2023%'")
    results = c.fetchall()
    print(f"   Result: {len(results)} customers found")
    print()
    
    conn.close()


def main():
    """Run all tests."""
    print()
    print("🧪 ERROR HANDLING TEST SUITE")
    print("=" * 60)
    print()
    print("This script demonstrates what happens when you query")
    print("a column that doesn't exist in your database.")
    print()
    # input("Press Enter to start tests...")
    print()
    
    # Create test database
    create_test_database()
    # input("Press Enter to continue...")
    print()
    
    # Test 1: Existing column
    test_column_exists()
    # input("Press Enter to continue...")
    print()
    
    # Test 2: Missing column
    test_column_missing()
    # input("Press Enter to continue...")
    print()
    
    # Test 3: Show available columns
    show_available_columns()
    # input("Press Enter to continue...")
    print()
    
    # Test 4: Show correct queries
    show_correct_queries()
    
    print("=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print()
    print("✅ What we learned:")
    print()
    print("1. When you query a missing column:")
    print("   - Database catches the error")
    print("   - No data is modified")
    print("   - Error message is returned")
    print("   - You can try again with correct columns")
    print()
    print("2. Smart MCP Server handles this by:")
    print("   - Including full schema in LLM prompt")
    print("   - LLM can detect missing columns")
    print("   - If SQL is generated, database catches it")
    print("   - Clear error messages returned")
    print()
    print("3. In your Arabic example:")
    print("   Query: 'أظهر لي جميع العملاء من الولايات المتحدة'")
    print("          (Show me all customers from USA)")
    print()
    print("   If 'country' column missing:")
    print("   → Error: 'Column country does not exist'")
    print("   → Lists available columns")
    print("   → You can query differently")
    print()
    print("4. Always safe:")
    print("   - Read-only mode protects data")
    print("   - Errors caught at database level")
    print("   - Helpful error messages")
    print()
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("   1. Update config.yaml:")
    print("      connection_string: 'sqlite:///customers_no_country.db'")
    print()
    print("   2. Run: python main.py")
    print()
    print("   3. Try the Arabic query:")
    print("      'أظهر لي جميع العملاء من الولايات المتحدة'")
    print()
    print("   4. See the error handling in action!")
    print()
    print("🎉 Your data is always safe!")
    print()


if __name__ == "__main__":
    main()

