import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ..models.warehouse import WarehouseDAO

class WarehouseFrame(ttk.Frame):
    def __init__(self, parent, dao: WarehouseDAO):
        super().__init__(parent); self.dao=dao
        self._build(); self._load()

    def _build(self):
        ttk.Button(self,text="Nuevo almacén",command=self._new).pack(anchor="e",pady=4)
        cols=("ID","Nombre","Ubicación")
        self.tree=ttk.Treeview(self,columns=cols,show="headings")
        for c in cols: self.tree.heading(c,text=c)
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.dao.list():
            self.tree.insert("", "end", values=(r["id"], r["name"], r["location"]))

    def _new(self):
        name=simpledialog.askstring("Nombre","Nombre del almacén:",parent=self)
        loc=simpledialog.askstring("Ubicación","Ubicación:",parent=self)
        if name: self.dao.add(name, loc); self._load()
