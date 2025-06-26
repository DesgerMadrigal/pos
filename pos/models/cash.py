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
