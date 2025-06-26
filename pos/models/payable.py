import sqlite3
from typing import Sequence, Mapping

class PayableDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_invoice(self, supplier_id: int, concept: str, amount: float) -> None:
        self.conn.execute("""
            INSERT INTO payables(supplier_id, date, concept, amount)
            VALUES (?, datetime('now','localtime'), ?, ?)
        """, (supplier_id, concept, amount))
        self.conn.commit()

    def pay(self, payable_id: int, amount: float) -> None:
        self.conn.execute("""
            UPDATE payables SET paid = paid + ?
            WHERE id = ? AND paid + ? <= amount
        """, (amount, payable_id, amount))
        self.conn.commit()

    def list(self, pending_only: bool = False) -> Sequence[Mapping]:
        sql = """
            SELECT p.id, s.name AS supplier, p.date, p.concept,
                   p.amount, p.paid, (p.amount - p.paid) AS balance
              FROM payables p JOIN suppliers s ON s.id = p.supplier_id
        """
        if pending_only:
            sql += " WHERE p.amount > p.paid"
        sql += " ORDER BY p.id DESC"
        return self.conn.execute(sql).fetchall()
