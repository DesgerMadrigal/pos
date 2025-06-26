import sqlite3
from typing import Sequence, Mapping

class WarehouseDAO:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, name: str, location: str = "") -> None:
        self.conn.execute("INSERT INTO warehouses(name, location) VALUES (?,?)",
                          (name, location))
        self.conn.commit()

    def list(self) -> Sequence[Mapping]:
        return self.conn.execute("SELECT id, name, location FROM warehouses").fetchall()
