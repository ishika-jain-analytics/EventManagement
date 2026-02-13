# Event Management System

A complete event management system built with Python (Flask), HTML, and CSS. The system allows users to book event services from vendors with a modern, responsive UI.

## Features

### User Features
- Register and login
- Browse vendors by category (Catering, Florist, Decoration, Lighting)
- View vendor services
- Add services to cart
- View and manage shopping cart
- Checkout with delivery details
- Track orders
- View order status (Received, Ready for Shipping, Out for Delivery)

### Vendor Features
- Register and login
- Add, update, and delete services
- View customer orders
- Update order status
- Manage pricing and descriptions

### Admin Features
- Login to admin panel
- View all users
- View all vendors
- View all orders
- Monitor system activity

## Technology Stack
- **Backend**: Python 3.x (Flask)
- **Frontend**: HTML5, CSS3
- **Database**: SQLite3
- **No External Frameworks**: Pure Python + HTML + CSS (No Bootstrap, No JavaScript Frameworks)

## Project Structure

```
event_management/
├── app.py                    # Main Flask application
├── create_db.py             # Database creation script
├── add_admin.py             # Admin creation script
├── database.db              # SQLite database (created after running create_db.py)
└── templates/
    ├── index.html           # Home page
    ├── login.html           # Login page (for user, vendor, admin)
    ├── register.html        # Registration page (for user, vendor)
    ├── user_dashboard.html  # User home page
    ├── vendor_services.html # Vendor services display
    ├── cart.html            # Shopping cart
    ├── my_orders.html       # User orders
    ├── success.html         # Order success page
    ├── vendor_dashboard.html # Vendor home page
    ├── manage_services.html # Service management
    ├── request_item.html    # Vendor order management
    ├── admin_dashboard.html # Admin home page
    └── admin_orders.html    # Admin view all orders
```

## Database Schema

### Users Table
- user_id (Primary Key)
- name
- email (Unique)
- password (hashed)
- phone
- created_at (timestamp)

### Vendors Table
- vendor_id (Primary Key)
- name
- email (Unique)
- password (hashed)
- phone
- category
- description
- created_at (timestamp)

### Services Table
- service_id (Primary Key)
- vendor_id (Foreign Key)
- name
- description
- price
- category
- created_at (timestamp)

### Cart Table
- cart_id (Primary Key)
- user_id (Foreign Key)
- service_id (Foreign Key)
- vendor_id (Foreign Key)
- quantity
- added_at (timestamp)

### Orders Table
- order_id (Primary Key)
- user_id (Foreign Key)
- total
- status (Received, Ready for Shipping, Out for Delivery)
- payment_method (Cash, UPI)
- customer_name, customer_email, customer_address, customer_city, customer_state, customer_pin, customer_phone
- created_at (timestamp)

### Order_Items Table
- item_id (Primary Key)
- order_id (Foreign Key)
- service_id (Foreign Key)
- vendor_id (Foreign Key)
- quantity
- price

### Admin Table
- admin_id (Primary Key)
- email (Unique)
- password (hashed)
- created_at (timestamp)

## Installation & Setup

### Step 1: Prerequisites
- Python 3.7 or higher installed
- pip (Python package manager)

### Step 2: Create Project Directory
```bash
mkdir event_management
cd event_management
```

### Step 3: Install Flask
```bash
pip install flask
```

### Step 4: Create Database
```bash
python create_db.py
```

Output:
```
Database created successfully!
```

### Step 5: Add Admin User
```bash
python add_admin.py
```

Output:
```
Admin added successfully!
Email: admin@event.com
Password: admin123
```

### Step 6: Run the Application
```bash
python app.py
```

Output:
```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

### Step 7: Open in Browser
Navigate to: **http://127.0.0.1:5000**

## User Guide

### For Users
1. Click "User Login" or "Register" on the home page
2. Create a new account with name, email, password, and phone
3. Log in with credentials
4. Select event category (Catering, Florist, Decoration, Lighting)
5. Browse vendors and their services
6. Click "Add to Cart" to add services
7. Go to cart and review items
8. Click "Proceed to Checkout"
9. Fill in delivery details (name, address, city, state, pin, phone)
10. Select payment method (Cash or UPI)
11. Place order
12. Track order status in "My Orders"

### For Vendors
1. Click "Vendor Login" or "Register" on the home page
2. Create account with name, email, password, phone, category, and description
3. Log in to vendor dashboard
4. Go to "Manage Services"
5. Click "+ Add Service" to create new services
6. Fill in service name, category, price, and description
7. View customer orders in "Orders"
8. Update order status as you process them
9. Customers can track the status in real-time

### For Admin
1. Click "Admin Login" on the home page
2. Use credentials:
   - Email: admin@event.com
   - Password: admin123
3. View dashboard with statistics
4. Navigate to Users, Vendors, or Orders sections
5. Monitor all system activity

## Features Breakdown

### Authentication & Security
- Password hashing using SHA256
- Session-based authentication
- Role-based access control (User, Vendor, Admin)

### Shopping Features
- Category-based vendor browsing
- Service listing with prices
- Shopping cart with quantity management
- Remove items from cart
- Clear entire cart
- Checkout with customer details

### Order Management
- Order placement with payment methods
- Order status tracking
- Vendor order processing
- Admin order monitoring

### UI/UX
- Clean, modern design with blue gradient theme
- Responsive layout for mobile and desktop
- Smooth transitions and hover effects
- Intuitive navigation
- Error handling with user feedback

## Default Credentials

### Admin
- Email: admin@event.com
- Password: admin123

## Customization

### Change Secret Key
Edit `app.py` line 10:
```python
app.secret_key = 'your_secret_key_change_in_production'
```

### Change Port
Edit the last line of `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Important Notes

1. **Database Backup**: The `database.db` file is created when you run `create_db.py`. Keep backups of this file.

2. **Development Mode**: The application runs in debug mode by default. For production, change `debug=True` to `debug=False` in `app.py`.

3. **File Names**: Do not change template file names or the system will not work correctly.

4. **Password Security**: In production, use a more secure password hashing method like bcrypt.

5. **Session Security**: In production, use a strong secret key and set `SESSION_COOKIE_SECURE = True`.

## Troubleshooting

### Database Error
If you get a database error, delete `database.db` and run `create_db.py` again:
```bash
del database.db
python create_db.py
python add_admin.py
```

### Port Already in Use
If port 5000 is already in use, edit `app.py`:
```python
app.run(debug=True, port=5001)  # Use a different port
```

### Flask Not Found
Make sure Flask is installed:
```bash
pip install flask
```

### Login Issues
- Verify credentials are correct
- Ensure database exists (`database.db`)
- Check that admin was added: `python add_admin.py`

## Performance Tips

1. The system can handle thousands of users and orders
2. For large deployments, consider:
   - Using PostgreSQL instead of SQLite
   - Adding database indexes
   - Implementing caching
   - Using a production WSGI server (Gunicorn, uWSGI)

## Legal Notice

This is a learning/demo project. For production use:
- Implement proper payment processing
- Add SSL/TLS encryption
- Comply with data protection regulations
- Add CSRF protection
- Implement rate limiting

## Support

For issues or questions, check:
1. The troubleshooting section above
2. Flask documentation: https://flask.palletsprojects.com/
3. SQLite documentation: https://www.sqlite.org/docs.html

---

**Built with Python | HTML | CSS**

Version 1.0 - February 2026
