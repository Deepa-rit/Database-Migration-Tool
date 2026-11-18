
import sqlite3
import os

def create_database():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect("data/ecommerce.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            total_amount REAL,
            order_status TEXT
        )
    """)

    cursor.executemany("""
        INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?)
    """, [
        (1, "Ananya", "ananya@gmail.com", "Chennai"),
        (2, "Karthik", "karthik@gmail.com", "Coimbatore"),
        (3, "Priya", "priya@gmail.com", "Madurai"),
        (4, "Rahul", "rahul@gmail.com", "Salem"),
        (5, "Divya", "divya@gmail.com", "Tiruvallur")
    ])

    cursor.executemany("""
        INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?)
    """, [
        (101, "Laptop", "Electronics", 55000, 10),
        (102, "Headphones", "Electronics", 1500, 25),
        (103, "Office Chair", "Furniture", 4500, 15),
        (104, "Notebook", "Stationery", 80, 100),
        (105, "Keyboard", "Electronics", 1200, 30)
    ])

    cursor.executemany("""
        INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1001, 1, 101, 1, 55000, "Delivered"),
        (1002, 2, 102, 2, 3000, "Shipped"),
        (1003, 3, 103, 1, 4500, "Pending"),
        (1004, 4, 104, 5, 400, "Delivered"),
        (1005, 5, 105, 2, 2400, "Processing")
    ])

    conn.commit()
    conn.close()

    print("E-commerce database created successfully!")
    print("Database: data/ecommerce.db")

if __name__ == "__main__":
    create_database()
