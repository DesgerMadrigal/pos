"""
pos.models.inventory
--------------------
DAO de inventarios con soporte multi-almacén, movimientos y traspasos.

• Cada movimiento se registra en `stock_movements`.
• El stock por almacén se calcula sumando movimientos; el stock global
  sigue almacenado en `products.stock` para consultas rápidas.
"""

from __future__ import annotations

import sqlite3
from typing import Sequence, Mapping, Optional


class InventoryDAO:
    """Data Access Object para operaciones de inventario."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # ───────────────────────────── helpers ──────────────────────────────
    def stock(
        self,
        product_id: int,
        warehouse_id: Optional[int] = None,
    ) -> float:
        """
        Devuelve el stock disponible.

        • Si se indica `warehouse_id`, solo ese almacén.
        • Si es None, suma en todos los almacenes (stock global).
        """
        cur = self.conn.cursor()
        if warehouse_id is None:
            cur.execute(
                "SELECT COALESCE(SUM(qty), 0) FROM stock_movements "
                "WHERE product_id = ?",
                (product_id,),
            )
        else:
            cur.execute(
                "SELECT COALESCE(SUM(qty), 0) FROM stock_movements "
                "WHERE product_id = ? AND warehouse_id = ?",
                (product_id, warehouse_id),
            )
        (qty,) = cur.fetchone()
        return float(qty or 0)

    # ────────────────────────── operaciones CRUD ─────────────────────────
    def move(
        self,
        product_id: int,
        warehouse_id: int,
        qty: float,
        concept: str = "",
    ) -> None:
        """
        Inserta un movimiento (positivo = entrada, negativo = salida).

        Lanza ValueError si la salida deja stock negativo.
        """
        if qty < 0:
            available = self.stock(product_id, warehouse_id)
            if available + qty < 0:
                raise ValueError(
                    f"Stock insuficiente en almacén {warehouse_id}: "
                    f"disponible {available}, intento mover {abs(qty)}"
                )

        with self.conn:
            # 1) registra el movimiento
            self.conn.execute(
                """
                INSERT INTO stock_movements
                       (date,          product_id, warehouse_id, qty, concept)
                VALUES (datetime('now','localtime'), ?,          ?,           ?,   ?)
                """,
                (product_id, warehouse_id, qty, concept),
            )
            # 2) actualiza el stock global en products
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
        """
        Traslada unidades de un almacén a otro en una transacción atómica.
        """
        if src == dst:
            raise ValueError("Origen y destino no pueden ser iguales")

        if self.stock(product_id, src) < qty:
            raise ValueError(
                f"Stock insuficiente en almacén {src} para transferir {qty}"
            )

        with self.conn:  # transacción atómica
            # salida (almacén origen)
            self.move(product_id, src, -qty, f"{concept} salida")
            # entrada (almacén destino)
            self.move(product_id, dst, +qty, f"{concept} entrada")

    # ───────────────────────────── consultas ────────────────────────────
    def movements(
        self,
        product_id: Optional[int] = None,
    ) -> Sequence[Mapping]:
        """
        Devuelve la lista de movimientos (últimos primero).

        Si `product_id` es None, trae los movimientos de todos los productos.
        """
        cur = self.conn.cursor()
        if product_id is None:
            cur.execute(
                """
                SELECT m.date, p.name, m.qty, m.concept, m.warehouse_id
                  FROM stock_movements m
                  JOIN products p ON p.id = m.product_id
              ORDER BY m.id DESC
                """
            )
        else:
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
        return cur.fetchall()
