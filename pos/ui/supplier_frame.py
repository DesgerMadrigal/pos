import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ..models.supplier import SupplierDAO

class SupplierFrame(ttk.Frame):
    def __init__(self, parent, dao: SupplierDAO):
        super().__init__(parent); self.dao=dao
        self._build(); self._load()

    def _build(self):
        ttk.Button(self,text="Nuevo proveedor",command=self._add).pack(anchor="e",pady=4)
        cols=("ID","Cédula","Nombre","Teléfono","Email")
        self.tree=ttk.Treeview(self,columns=cols,show="headings")
        for c in cols: self.tree.heading(c,text=c)
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.dao.list():
            self.tree.insert("", "end",
                values=(r["id"], r["legal_id"], r["name"], r["phone"], r["email"]))

    def _add(self):
        datos={}
        for lbl in ("Cédula jurídica","Nombre","Teléfono","Email","Datos bancarios"):
            datos[lbl]=simpledialog.askstring("Proveedor",lbl+":",parent=self) or ""
        if not datos["Nombre"]: return
        self.dao.add(legal_id=datos["Cédula jurídica"], name=datos["Nombre"],
                     phone=datos["Teléfono"], email=datos["Email"],
                     bank_info=datos["Datos bancarios"])
        self._load()
