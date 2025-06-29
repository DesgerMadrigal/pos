import sqlite3
from typing import Sequence, Mapping

class CashDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, concept: str, amount: float) -> None:
        self.conn.execute(
            "INSERT INTO cash_movements(date, concept, amount) VALUES "
            "(datetime('now','localtime'), ?, ?)",
            (concept, amount))
        self.conn.commit()

    def list(self) -> Sequence[Mapping]:
        return self.conn.execute(
            "SELECT id, date, concept, amount FROM cash_movements ORDER BY id DESC"
        ).fetchall()

    def total_shift(self) -> float:
        row = self.conn.execute("SELECT COALESCE(SUM(amount),0) AS t FROM cash_movements").fetchone()
        return row["t"]

    def current_shift_id(self) -> int:
        return self.conn.execute(
            "SELECT id FROM cash_shifts WHERE closed IS NULL"
        ).fetchone()["id"]

    def open_shift(self, opening_amount: float = 0) -> int:
        with self.conn:
            self.conn.execute("""
                INSERT INTO cash_shifts(opened, opening_amount)
                VALUES (datetime('now','localtime'), ?)
            """, (opening_amount,))
        return self.current_shift_id()

    def close_shift(self) -> tuple[str, float]:
        sid = self.current_shift_id()
        total = self.total_shift()
        with self.conn:
            self.conn.execute("""
                UPDATE cash_shifts SET closed = datetime('now','localtime')
                WHERE id = ?
            """, (sid,))
        return (f"shift_{sid}_{int(total)}.txt", total)
