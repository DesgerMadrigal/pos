import sqlite3
from typing import Sequence, Mapping

class InventoryDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ajuste directo: +qty o -qty
    def move(self, product_id: int, warehouse_id: int,
             qty: float, concept: str = "") -> None:
        with self.conn:
            self.conn.execute("""
                INSERT INTO stock_movements(date, product_id, warehouse_id, qty, concept)
                VALUES (datetime('now','localtime'), ?, ?, ?, ?)
            """, (product_id, warehouse_id, qty, concept))
            # actualiza stock en products (un ejemplo simple, sin multi-almacén detallado)
            self.conn.execute("UPDATE products SET stock = stock + ? WHERE id=?",
                              (qty, product_id))

    def movements(self, product_id: int | None = None) -> Sequence[Mapping]:
        cur = self.conn.cursor()
        if product_id:
            cur.execute("""
                SELECT m.date, p.name, m.qty, m.concept
                  FROM stock_movements m
                  JOIN products p ON p.id = m.product_id
                 WHERE product_id = ?
              ORDER BY m.id DESC
            """, (product_id,))
        else:
            cur.execute("""
                SELECT m.date, p.name, m.qty, m.concept
                  FROM stock_movements m
                  JOIN products p ON p.id = m.product_id
              ORDER BY m.id DESC
            """)
        return cur.fetchall()
