import sqlite3
from pathlib import Path

DB_NAME = "pos.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn

def _create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode     TEXT UNIQUE,
            name        TEXT NOT NULL,
            description TEXT,
            unit        TEXT DEFAULT 'pz',
            price       REAL NOT NULL DEFAULT 0,
            discount    REAL NOT NULL DEFAULT 0,
            iva         REAL NOT NULL DEFAULT 0,
            sku         TEXT,
            stock       INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Tabla clientes y placeholders de otras …
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            credit_limit REAL DEFAULT 0,
            balance REAL DEFAULT 0
        )
    """)

    # Placeholder ventas / items (vacías aún)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            client_id INTEGER,
            total REAL NOT NULL,
            discount REAL DEFAULT 0,
            paid REAL DEFAULT 0,
            payment_type TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            discount REAL DEFAULT 0,
            iva REAL DEFAULT 0,
            FOREIGN KEY(sale_id) REFERENCES sales(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)
    
    # Movimientos de caja
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cash_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            concept TEXT NOT NULL,
            amount REAL NOT NULL      -- positivo = entrada, negativo = salida
        )
    """)

    # Almacenes (1 = almacén principal por defecto)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS warehouses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT
        )
    """)
    cur.execute("INSERT OR IGNORE INTO warehouses(id, name) VALUES (1,'Principal')")

    # Movimientos de inventario
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            qty REAL NOT NULL,
            concept TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(warehouse_id) REFERENCES warehouses(id)
        )
    """)

    # Proveedores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            legal_id TEXT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            bank_info TEXT
        )
    """)

    # Cuentas por pagar a proveedores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            concept TEXT NOT NULL,
            amount REAL NOT NULL,
            paid REAL DEFAULT 0,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )
    """)

    conn.commit()
