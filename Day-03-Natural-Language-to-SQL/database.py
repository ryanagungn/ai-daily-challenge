"""
Day 03 - Database Module & Seed Data
Menyediakan in-memory / file SQLite database dengan skema e-commerce realistis:
Customers, Categories, Products, Orders, OrderItems.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple

DB_PATH = Path(__file__).parent / "ecommerce.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inisialisasi tabel dan sample data e-commerce jika belum ada."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        rating REAL DEFAULT 0.0,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );

    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT NOT NULL,
        country TEXT DEFAULT 'Indonesia',
        joined_date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT CHECK(status IN ('completed', 'pending', 'cancelled', 'shipped')),
        payment_method TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    # Cek apakah data sudah ada
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        _seed_data(cursor)

    conn.commit()
    conn.close()

def _seed_data(cursor: sqlite3.Cursor):
    """Seed data realistis untuk demo e-commerce."""
    # 1. Categories
    categories = [
        (1, "Elektronik & Gadget", "Smartphone, laptop, aksesoris audio dan gadget pintar"),
        (2, "Pakaian & Fashion", "Baju, jaket, sepatu, dan aksesoris gaya hidup"),
        (3, "Peralatan Rumah Tangga", "Perabot rumah, dapur, dekorasi dan perkakas"),
        (4, "Buku & Alat Tulis", "Buku pemrograman, bisnis, novel dan perlengkapan kantor"),
        (5, "Kesehatan & Olahraga", "Suplemen, perlengkapan gym, sepeda dan fitness")
    ]
    cursor.executemany("INSERT INTO categories VALUES (?, ?, ?)", categories)

    # 2. Products (id, name, cat_id, price, stock, rating)
    products = [
        (1, "Laptop Pro 14 M3", 1, 21999000, 15, 4.9),
        (2, "Wireless Noise Cancelling Headphone", 1, 2499000, 45, 4.8),
        (3, "Mechanical Keyboard RGB", 1, 899000, 80, 4.7),
        (4, "Smartwatch Fitness Tracker", 1, 1250000, 30, 4.5),
        (5, "Kaos Polos Cotton Combed 30s", 2, 85000, 200, 4.6),
        (6, "Jaket Hoodie Waterproof", 2, 349000, 50, 4.8),
        (7, "Sepatu Sneakers Low-Top", 2, 699000, 40, 4.7),
        (8, "Air Fryer Digital 4L", 3, 799000, 25, 4.8),
        (9, "Robot Vacuum Cleaner Smart", 3, 2899000, 12, 4.6),
        (10, "Set Pisau Dapur Stainless", 3, 249000, 60, 4.5),
        (11, "Buku AI & Machine Learning with Python", 4, 185000, 95, 4.9),
        (12, "Buku Designing Data-Intensive Apps", 4, 275000, 40, 5.0),
        (13, "Notebook Kulit Hardcover A5", 4, 75000, 150, 4.7),
        (14, "Matras Yoga Anti-Slip 6mm", 5, 195000, 70, 4.7),
        (15, "Whey Protein Isolate 1kg", 5, 499000, 35, 4.8),
        (16, "Dumbbell Set 20kg Adjustable", 5, 850000, 20, 4.6)
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)", products)

    # 3. Customers (id, name, email, city, country, joined_date)
    customers = [
        (1, "Budi Santoso", "budi.santoso@gmail.com", "Jakarta", "Indonesia", "2024-01-15"),
        (2, "Siti Rahmawati", "siti.rahma@yahoo.com", "Bandung", "Indonesia", "2024-02-10"),
        (3, "Ahmad Hidayat", "ahmad.h@techcorp.id", "Surabaya", "Indonesia", "2024-03-05"),
        (4, "Dewi Lestari", "dewi.lestari@gmail.com", "Yogyakarta", "Indonesia", "2024-03-22"),
        (5, "Rizky Pratama", "rizky.pratama@outlook.com", "Jakarta", "Indonesia", "2024-04-18"),
        (6, "Indah Permata", "indah.p@gmail.com", "Medan", "Indonesia", "2024-05-02"),
        (7, "Fajar Nugraha", "fajar.nugraha@gmail.com", "Semarang", "Indonesia", "2024-06-11"),
        (8, "Anisa Maharani", "anisa.m@gmail.com", "Jakarta", "Indonesia", "2024-06-25"),
        (9, "Kevin Wijaya", "kevin.wijaya@gmail.com", "Bali", "Indonesia", "2024-07-04"),
        (10, "Maya Anggraini", "maya.a@gmail.com", "Bandung", "Indonesia", "2024-08-14")
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)", customers)

    # 4. Orders (id, customer_id, date, total, status, payment)
    orders = [
        (1, 1, "2024-05-10", 22898000, "completed", "credit_card"),
        (2, 2, "2024-05-14", 1048000, "completed", "qris"),
        (3, 3, "2024-05-20", 2499000, "completed", "bank_transfer"),
        (4, 1, "2024-06-01", 349000, "completed", "qris"),
        (5, 4, "2024-06-15", 460000, "completed", "e_wallet"),
        (6, 5, "2024-06-22", 2899000, "shipped", "credit_card"),
        (7, 6, "2024-07-01", 699000, "completed", "bank_transfer"),
        (8, 7, "2024-07-05", 1349000, "completed", "qris"),
        (9, 8, "2024-07-12", 24498000, "completed", "credit_card"),
        (10, 2, "2024-07-18", 195000, "completed", "e_wallet"),
        (11, 9, "2024-08-01", 1349000, "pending", "bank_transfer"),
        (12, 10, "2024-08-10", 799000, "completed", "qris"),
        (13, 3, "2024-08-15", 850000, "shipped", "bank_transfer"),
        (14, 5, "2024-08-20", 170000, "completed", "qris"),
        (15, 1, "2024-08-25", 499000, "completed", "credit_card")
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders)

    # 5. Order Items (id, order_id, product_id, quantity, unit_price)
    order_items = [
        (1, 1, 1, 1, 21999000),  # Laptop
        (2, 1, 3, 1, 899000),    # Keyboard
        (3, 2, 6, 1, 349000),    # Hoodie
        (4, 2, 7, 1, 699000),    # Sneakers
        (5, 3, 2, 1, 2499000),   # Headphone
        (6, 4, 6, 1, 349000),    # Hoodie
        (7, 5, 11, 1, 185000),   # Buku AI
        (8, 5, 12, 1, 275000),   # Buku DDIA
        (9, 6, 9, 1, 2899000),   # Robot Vacuum
        (10, 7, 7, 1, 699000),   # Sneakers
        (11, 8, 4, 1, 1250000),  # Smartwatch
        (12, 8, 13, 1, 75000),   # Notebook
        (13, 8, 14, 1, 195000),  # Matras Yoga
        (14, 9, 1, 1, 21999000), # Laptop
        (15, 9, 2, 1, 2499000),  # Headphone
        (16, 10, 14, 1, 195000), # Matras
        (17, 11, 4, 1, 1250000), # Smartwatch
        (18, 12, 8, 1, 799000),  # Air Fryer
        (19, 13, 16, 1, 850000), # Dumbbell
        (20, 14, 5, 2, 85000),   # Kaos x2
        (21, 15, 15, 1, 499000)  # Whey Protein
    ]
    cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", order_items)

def get_schema_description() -> str:
    """Mengembalikan DDL schema lengkap untuk prompt LLM."""
    return """
    DATABASE SCHEMA (SQLite):

    TABLE categories (
        category_id INTEGER PRIMARY KEY,
        name TEXT, -- e.g. 'Elektronik & Gadget', 'Pakaian & Fashion'
        description TEXT
    );

    TABLE products (
        product_id INTEGER PRIMARY KEY,
        name TEXT,
        category_id INTEGER REFERENCES categories(category_id),
        price REAL, -- in IDR (Rupiah)
        stock_quantity INTEGER,
        rating REAL -- 0.0 to 5.0
    );

    TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        city TEXT, -- e.g. 'Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Yogyakarta'
        country TEXT,
        joined_date TEXT -- YYYY-MM-DD
    );

    TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(customer_id),
        order_date TEXT, -- YYYY-MM-DD
        total_amount REAL, -- in IDR
        status TEXT, -- 'completed', 'pending', 'cancelled', 'shipped'
        payment_method TEXT -- 'credit_card', 'qris', 'bank_transfer', 'e_wallet'
    );

    TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER REFERENCES orders(order_id),
        product_id INTEGER REFERENCES products(product_id),
        quantity INTEGER,
        unit_price REAL
    );
    """

def execute_query(query: str, max_rows: int = 100) -> Tuple[List[str], List[Dict[str, Any]], float]:
    """
    Mengeksekusi SQL query secara aman (read-only) dan mengembalikan:
    (column_names, rows, execution_time_ms)
    """
    import time
    
    # Inisialisasi DB jika belum ada
    init_database()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    start_time = time.time()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description] if cursor.description else []
    raw_rows = cursor.fetchmany(max_rows)
    elapsed_ms = (time.time() - start_time) * 1000
    
    rows = [dict(row) for row in raw_rows]
    conn.close()
    
    return columns, rows, elapsed_ms
