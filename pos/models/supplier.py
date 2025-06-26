import sqlite3
from typing import Sequence, Mapping

class SupplierDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, *, legal_id: str, name: str,
            phone: str = "", email: str = "", bank_info: str = ""):
        self.conn.execute("""
            INSERT INTO suppliers(legal_id, name, phone, email, bank_info)
            VALUES (?,?,?,?,?)
        """, (legal_id, name, phone, email, bank_info))
        self.conn.commit()

    def list(self) -> Sequence[Mapping]:
        return self.conn.execute("""
            SELECT id, legal_id, name, phone, email FROM suppliers ORDER BY name
        """).fetchall()
