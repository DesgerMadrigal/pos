"""
pos.models.inventory
--------------------
DAO de inventarios con soporte multi-almacén, movimientos y traspasos.
"""

from __future__ import annotations

import sqlite3
from typing import Sequence, Mapping, Optional


class InventoryDAO:
    """Data Access Object para operaciones de inventario."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # ───────────── helpers ─────────────
    def stock(self, product_id: int, warehouse_id: Optional[int] = None) -> float:
        """Devuelve existencias (por almacén o globales)."""
        cur = self.conn.cursor()
        if warehouse_id is None:
            cur.execute(
                "SELECT COALESCE(SUM(qty),0) FROM stock_movements WHERE product_id=?",
                (product_id,),
            )
        else:
            cur.execute(
                "SELECT COALESCE(SUM(qty),0) FROM stock_movements "
                "WHERE product_id=? AND warehouse_id=?",
                (product_id, warehouse_id),
            )
        (qty,) = cur.fetchone()
        return float(qty or 0)

    # ───────────── movimientos ─────────────
    def move(self, product_id: int, warehouse_id: int, qty: float, concept: str = ""):
        """Inserta un movimiento simple (entrada + / salida –)."""
        if qty < 0 and self.stock(product_id, warehouse_id) + qty < 0:
            raise ValueError("Stock insuficiente")

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO stock_movements(date,product_id,warehouse_id,qty,concept)
                VALUES (datetime('now','localtime'),?,?,?,?)
                """,
                (product_id, warehouse_id, qty, concept),
            )
            self.conn.execute(
                "UPDATE products SET stock = stock + ? WHERE id = ?",
                (qty, product_id),
            )

    def transfer(
        self,
        product_id: int,
        src: int,
        dst: int,
        qty: float,
        concept: str = "Traspaso",
    ) -> None:
        """Mueve stock de `src` a `dst` en una transacción atómica."""
        if src == dst:
            raise ValueError("Origen y destino no pueden ser iguales")
        if self.stock(product_id, src) < qty:
            raise ValueError("Stock insuficiente en almacén origen")

        with self.conn:
            self.move(product_id, src, -qty, f"{concept} salida")
            self.move(product_id, dst, +qty, f"{concept} entrada")

    # ───────────── consultas ─────────────
    def movements(self, product_id: Optional[int] = None) -> Sequence[Mapping]:
        """Devuelve los movimientos (últimos primero)."""
        cur = self.conn.cursor()
        if product_id:
            cur.execute(
                """
                SELECT m.date, p.name, m.qty, m.concept, m.warehouse_id
                  FROM stock_movements m
                  JOIN products p ON p.id = m.product_id
                 WHERE m.product_id = ?
              ORDER BY m.id DESC
                """,
                (product_id,),
            )
        else:
            cur.execute(
                """
                SELECT m.date, p.name, m.qty, m.concept, m.warehouse_id
                  FROM stock_movements m
                  JOIN products p ON p.id = m.product_id
              ORDER BY m.id DESC
                """
            )
        return cur.fetchall()
