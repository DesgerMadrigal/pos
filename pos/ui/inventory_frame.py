import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ..models.product import ProductDAO
from ..models.inventory import InventoryDAO

class InventoryFrame(ttk.Frame):
    def __init__(self, parent, prod_dao: ProductDAO, inv_dao: InventoryDAO):
        super().__init__(parent); self.prod_dao, self.inv_dao = prod_dao, inv_dao
        self._build(); self._load()

    def _build(self):
        bar=ttk.Frame(self); bar.pack(fill="x",pady=4)
        self.q=tk.StringVar()
        ent=ttk.Entry(bar,textvariable=self.q,width=30); ent.pack(side="left")
        ent.bind("<Return>", lambda e:self._load())
        ttk.Button(bar,text="Entrada", command=lambda:self._move(1)).pack(side="right")
        ttk.Button(bar,text="Salida",  command=lambda:self._move(-1)).pack(side="right")

        cols=("ID","Nombre","Stock")
        self.tree=ttk.Treeview(self,columns=cols,show="headings")
        for c in cols: self.tree.heading(c,text=c)
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.prod_dao.search(self.q.get()):
            self.tree.insert("", "end",
                values=(r[0], r[2], r[5]))   # id, name, stock

    def _move(self, sign:int):
        sel=self.tree.focus()
        if not sel:
            messagebox.showinfo("Selecciona","Elige un producto"); return
        pid=int(self.tree.item(sel)["values"][0])
        qty=float(simpledialog.askstring("Cantidad","Cantidad:",parent=self) or 0)
        concept=simpledialog.askstring("Concepto","Motivo:",parent=self) or ""
        if qty<=0: return
        try:
            self.inv_dao.move(pid, warehouse_id=1, qty=sign*qty, concept=concept)
            self._load()
        except Exception as e:
            messagebox.showerror("Error",str(e))
