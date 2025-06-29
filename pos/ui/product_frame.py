"""
product_frame.py
----------------
Gestión de productos: búsqueda, alta y envío de un producto seleccionado
al carrito de la pestaña Ventas mediante el evento virtual <<AddToCart>>.
"""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk, messagebox

from ..models.product import ProductDAO


class ProductFrame(ttk.Frame):
    """Pestaña «Productos» con lista, búsqueda y alta de artículos."""

    def __init__(self, parent: tk.Misc, dao: ProductDAO) -> None:
        super().__init__(parent)
        self.dao = dao
        self._build_widgets()
        self._load()

    # ────────────────────────── UI ──────────────────────────
    def _build_widgets(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=4)

        # búsqueda rápida
        self.search_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.search_var, width=28).pack(
            side="left", padx=4
        )
        ttk.Button(bar, text="Buscar", command=self._load).pack(side="left")

        # ── botones de acción (derecha) ──────────────────────
        ttk.Button(
            bar, text="Añadir a carrito", command=self._send_to_cart
        ).pack(side="right", padx=4)
        ttk.Button(
            bar, text="Agregar Producto", command=self._open_add
        ).pack(side="right")

        # tabla
        cols = ("ID", "Código", "Nombre", "Unidad", "Precio", "Stock")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        # anchuras de columna
        for col, w in zip(cols, (60, 120, 220, 70, 90, 70)):
            self.tree.column(col, width=w, anchor="center")

    # ────────────────────── datos / helpers ─────────────────
    def _load(self) -> None:
        """Recarga la tabla aplicando el filtro de búsqueda."""
        self.tree.delete(*self.tree.get_children())
        for row in self.dao.search(self.search_var.get()):
            self.tree.insert("", "end", values=row)

    def _send_to_cart(self) -> None:
        """Envía el producto seleccionado al carrito (evento global)."""
        sel = self.tree.focus()
        if not sel:
            messagebox.showinfo("Selecciona", "Elige un producto primero")
            return

        product_id = int(self.tree.item(sel)["values"][0])

        root = self.winfo_toplevel()           # ventana raíz (Tk)
        root._product_to_add = product_id      # ← atributo temporal
        root.event_generate("<<AddToCart>>", when="tail")

    def _open_add(self) -> None:
        """Abre la ventana emergente para crear un nuevo producto."""
        AddProductWindow(self, self.dao, on_save=self._load)


# ════════════════════════════════════════════════════════════
#  Ventana emergente de alta de producto
# ════════════════════════════════════════════════════════════
class AddProductWindow(tk.Toplevel):
    """Formulario completo para registrar un producto."""

    def __init__(
        self,
        master: ProductFrame,
        dao: ProductDAO,
        on_save,
    ) -> None:
        super().__init__(master)
        self.dao, self.on_save = dao, on_save
        self.title("Agregar Producto")
        self.geometry("420x420")
        self.resizable(False, False)
        self.columnconfigure(1, weight=1)

        # ── validadores ─────────────────────────────────────
        v_int = (self.register(lambda P: P == "" or P.isdigit()), "%P")
        v_float = (
            self.register(
                lambda P: P == ""
                or (P.replace(".", "", 1).isdigit() and P.count(".") <= 1)
            ),
            "%P",
        )

        # campos de entrada
        self.inputs: dict[str, tk.Entry] = {}
        campos = [
            ("barcode", "Código de barras", None),  # se autogenera
            ("name", "Nombre", None),
            ("description", "Descripción", None),
            ("unit", "Unidad", None),
            ("price", "Precio", v_float),
            ("discount", "Descuento (%)", v_float),
            ("iva", "IVA (%)", v_float),
            ("sku", "Clave/SKU", None),  # se autogenera
            ("stock", "Existencia", v_int),
        ]

        for i, (key, lbl, vcmd) in enumerate(campos):
            ttk.Label(self, text=lbl).grid(
                row=i, column=0, sticky="e", padx=5, pady=3
            )
            ent = (
                ttk.Entry(self, validate="key", validatecommand=vcmd)
                if vcmd
                else ttk.Entry(self)
            )
            ent.grid(row=i, column=1, sticky="we", padx=5)
            self.inputs[key] = ent

        # autogenerar código de barras y SKU
        self._init_auto_codes()

        ttk.Button(self, text="Guardar", command=self._save).grid(
            row=len(campos), columnspan=2, pady=10
        )

    # ─────────────────── auxiliares ────────────────────
    def _init_auto_codes(self) -> None:
        """Genera barcode y SKU únicos y los coloca en los campos."""
        # EAN-13
        barcode = self._new_barcode()
        self.inputs["barcode"].insert(0, barcode)
        self.inputs["barcode"]["state"] = "readonly"

        # SKU
        sku = self._new_sku()
        self.inputs["sku"].insert(0, sku)
        self.inputs["sku"]["state"] = "readonly"

    def _new_barcode(self) -> str:
        """Devuelve un EAN-13 único en la BD."""
        while True:
            code = "".join(random.choices("0123456789", k=13))
            if not self.dao.barcode_exists(code):
                return code

    def _new_sku(self) -> str:
        """Devuelve un SKU alfanumérico (8 car.) único en la BD."""
        chars = "ABCDEFGHJKLMNPQRTUVWXYZ23456789"
        while True:
            code = "".join(random.choices(chars, k=8))
            if not self.dao.sku_exists(code):
                return code

    # ───────────────────────── guardar ─────────────────────────
    def _save(self) -> None:
        """Valida datos, crea el producto y registra stock inicial."""
        try:
            d = {k: v.get() for k, v in self.inputs.items()}
            stock_qty = int(d["stock"] or 0)

            # 1) crea el producto con stock 0
            pid = self.dao.add(
                barcode=d["barcode"],
                name=d["name"],
                description=d["description"],
                unit=d["unit"] or "pz",
                price=float(d["price"] or 0),
                discount=float(d["discount"] or 0),
                iva=float(d["iva"] or 0),
                sku=d["sku"],
                stock=0,
            )

            # 2) registra el inventario inicial en almacén 1
            if stock_qty > 0:
                from ..models.inventory import InventoryDAO

                InventoryDAO(self.dao.conn).move(
                    product_id=pid,
                    warehouse_id=1,
                    qty=stock_qty,
                    concept="Alta inicial",
                )

            messagebox.showinfo("Éxito", "Producto registrado")
            self.on_save()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
