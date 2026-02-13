from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_in_production'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    return stored_hash == hash_password(password)

# INDEX PAGE
@app.route('/')
def index():
    return render_template('index.html')

# USER LOGIN
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and verify_password(user['password'], password):
            session.clear()
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['role'] = 'user'
            return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password', role='user')
    
    return render_template('login.html', role='user')

# USER REGISTER
@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        if not all([name, email, password, phone]):
            return render_template('register.html', error='All fields are required', role='user')
        
        hashed_password = hash_password(password)
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO Users (name, email, password, phone) VALUES (?, ?, ?, ?)',
                        (name, email, hashed_password, phone))
            conn.commit()
            conn.close()
            return redirect(url_for('user_login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Email already exists', role='user')
    
    return render_template('register.html', role='user')

# VENDOR LOGIN
@app.route('/vendor_login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        vendor = conn.execute('SELECT * FROM Vendors WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if vendor and verify_password(vendor['password'], password):
            session.clear()
            session['vendor_id'] = vendor['vendor_id']
            session['vendor_name'] = vendor['name']
            session['role'] = 'vendor'
            return redirect(url_for('vendor_dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password', role='vendor')
    
    return render_template('login.html', role='vendor')

# VENDOR REGISTER
@app.route('/vendor_register', methods=['GET', 'POST'])
def vendor_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        category = request.form.get('category')
        description = request.form.get('description')
        
        if not all([name, email, password, phone, category]):
            return render_template('register.html', error='All fields are required', role='vendor')
        
        hashed_password = hash_password(password)
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO Vendors (name, email, password, phone, category, description) VALUES (?, ?, ?, ?, ?, ?)',
                        (name, email, hashed_password, phone, category, description))
            conn.commit()
            conn.close()
            return redirect(url_for('vendor_login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Email already exists', role='vendor')
    
    return render_template('register.html', role='vendor')

# ADMIN LOGIN
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM Admin WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if admin and verify_password(admin['password'], password):
            session.clear()
            session['admin_email'] = email
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password', role='admin')
    
    return render_template('login.html', role='admin')

# USER DASHBOARD
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    conn = get_db_connection()
    categories = conn.execute('SELECT DISTINCT category FROM Vendors ORDER BY category').fetchall()
    conn.close()
    
    return render_template('user_dashboard.html', 
                         user_name=session.get('user_name'),
                         categories=[cat['category'] for cat in categories])

# VIEW VENDORS BY CATEGORY
@app.route('/vendor_services')
def vendor_services():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    category = request.args.get('category')
    
    conn = get_db_connection()
    vendors = conn.execute('''
        SELECT DISTINCT v.vendor_id, v.name, v.category 
        FROM Vendors v 
        WHERE v.category = ?
    ''', (category,)).fetchall()
    
    vendor_id = request.args.get('vendor_id')
    services = []
    if vendor_id:
        services = conn.execute('''
            SELECT * FROM Services 
            WHERE vendor_id = ?
        ''', (vendor_id,)).fetchall()
    
    conn.close()
    
    return render_template('vendor_services.html',
                         vendors=vendors,
                         services=services,
                         category=category,
                         selected_vendor=vendor_id,
                         user_name=session.get('user_name'))

# ADD TO CART
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    data = request.get_json()
    user_id = session['user_id']
    service_id = data.get('service_id')
    vendor_id = data.get('vendor_id')
    quantity = data.get('quantity', 1)
    
    conn = get_db_connection()
    
    # Check if item already in cart
    existing = conn.execute('''
        SELECT * FROM Cart 
        WHERE user_id = ? AND service_id = ? AND vendor_id = ?
    ''', (user_id, service_id, vendor_id)).fetchone()
    
    if existing:
        conn.execute('''
            UPDATE Cart 
            SET quantity = quantity + ?
            WHERE user_id = ? AND service_id = ? AND vendor_id = ?
        ''', (quantity, user_id, service_id, vendor_id))
    else:
        conn.execute('''
            INSERT INTO Cart (user_id, service_id, vendor_id, quantity)
            VALUES (?, ?, ?, ?)
        ''', (user_id, service_id, vendor_id, quantity))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Added to cart'})

# VIEW CART
@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT c.cart_id, c.quantity, s.service_id, s.name, s.price, v.name as vendor_name, v.vendor_id
        FROM Cart c
        JOIN Services s ON c.service_id = s.service_id
        JOIN Vendors v ON c.vendor_id = v.vendor_id
        WHERE c.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return render_template('cart.html',
                         cart_items=cart_items,
                         total=total,
                         user_name=session.get('user_name'))

# REMOVE FROM CART
@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart WHERE cart_id = ? AND user_id = ?', (cart_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return redirect(url_for('cart'))

# CLEAR CART
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM Cart WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    return redirect(url_for('cart'))

# CHECKOUT
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    
    name = request.form.get('name')
    email = request.form.get('email')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    pin = request.form.get('pin')
    phone = request.form.get('phone')
    payment_method = request.form.get('payment_method')
    
    if not all([name, email, address, city, state, pin, phone, payment_method]):
        return redirect(url_for('cart'))
    
    conn = get_db_connection()
    
    # Get cart items
    cart_items = conn.execute('''
        SELECT c.quantity, s.service_id, s.price, c.vendor_id
        FROM Cart c
        JOIN Services s ON c.service_id = s.service_id
        WHERE c.user_id = ?
    ''', (user_id,)).fetchall()
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Create order
    cursor = conn.execute('''
        INSERT INTO Orders (user_id, total, status, payment_method, customer_name, customer_email, 
                           customer_address, customer_city, customer_state, customer_pin, customer_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, total, 'Received', payment_method, name, email, address, city, state, pin, phone))
    
    order_id = cursor.lastrowid
    
    # Add order items
    for item in cart_items:
        conn.execute('''
            INSERT INTO Order_Items (order_id, service_id, vendor_id, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, item['service_id'], item['vendor_id'], item['quantity'], item['price']))
    
    # Clear cart
    conn.execute('DELETE FROM Cart WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('success'))

# SUCCESS PAGE
@app.route('/success')
def success():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    return render_template('success.html', user_name=session.get('user_name'))

# MY ORDERS
@app.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT o.order_id, o.total, o.status, o.created_at, o.payment_method,
               COUNT(oi.item_id) as item_count
        FROM Orders o
        LEFT JOIN Order_Items oi ON o.order_id = oi.order_id
        WHERE o.user_id = ?
        GROUP BY o.order_id
        ORDER BY o.created_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    return render_template('my_orders.html',
                         orders=orders,
                         user_name=session.get('user_name'))

# VENDOR DASHBOARD
@app.route('/vendor_dashboard')
def vendor_dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor_login'))
    
    vendor_id = session['vendor_id']
    
    conn = get_db_connection()
    service_count = conn.execute('SELECT COUNT(*) as count FROM Services WHERE vendor_id = ?', 
                                 (vendor_id,)).fetchone()['count']
    order_count = conn.execute('''
        SELECT COUNT(DISTINCT o.order_id) as count
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        WHERE oi.vendor_id = ?
    ''', (vendor_id,)).fetchone()['count']
    conn.close()
    
    return render_template('vendor_dashboard.html',
                         vendor_name=session.get('vendor_name'),
                         service_count=service_count,
                         order_count=order_count)

# MANAGE SERVICES
@app.route('/manage_services', methods=['GET', 'POST'])
def manage_services():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor_login'))
    
    vendor_id = session['vendor_id']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')
            
            if not all([name, price, category]):
                pass
            
            try:
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO Services (vendor_id, name, description, price, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (vendor_id, name, description, float(price), category))
                conn.commit()
                conn.close()
            except Exception as e:
                pass
        
        elif action == 'update':
            service_id = request.form.get('service_id')
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')
            
            conn = get_db_connection()
            conn.execute('''
                UPDATE Services 
                SET name = ?, description = ?, price = ?, category = ?
                WHERE service_id = ? AND vendor_id = ?
            ''', (name, description, float(price), category, service_id, vendor_id))
            conn.commit()
            conn.close()
        
        elif action == 'delete':
            service_id = request.form.get('service_id')
            conn = get_db_connection()
            conn.execute('DELETE FROM Services WHERE service_id = ? AND vendor_id = ?', 
                        (service_id, vendor_id))
            conn.commit()
            conn.close()
    
    conn = get_db_connection()
    services = conn.execute('SELECT * FROM Services WHERE vendor_id = ?', (vendor_id,)).fetchall()
    conn.close()
    
    return render_template('manage_services.html',
                         services=services,
                         vendor_name=session.get('vendor_name'))

# REQUEST ITEMS (Vendor Orders)
@app.route('/request_item')
def request_item():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor_login'))
    
    vendor_id = session['vendor_id']
    
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT o.order_id, o.customer_name, o.customer_email, o.customer_address,
               o.customer_city, o.customer_state, o.customer_pin, o.customer_phone,
               o.status, o.created_at, o.total,
               GROUP_CONCAT(s.name) as services,
               GROUP_CONCAT(oi.quantity) as quantities
        FROM Orders o
        JOIN Order_Items oi ON o.order_id = oi.order_id
        JOIN Services s ON oi.service_id = s.service_id
        WHERE oi.vendor_id = ?
        GROUP BY o.order_id
        ORDER BY o.created_at DESC
    ''', (vendor_id,)).fetchall()
    
    conn.close()
    
    return render_template('request_item.html',
                         orders=orders,
                         vendor_name=session.get('vendor_name'))

# UPDATE ORDER STATUS
@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor_login'))
    
    order_id = request.form.get('order_id')
    status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute('UPDATE Orders SET status = ? WHERE order_id = ?', (status, order_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('request_item'))

# ADMIN DASHBOARD
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    user_count = conn.execute('SELECT COUNT(*) as count FROM Users').fetchone()['count']
    vendor_count = conn.execute('SELECT COUNT(*) as count FROM Vendors').fetchone()['count']
    order_count = conn.execute('SELECT COUNT(*) as count FROM Orders').fetchone()['count']
    conn.close()
    
    return render_template('admin_dashboard.html',
                         user_count=user_count,
                         vendor_count=vendor_count,
                         order_count=order_count)

# ADMIN - MANAGE USERS
@app.route('/admin_users')
def admin_users():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM Users ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', section='users', users=users)

# ADMIN - MANAGE VENDORS
@app.route('/admin_vendors')
def admin_vendors():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    vendors = conn.execute('SELECT * FROM Vendors ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', section='vendors', vendors=vendors)

# ADMIN - VIEW ORDERS
@app.route('/admin_orders')
def admin_orders():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT o.order_id, o.total, o.status, o.payment_method, o.created_at,
               u.name as customer_name, u.email as customer_email,
               COUNT(oi.item_id) as item_count
        FROM Orders o
        JOIN Users u ON o.user_id = u.user_id
        LEFT JOIN Order_Items oi ON o.order_id = oi.order_id
        GROUP BY o.order_id
        ORDER BY o.created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin_orders.html', orders=orders)

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Check if database exists, if not create it
    if not os.path.exists('database.db'):
        from create_db import create_database
        create_database()
    
    app.run(debug=True)
