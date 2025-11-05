"""
Example Database Creator
Run this script to create a sample SQLite database for testing Smart MCP Server.
"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_sample_database(db_path: str = "example.db"):
    """Create a sample e-commerce database with customers, products, and orders."""
    
    print(f"Creating sample database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Drop existing tables
    c.execute("DROP TABLE IF EXISTS order_items")
    c.execute("DROP TABLE IF EXISTS orders")
    c.execute("DROP TABLE IF EXISTS products")
    c.execute("DROP TABLE IF EXISTS customers")
    c.execute("DROP TABLE IF EXISTS categories")
    
    # Create categories table
    c.execute('''CREATE TABLE categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    )''')
    
    # Create customers table
    c.execute('''CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        country TEXT,
        registration_date TEXT,
        is_active INTEGER DEFAULT 1
    )''')
    
    # Create products table
    c.execute('''CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category_id INTEGER,
        price REAL NOT NULL,
        stock_quantity INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )''')
    
    # Create orders table
    c.execute('''CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )''')
    
    # Create order_items table
    c.execute('''CREATE TABLE order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    
    # Insert categories
    categories = [
        (1, "Electronics", "Electronic devices and gadgets"),
        (2, "Clothing", "Apparel and fashion items"),
        (3, "Books", "Physical and digital books"),
        (4, "Home & Garden", "Home improvement and gardening"),
        (5, "Sports", "Sports equipment and accessories")
    ]
    c.executemany("INSERT INTO categories VALUES (?, ?, ?)", categories)
    
    # Insert customers
    customers = [
        (1, "John Doe", "john.doe@example.com", "USA", "2023-01-15", 1),
        (2, "Jane Smith", "jane.smith@example.com", "UK", "2023-02-20", 1),
        (3, "Bob Johnson", "bob.johnson@example.com", "Canada", "2023-03-10", 1),
        (4, "Alice Williams", "alice.w@example.com", "USA", "2023-04-05", 1),
        (5, "Charlie Brown", "charlie.b@example.com", "Australia", "2023-05-12", 0),
        (6, "Diana Prince", "diana.p@example.com", "UK", "2023-06-18", 1),
        (7, "Eve Davis", "eve.davis@example.com", "USA", "2023-07-22", 1),
        (8, "Frank Miller", "frank.m@example.com", "Germany", "2023-08-30", 0),
        (9, "Grace Lee", "grace.lee@example.com", "South Korea", "2023-09-14", 1),
        (10, "Henry Zhang", "henry.z@example.com", "China", "2023-10-25", 1)
    ]
    c.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", customers)
    
    # Insert products
    products = [
        (1, "Laptop Pro 15", 1, 1299.99, 50),
        (2, "Wireless Mouse", 1, 29.99, 200),
        (3, "USB-C Cable", 1, 12.99, 500),
        (4, "Cotton T-Shirt", 2, 19.99, 300),
        (5, "Jeans", 2, 49.99, 150),
        (6, "Python Programming Book", 3, 39.99, 80),
        (7, "Cookbook Collection", 3, 29.99, 60),
        (8, "Garden Tools Set", 4, 89.99, 40),
        (9, "LED Desk Lamp", 4, 34.99, 120),
        (10, "Yoga Mat", 5, 24.99, 100),
        (11, "Tennis Racket", 5, 79.99, 45),
        (12, "Smartphone X", 1, 899.99, 75),
        (13, "Headphones Pro", 1, 199.99, 90),
        (14, "Winter Jacket", 2, 129.99, 60),
        (15, "Running Shoes", 5, 89.99, 80)
    ]
    c.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)
    
    # Insert orders with realistic dates
    base_date = datetime(2023, 1, 1)
    order_id = 1
    order_item_id = 1
    
    for customer_id in [1, 1, 2, 3, 4, 1, 6, 7, 9, 10, 2, 3, 6, 7, 9]:
        # Random date in 2023
        days_offset = random.randint(0, 300)
        order_date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        # Random products and quantities
        num_items = random.randint(1, 4)
        product_ids = random.sample(range(1, 16), num_items)
        
        total_amount = 0
        order_items = []
        
        for product_id in product_ids:
            quantity = random.randint(1, 3)
            # Get product price
            c.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            unit_price = c.fetchone()[0]
            total_amount += unit_price * quantity
            
            order_items.append((order_item_id, order_id, product_id, quantity, unit_price))
            order_item_id += 1
        
        status = random.choice(["completed", "completed", "completed", "pending", "shipped"])
        
        c.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", 
                 (order_id, customer_id, order_date, total_amount, status))
        
        c.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", order_items)
        
        order_id += 1
    
    conn.commit()
    conn.close()
    
    print("✅ Sample database created successfully!")
    print(f"   - 5 categories")
    print(f"   - 10 customers")
    print(f"   - 15 products")
    print(f"   - {order_id - 1} orders")
    print(f"\nYou can now test queries like:")
    print('   - "Show me all customers"')
    print('   - "What are the top 5 most expensive products?"')
    print('   - "Show me orders with customer names"')
    print('   - "What is the total revenue by category?"')


if __name__ == "__main__":
    create_sample_database()

