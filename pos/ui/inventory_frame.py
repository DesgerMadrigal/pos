import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from ..models.product import ProductDAO
from ..models.inventory import InventoryDAO
from ..models.warehouse import WarehouseDAO


class InventoryFrame(ttk.Frame):
    """Vista de inventario con control de movimientos y traspasos."""

    def __init__(
        self,
        parent,
        prod_dao: ProductDAO,
        inv_dao: InventoryDAO,
        wh_dao: WarehouseDAO,
    ):
        super().__init__(parent)
        self.prod_dao, self.inv_dao, self.wh_dao = prod_dao, inv_dao, wh_dao

        self._build()
        self._load()

    # ───────────────────────── UI ─────────────────────────
    def _build(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=4)

        # búsqueda
        self.q = tk.StringVar()
        ent = ttk.Entry(bar, textvariable=self.q, width=30)
        ent.pack(side="left")
        ent.bind("<Return>", lambda e: self._load())

        # selección de almacén
        ttk.Label(bar, text="Almacén").pack(side="left", padx=(8, 2))
        self.cb_wh = ttk.Combobox(
            bar,
            state="readonly",
            values=[f"{w['id']} - {w['name']}" for w in self.wh_dao.list()],
            width=18,
        )
        self.cb_wh.current(0)
        self.cb_wh.pack(side="left")
        self.cb_wh.bind("<<ComboboxSelected>>", lambda e: self._load())

        # botones de movimiento
        ttk.Button(bar, text="Entrada", command=lambda: self._move(+1)).pack(
            side="right", padx=2
        )
        ttk.Button(bar, text="Salida", command=lambda: self._move(-1)).pack(
            side="right"
        )

        # tabla
        cols = ("ID", "Nombre", "Stock")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

    # ─────────────────────── helpers ──────────────────────
    def _selected_wh(self) -> int:
        """Devuelve el ID del almacén seleccionado en el combobox."""
        return int(self.cb_wh.get().split(" - ")[0])

    # ───────────────────────── datos ──────────────────────
    def _load(self) -> None:
        """Rellena la tabla con el stock del almacén actual o búsqueda."""
        self.tree.delete(*self.tree.get_children())
        wid = self._selected_wh()
        query = self.q.get()
        for r in self.prod_dao.search(query):
            pid, name = r[0], r[2]
            stock = self.inv_dao.stock(pid, warehouse_id=wid)
            self.tree.insert("", "end", values=(pid, name, stock))

    def _move(self, sign: int) -> None:
        """Entrada (+1) o salida (-1) de inventario para el producto seleccionado."""
        sel = self.tree.focus()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige un producto")
            return

        pid = int(self.tree.item(sel)["values"][0])
        wid = self._selected_wh()

        try:
            qty = float(
                simpledialog.askstring("Cantidad", "Cantidad:", parent=self) or 0
            )
        except ValueError:
            return
        if qty <= 0:
            return

        concept = (
            simpledialog.askstring("Concepto", "Motivo:", parent=self) or ""
        )

        try:
            self.inv_dao.move(
                product_id=pid,
                warehouse_id=wid,
                qty=sign * qty,
                concept=concept,
            )
            self._load()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
