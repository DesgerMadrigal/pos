# POS/ui/sale_frame.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from ..models.product import ProductDAO
from ..models.client import ClientDAO
from ..models.sale import SaleDAO

class SaleFrame(ttk.Frame):
    def __init__(self, parent: tk.Misc,
                 prod_dao: ProductDAO, client_dao: ClientDAO, sale_dao: SaleDAO):
        super().__init__(parent)
        self.prod_dao, self.client_dao, self.sale_dao = prod_dao, client_dao, sale_dao
        self.cart = []      # ← lista de dicts
        self._build_widgets()

    # ------------------ UI ------------------
    def _build_widgets(self):
        top = ttk.Frame(self); top.pack(fill="x", pady=4)
        self.q_search = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.q_search, width=40)
        ent.pack(side="left", padx=4); ent.bind("<Return>", self._add_by_search)
        ttk.Label(top, text="Cliente").pack(side="left", padx=6)
        self.cb_client = ttk.Combobox(top, state="readonly",
            values=[f"{c['id']} - {c['name']}" for c in self.client_dao.list()])
        self.cb_client.pack(side="left")
        ttk.Button(top, text="Cobrar", command=self._checkout).pack(side="right", padx=4)

        cols=("ID","Nombre","Cant","Precio","Subtotal")
        self.tree=ttk.Treeview(self,columns=cols,show="headings",height=12)
        for c in cols: self.tree.heading(c,text=c); self.tree.column(c,anchor="center")
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)

        # totales
        bottom = ttk.Frame(self); bottom.pack(fill="x")
        self.lbl_total = ttk.Label(bottom, text="Total: 0.00", font=("Helvetica", 12, "bold"))
        self.lbl_total.pack(side="right", padx=8, pady=4)

    # ------------- lógica --------------
    def _add_by_search(self, event=None):
        text=self.q_search.get().strip()
        if not text: return
        # busca el primer match
        prod = next(iter(self.prod_dao.search(text)), None)
        if not prod:
            messagebox.showwarning("Sin resultados","Producto no encontrado"); return
        self._add_to_cart(prod)
        self.q_search.set("")

    def _add_to_cart(self, prod_row):
        # row = (id, barcode, name, unit, price, stock)
        pid = prod_row[0]
        for item in self.cart:
            if item["product_id"]==pid:
                if item["qty"]+1 > prod_row[5]:
                    messagebox.showwarning("Stock","Sin stock suficiente"); return
                item["qty"]+=1; break
        else:
            if prod_row[5] < 1:
                messagebox.showwarning("Stock","Sin stock disponible"); return
            self.cart.append(dict(product_id=pid, name=prod_row[2],
                                  qty=1, price=prod_row[4]))
        self._refresh_table()

    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        total=0
        for it in self.cart:
            subtotal = it["price"]*it["qty"]
            total += subtotal
            self.tree.insert("", "end",
                values=(it["product_id"], it["name"], it["qty"],
                        f"{it['price']:.2f}", f"{subtotal:.2f}"))
        self.lbl_total["text"]=f"Total: {total:.2f}"

    def _checkout(self):
        if not self.cart:
            messagebox.showinfo("Carrito vacío","Agrega productos primero"); return
        total=float(self.lbl_total["text"].split(":")[1])
        paid = float(simpledialog.askstring("Pago",
                     f"Total {total:.2f}\nMonto pagado (0 = crédito):",
                     parent=self) or 0)
        client_id = None
        if self.cb_client.get():
            client_id = int(self.cb_client.get().split(" - ")[0])
        try:
            self.sale_dao.create_sale(client_id=client_id,
                                      cart=self.cart,
                                      discount_global=0,
                                      paid=paid)
            messagebox.showinfo("Éxito","Venta registrada")
            self.cart.clear(); self._refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))
