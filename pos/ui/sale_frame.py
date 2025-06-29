"""
sale_frame.py
-------------
Módulo de ventas: permite buscar/añadir productos, recibir artículos
desde la pestaña Productos (evento <<AddToCart>>), seleccionar cliente,
cobrar y registrar la venta.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from ..models.product import ProductDAO
from ..models.client import ClientDAO
from ..models.sale import SaleDAO


class SaleFrame(ttk.Frame):
    """Pestaña «Ventas» con carrito y proceso de cobro."""

    def __init__(
        self,
        parent: tk.Misc,
        prod_dao: ProductDAO,
        client_dao: ClientDAO,
        sale_dao: SaleDAO,
    ) -> None:
        super().__init__(parent)
        self.prod_dao, self.client_dao, self.sale_dao = (
            prod_dao,
            client_dao,
            sale_dao,
        )
        self.cart: list[dict] = []  # lista de ítems del carrito
        self._build_widgets()

    # ───────────────────── datos auxiliares ─────────────────────
    def _load_clients(self) -> None:
        """Consulta la BD y actualiza el combobox de clientes."""
        self.cb_client["values"] = [
            f"{c['id']} - {c['name']}" for c in self.client_dao.list()
        ]
        if self.cb_client["values"]:
            self.cb_client.current(0)

    # ────────────────────────── UI ──────────────────────────────
    def _build_widgets(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x", pady=4)

        # caja de búsqueda de productos
        self.q_search = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.q_search, width=40)
        ent.pack(side="left", padx=4)
        ent.bind("<Return>", self._add_by_search)

        # selector de cliente
        ttk.Label(top, text="Cliente").pack(side="left", padx=6)
        self.cb_client = ttk.Combobox(top, state="readonly")
        self.cb_client.pack(side="left")
        self._load_clients()

        # botón manual de refresco de clientes
        ttk.Button(top, text="Refrescar", command=self._load_clients).pack(
            side="left", padx=4
        )

        # escucha eventos globales
        self.winfo_toplevel().bind(
            "<<ClientAdded>>", lambda e: self._load_clients(), add="+"
        )
        self.winfo_toplevel().bind(
            "<<AddToCart>>", self._on_add_product, add="+"
        )

        # botón COBRAR
        ttk.Button(top, text="Cobrar", command=self._checkout).pack(
            side="right", padx=4
        )

        # tabla del carrito
        cols = ("ID", "Nombre", "Cant", "Precio", "Subtotal")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        # total
        bottom = ttk.Frame(self)
        bottom.pack(fill="x")
        self.lbl_total = ttk.Label(
            bottom, text="Total: 0.00", font=("Helvetica", 12, "bold")
        )
        self.lbl_total.pack(side="right", padx=8, pady=4)

    # ──────────────────── lógica de carrito ────────────────────
    def _add_by_search(self, _event=None) -> None:
        """Añade el primer producto que coincida con la búsqueda al carrito."""
        text = self.q_search.get().strip()
        if not text:
            return
        prod = next(iter(self.prod_dao.search(text)), None)
        if not prod:
            messagebox.showwarning("Sin resultados", "Producto no encontrado")
            return
        self._add_to_cart(prod)
        self.q_search.set("")

    def _on_add_product(self, _event=None) -> None:
        """
        Manejador del evento global <<AddToCart>>.
        El ID del producto está en root._product_to_add.
        """
        pid = getattr(self.winfo_toplevel(), "_product_to_add", None)
        if pid is None:
            return

        prod = next(
            (r for r in self.prod_dao.search(str(pid)) if r[0] == pid), None
        )
        if prod:
            self._add_to_cart(prod)


    def _add_to_cart(self, prod_row) -> None:
        """Añade el producto (tupla) al carrito, respetando el stock."""
        pid = prod_row[0]  # id
        # si ya existe en carrito, incrementa qty
        for item in self.cart:
            if item["product_id"] == pid:
                if item["qty"] + 1 > prod_row[5]:
                    messagebox.showwarning("Stock", "Sin stock suficiente")
                    return
                item["qty"] += 1
                break
        else:
            # nuevo item
            if prod_row[5] < 1:
                messagebox.showwarning("Stock", "Sin stock disponible")
                return
            self.cart.append(
                {
                    "product_id": pid,
                    "name": prod_row[2],
                    "qty": 1,
                    "price": prod_row[4],
                }
            )
        self._refresh_table()

    def _refresh_table(self) -> None:
        """Redibuja la tabla del carrito y su total."""
        self.tree.delete(*self.tree.get_children())
        total = 0.0
        for it in self.cart:
            subtotal = it["price"] * it["qty"]
            total += subtotal
            self.tree.insert(
                "",
                "end",
                values=(
                    it["product_id"],
                    it["name"],
                    it["qty"],
                    f"{it['price']:.2f}",
                    f"{subtotal:.2f}",
                ),
            )
        self.lbl_total["text"] = f"Total: {total:.2f}"

    # ───────────────────── proceso de cobro ────────────────────
    def _checkout(self) -> None:
        """Registra la venta si el carrito no está vacío."""
        if not self.cart:
            messagebox.showinfo("Carrito vacío", "Agrega productos primero")
            return

        total = float(self.lbl_total["text"].split(":")[1])
        paid = float(
            simpledialog.askstring(
                "Pago",
                f"Total {total:.2f}\nMonto pagado (0 = crédito):",
                parent=self,
            )
            or 0
        )

        client_id = (
            int(self.cb_client.get().split(" - ")[0]) if self.cb_client.get() else None
        )

        try:
            self.sale_dao.create_sale(
                client_id=client_id,
                cart=self.cart,
                discount_global=0,
                paid=paid,
            )
            messagebox.showinfo("Éxito", "Venta registrada")
            self.cart.clear()
            self._refresh_table()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
