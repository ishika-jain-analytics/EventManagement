import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
INSERT INTO users (name, email, password, role, status)
VALUES ('Admin', 'admin@gmail.com', 'admin123', 'admin', 'approved')
""")

conn.commit()
conn.close()

print("Admin created!")
