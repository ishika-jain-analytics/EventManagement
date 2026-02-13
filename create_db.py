import sqlite3
import os

def create_database():
    db_path = 'database.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Vendors table
    cursor.execute('''
        CREATE TABLE Vendors (
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            category TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Services table
    cursor.execute('''
        CREATE TABLE Services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        )
    ''')
    
    # Create Cart table
    cursor.execute('''
        CREATE TABLE Cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (service_id) REFERENCES Services(service_id),
            FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        )
    ''')
    
    # Create Orders table
    cursor.execute('''
        CREATE TABLE Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Received',
            payment_method TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            customer_city TEXT NOT NULL,
            customer_state TEXT NOT NULL,
            customer_pin TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    ''')
    
    # Create Order_Items table
    cursor.execute('''
        CREATE TABLE Order_Items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES Orders(order_id),
            FOREIGN KEY (service_id) REFERENCES Services(service_id),
            FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
        )
    ''')
    
    # Create Admin table
    cursor.execute('''
        CREATE TABLE Admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == '__main__':
    create_database()
