from typing import Sequence, Mapping
import sqlite3

class ProductDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # CRUD ----------------------------------------------------------------
    def add(self, *, barcode: str, name: str, description: str = "",
            unit: str = "pz", price: float = 0, discount: float = 0,
            iva: float = 0, sku: str = "", stock: int = 0) -> None:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO products(barcode,name,description,unit,price,
                                 discount,iva,sku,stock)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (barcode, name, description, unit, price,
              discount, iva, sku, stock))
        self.conn.commit()

    def search(self, text: str = ""):
        cur = self.conn.cursor()
        if text:
            like = f"%{text}%"
            cur.execute("""
                SELECT id, barcode, name, unit, price, stock
                  FROM products
                 WHERE barcode LIKE ? OR name LIKE ? OR sku LIKE ?
              ORDER BY name
            """, (like, like, like))
        else:
            cur.execute("""
                SELECT id, barcode, name, unit, price, stock
                  FROM products
              ORDER BY name
            """)
        return [tuple(row) for row in cur.fetchall()]
    
    def barcode_exists(self, barcode: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM products WHERE barcode = ? LIMIT 1", (barcode,))
        return cur.fetchone() is not None
