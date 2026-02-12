from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"


# -----------------------
# Database Connection
# -----------------------
def get_db():
    conn = sqlite3.connect("database.db", timeout=10)
    conn.row_factory = sqlite3.Row
    return conn



# -----------------------
# Home (Login Page)
# -----------------------
@app.route("/")
def home():
    return render_template("index.html")




@app.route("/login/<role>")
def login_page(role):
    return render_template("login.html", role=role)



# -----------------------
# Register
# -----------------------
@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]

    conn = get_db()
    conn.execute(
        "INSERT INTO users (name, email, password, role, status) VALUES (?, ?, ?, ?, ?)",
        (name, email, password, role, "approved")
    )
    conn.commit()
    conn.close()

    return redirect("/")


# -----------------------
# Login
# -----------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=? AND role=?",
        (email, password, role)
    ).fetchone()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["role"] = role

        if role == "admin":
            return redirect("/admin")
        elif role == "vendor":
            return redirect("/vendor")
        else:
            return redirect("/user")

    return "Invalid Login"



# -----------------------
# User Dashboard
# -----------------------
@app.route("/user")
def user_dashboard():
    if session.get("role") != "user":
        return "Unauthorized"

    conn = get_db()
    services = conn.execute(
        "SELECT * FROM services WHERE status='approved'"
    ).fetchall()
    conn.close()

    return render_template("user_dashboard.html", services=services)


# -----------------------
# Vendor Dashboard
# -----------------------
@app.route("/vendor")
def vendor_dashboard():
    if session.get("role") != "vendor":
        return "Unauthorized"
    return render_template("vendor_dashboard.html")


# Vendor Add Service
@app.route("/add_service", methods=["POST"])
def add_service():
    if session.get("role") != "vendor":
        return "Unauthorized"

    name = request.form["name"]
    category = request.form["category"]
    price = request.form["price"]
    description = request.form["description"]
    vendor_id = session["user_id"]

    conn = get_db()
    conn.execute("""
        INSERT INTO services (vendor_id, name, category, price, description, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (vendor_id, name, category, price, description, "pending"))
    conn.commit()
    conn.close()

    return redirect("/vendor")


# Vendor View Own Services
@app.route("/vendor_services")
def vendor_services():
    if session.get("role") != "vendor":
        return "Unauthorized"

    vendor_id = session["user_id"]
    conn = get_db()
    services = conn.execute(
        "SELECT * FROM services WHERE vendor_id=?",
        (vendor_id,)
    ).fetchall()
    conn.close()

    return render_template("vendor_services.html", services=services)


# -----------------------
# Admin Dashboard
# -----------------------
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return "Unauthorized"
    return render_template("admin_dashboard.html")


# Admin Manage Services
@app.route("/manage_services")
def manage_services():
    if session.get("role") != "admin":
        return "Unauthorized"

    conn = get_db()
    services = conn.execute("""
        SELECT services.*, users.name as vendor_name
        FROM services
        JOIN users ON services.vendor_id = users.id
    """).fetchall()
    conn.close()

    return render_template("manage_services.html", services=services)


# Approve Service
@app.route("/approve/<int:id>")
def approve_service(id):
    if session.get("role") != "admin":
        return "Unauthorized"

    conn = get_db()
    conn.execute("UPDATE services SET status='approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/manage_services")


# Reject Service
@app.route("/reject/<int:id>")
def reject_service(id):
    if session.get("role") != "admin":
        return "Unauthorized"

    conn = get_db()
    conn.execute("UPDATE services SET status='rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/manage_services")


# -----------------------
# Logout (Useful)
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add_to_cart/<int:service_id>")
def add_to_cart(service_id):
    if session.get("role") != "user":
        return "Unauthorized"

    user_id = session["user_id"]

    conn = get_db()
    conn.execute(
        "INSERT INTO cart (user_id, service_id, quantity) VALUES (?, ?, ?)",
        (user_id, service_id, 1)
    )
    conn.commit()
    conn.close()

    return redirect("/user")
@app.route("/checkout")
def checkout():
    if session.get("role") != "user":
        return "Unauthorized"

    user_id = session["user_id"]
    conn = get_db()

    items = conn.execute("""
        SELECT services.price
        FROM cart
        JOIN services ON cart.service_id = services.id
        WHERE cart.user_id=?
    """, (user_id,)).fetchall()

    if not items:
        conn.close()
        return "Cart is empty or already checked out"

    total = sum(item["price"] for item in items)

    # Insert order
    conn.execute(
        "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
        (user_id, total, "Placed")
    )

    # Clear cart
    conn.execute("DELETE FROM cart WHERE user_id=?", (user_id,))

    conn.commit()
    conn.close()

    return render_template("success.html", total=total)
@app.route("/my_orders")
def my_orders():
    if session.get("role") != "user":
        return "Unauthorized"

    user_id = session["user_id"]
    conn = get_db()

    orders = conn.execute("""
        SELECT * FROM orders
        WHERE user_id=?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    conn.close()

    return render_template("my_orders.html", orders=orders)
@app.route("/admin_orders")
def admin_orders():
    if session.get("role") != "admin":
        return "Unauthorized"

    conn = get_db()

    orders = conn.execute("""
        SELECT orders.*, users.name as user_name
        FROM orders
        JOIN users ON orders.user_id = users.id
        ORDER BY orders.id DESC
    """).fetchall()

    conn.close()

    return render_template("admin_orders.html", orders=orders)
@app.route("/request_item")
def request_item_page():
    if session.get("role") != "user":
        return "Unauthorized"
    return render_template("request_item.html")
@app.route("/request_item", methods=["POST"])
def submit_request():
    user_id = session["user_id"]
    description = request.form["description"]

    conn = get_db()
    conn.execute(
        "INSERT INTO requests (user_id, description, status) VALUES (?, ?, ?)",
        (user_id, description, "Pending")
    )
    conn.commit()
    conn.close()

    return redirect("/user")


@app.route("/cart")
def view_cart():
    if session.get("role") != "user":
        return "Unauthorized"

    user_id = session["user_id"]

    conn = get_db()
    items = conn.execute("""
        SELECT cart.id, services.name, services.price
        FROM cart
        JOIN services ON cart.service_id = services.id
        WHERE cart.user_id=?
    """, (user_id,)).fetchall()

    conn.close()

    return render_template("cart.html", items=items)
# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

