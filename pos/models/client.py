# POS/models/client.py
import sqlite3
from typing import Sequence, Mapping

class ClientDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---------- CRUD básico -------------
    def add(self, *, name: str, phone: str = "", email: str = "",
            address: str = "", credit_limit: float = 0) -> None:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO clients(name, phone, email, address, credit_limit)
            VALUES (?,?,?,?,?)
        """, (name, phone, email, address, credit_limit))
        self.conn.commit()

    def list(self) -> Sequence[Mapping]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, phone, email, balance FROM clients ORDER BY name")
        return cur.fetchall()

    def get(self, client_id: int) -> Mapping | None:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
        return cur.fetchone()

    def update_balance(self, client_id: int, delta: float) -> None:
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE clients SET balance = balance + ? WHERE id=?
        """, (delta, client_id))
        self.conn.commit()
