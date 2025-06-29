#product_frame.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from ..models.product import ProductDAO
import random        

class ProductFrame(ttk.Frame):
    def __init__(self, parent: tk.Misc, dao: ProductDAO):
        super().__init__(parent)
        self.dao = dao
        self._build_widgets()
        self._load()

    # ------------------------------------------------------------------ UI
    def _build_widgets(self):
        bar = ttk.Frame(self); bar.pack(fill="x", pady=4)
        self.search_var = tk.StringVar()
        ttk.Entry(bar,textvariable=self.search_var,width=28)\
            .pack(side="left",padx=4)
        ttk.Button(bar,text="Buscar",command=self._load).pack(side="left")
        ttk.Button(bar,text="Agregar Producto",
                   command=self._open_add).pack(side="right",padx=4)

        cols = ("ID","Código","Nombre","Unidad","Precio","Stock")
        self.tree = ttk.Treeview(self,columns=cols,show="headings")
        for c in cols:
            self.tree.heading(c,text=c); self.tree.column(c,anchor="center")
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)
        col_widths = [60, 120, 220, 70, 90, 70]
        for col, w in zip(cols, col_widths):
            self.tree.column(col, width=w, anchor="center")

    # -------------------------------------------------------------- helpers
    def _load(self):
        self.tree.delete(*self.tree.get_children())   # limpia la tabla
        for values in self.dao.search(self.search_var.get()):
            self.tree.insert("", "end", values=values)

    def _open_add(self):
        AddProductWindow(self, self.dao, on_save=self._load)

class AddProductWindow(tk.Toplevel):
    def __init__(self, master, dao: ProductDAO, on_save):
        super().__init__(master)
        self.dao, self.on_save = dao, on_save
        self.title("Agregar Producto")
        self.geometry("420x420")
        self.resizable(False, False)
        self.columnconfigure(1, weight=1)

        # ---------------- VALIDADORES -----------------
        # solo dígitos enteros
        v_int   = (self.register(lambda P: P == "" or P.isdigit()), "%P")
        # números decimales: 123 o 123.45
        v_float = (self.register(
            lambda P: P == "" or (P.replace(".", "", 1).isdigit() and P.count(".") <= 1)
        ), "%P")

        self.inputs = {}
        fields = [
            ("barcode",  "Código de barras",  None),      # se autogenera
            ("name",     "Nombre",            None),
            ("description","Descripción",     None),
            ("unit",     "Unidad",            None),
            ("price",    "Precio",            v_float),
            ("discount", "Descuento (%)",     v_float),
            ("iva",      "IVA (%)",           v_float),
            ("sku",      "Clave/SKU",         None),
            ("stock",    "Existencia",        v_int),
        ]

        for i, (key, label, vcmd) in enumerate(fields):
            ttk.Label(self, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=3)
            ent = ttk.Entry(self, validate="key", validatecommand=vcmd) if vcmd else ttk.Entry(self)
            ent.grid(row=i, column=1, sticky="we", padx=5)
            self.inputs[key] = ent

        # ---- Autogenera el código de barras ----
        barcode = self._new_barcode()
        self.inputs["barcode"].insert(0, barcode)
        self.inputs["barcode"]["state"] = "readonly"  # evita edición

        ttk.Button(self, text="Guardar", command=self._save)\
            .grid(row=len(fields), columnspan=2, pady=10)

    # ------------------------------------------------
    def _new_barcode(self) -> str:
        """Genera un EAN-13 aleatorio y garantiza unicidad contra la BD."""
        while True:
            code = "".join(random.choices("0123456789", k=13))
            if not hasattr(self.dao, "barcode_exists") or not self.dao.barcode_exists(code):
                return code

    def _save(self):
        try:
            d = {k: v.get() for k, v in self.inputs.items()}
            self.dao.add(barcode=d["barcode"], name=d["name"],
                         description=d["description"],
                         unit=d["unit"] or "pz",
                         price=float(d["price"] or 0),
                         discount=float(d["discount"] or 0),
                         iva=float(d["iva"] or 0),
                         sku=d["sku"], stock=int(d["stock"] or 0))
            messagebox.showinfo("Éxito", "Producto registrado")
            self.on_save(); self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
