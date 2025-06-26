# POS/models/sale.py
import sqlite3
from typing import Sequence, Mapping

class SaleDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn, self.cur = conn, conn.cursor()

    # carrito = list[dict(product_id, qty, price, discount, iva)]
    def create_sale(self, *, client_id: int | None, cart: Sequence[Mapping],
                    discount_global: float = 0, paid: float = 0) -> int:
        total = sum((item["price"] * item["qty"]) for item in cart)
        total *= (1 - discount_global / 100)

        with self.conn:          # ⇒ COMMIT o ROLLBACK automático
            self.cur.execute("""
                INSERT INTO sales(date, client_id, total, discount, paid, payment_type)
                VALUES (datetime('now','localtime'), ?, ?, ?, ?, ?)
            """, (client_id, total, discount_global, paid,
                  "contado" if paid >= total else "credito"))
            sale_id = self.cur.lastrowid

            for it in cart:
                self.cur.execute("""
                    INSERT INTO sale_items(sale_id, product_id, quantity, price, discount, iva)
                    VALUES (?,?,?,?,?,?)
                """, (sale_id, it["product_id"], it["qty"], it["price"],
                      it.get("discount", 0), it.get("iva", 0)))
                # descuenta stock
                self.cur.execute("UPDATE products SET stock = stock - ? WHERE id=?",
                                 (it["qty"], it["product_id"]))

            # saldo del cliente si fue a crédito
            if client_id and paid < total:
                self.cur.execute("""
                    UPDATE clients SET balance = balance + ? WHERE id=?
                """, (total - paid, client_id))

        return sale_id
