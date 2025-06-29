"""
inventory_frame.py
------------------
Inventario multi-almacén: entradas, salidas, traspasos y filtro
«Solo con existencia» para ver rápidamente qué hay en cada almacén.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from ..models.product import ProductDAO
from ..models.inventory import InventoryDAO
from ..models.warehouse import WarehouseDAO


class InventoryFrame(ttk.Frame):
    """Pestaña Inventario con filtro por almacén y movimientos."""

    def __init__(
        self,
        parent: tk.Misc,
        prod_dao: ProductDAO,
        inv_dao: InventoryDAO,
        wh_dao: WarehouseDAO,
    ) -> None:
        super().__init__(parent)
        self.prod_dao, self.inv_dao, self.wh_dao = prod_dao, inv_dao, wh_dao

        self._build()
        self._load()

    # ────────────────────────── UI ──────────────────────────
    def _build(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=4)

        # búsqueda
        self.q = tk.StringVar()
        ent = ttk.Entry(bar, textvariable=self.q, width=30)
        ent.pack(side="left")
        ent.bind("<Return>", lambda _e: self._load())

        # almacén
        ttk.Label(bar, text="Almacén").pack(side="left", padx=(8, 2))
        self.cb_wh = ttk.Combobox(
            bar,
            state="readonly",
            values=[f"{w['id']} - {w['name']}" for w in self.wh_dao.list()],
            width=18,
        )
        self.cb_wh.current(0)
        self.cb_wh.pack(side="left")
        self.cb_wh.bind("<<ComboboxSelected>>", lambda _e: self._load())

        # filtro «solo con existencia»
        self.only_stock = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            bar,
            text="Solo con existencia",
            variable=self.only_stock,
            command=self._load,
        ).pack(side="left", padx=8)

        # botones
        ttk.Button(bar, text="Entrada", command=lambda: self._move(+1)).pack(
            side="right", padx=2
        )
        ttk.Button(bar, text="Salida", command=lambda: self._move(-1)).pack(
            side="right", padx=2
        )
        ttk.Button(bar, text="Traspasar", command=self._transfer).pack(
            side="right", padx=6
        )

        # tabla
        cols = ("ID", "Nombre", "Stock")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

    # ───────────────────────── helpers ──────────────────────
    def _selected_wh(self) -> int:
        return int(self.cb_wh.get().split(" - ")[0])

    # ───────────────────────── datos ────────────────────────
    def _load(self) -> None:
        """Rellena la tabla aplicando filtros."""
        self.tree.delete(*self.tree.get_children())
        wid = self._selected_wh()
        query = self.q.get()
        for r in self.prod_dao.search(query):
            pid, name = r[0], r[2]
            stock = self.inv_dao.stock(pid, warehouse_id=wid)
            if self.only_stock.get() and stock == 0:
                continue
            self.tree.insert("", "end", values=(pid, name, stock))

    # ────────────────── movimientos simples ─────────────────
    def _move(self, sign: int) -> None:
        sel = self.tree.focus()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige un producto")
            return

        pid = int(self.tree.item(sel)["values"][0])
        wid = self._selected_wh()

        try:
            qty = float(
                simpledialog.askstring(
                    "Cantidad", "Cantidad:", parent=self
                )
                or 0
            )
        except ValueError:
            return
        if qty <= 0:
            return

        concept = (
            simpledialog.askstring("Concepto", "Motivo:", parent=self) or ""
        )

        try:
            self.inv_dao.move(pid, wid, sign * qty, concept)
            self._load()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    # ─────────────────────── traspaso ───────────────────────
    def _transfer(self) -> None:
        sel = self.tree.focus()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige un producto")
            return

        pid = int(self.tree.item(sel)["values"][0])
        origen = self._selected_wh()

        # destino
        almacenes = [w for w in self.wh_dao.list() if w["id"] != origen]
        if not almacenes:
            messagebox.showinfo("Almacenes", "No hay otro almacén destino")
            return

        dst_str = simpledialog.askstring(
            "Destino",
            "ID almacén destino "
            f"({', '.join(str(w['id']) for w in almacenes)}):",
            parent=self,
        )
        if not dst_str:
            return
        try:
            destino = int(dst_str)
        except ValueError:
            return
        if destino == origen:
            messagebox.showwarning("Destino", "Destino = origen")
            return

        # cantidad
        try:
            qty = float(
                simpledialog.askstring(
                    "Cantidad", "Cantidad a transferir:", parent=self
                )
                or 0
            )
        except ValueError:
            return
        if qty <= 0:
            return

        try:
            self.inv_dao.transfer(pid, origen, destino, qty)
            self._load()
            messagebox.showinfo(
                "Éxito", f"Trasladadas {qty} u. al almacén {destino}"
            )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
