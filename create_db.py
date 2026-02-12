import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# Users table (Admin, Vendor, User)
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    status TEXT
)
""")

# Services / Products
c.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    name TEXT,
    category TEXT,
    price REAL,
    description TEXT,
    status TEXT
)
""")

# Orders
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    total_amount REAL,
    status TEXT
)
""")

# Order Items
c.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    service_id INTEGER,
    quantity INTEGER
)
""")

# Requests (from Excel)
c.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    description TEXT,
    status TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service_id INTEGER,
    quantity INTEGER
)
""")

# Orders table
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    total_amount REAL,
    status TEXT
)
""")

conn.commit()
conn.close()

print("Database Created!")
