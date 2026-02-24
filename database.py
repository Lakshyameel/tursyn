import sqlite3
from datetime import datetime

DB_NAME = "restaurant.db"   # use your existing DB name

# =========================
# CREATE TABLE
# =========================
def create_orders_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id TEXT,
        customer_id TEXT,
        items TEXT,
        quantities TEXT,
        total REAL,
        timestamp TEXT,
        source TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# SAVE ORDER
# =========================
def save_order(rest_id, cust_id, items, qtys, total, source):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO orders
    (restaurant_id, customer_id, items, quantities, total, timestamp, source)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (rest_id, cust_id, items, qtys, total, timestamp, source))

    conn.commit()
    conn.close()


# =========================
# GET ALL ORDERS
# =========================
def get_all_orders():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        order_id,
        restaurant_id,
        customer_id,
        items,
        quantities,
        total,
        timestamp,
        source
    FROM orders
    ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows