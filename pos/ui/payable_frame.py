import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ..models.payable import PayableDAO
from ..models.supplier import SupplierDAO

class PayableFrame(ttk.Frame):
    def __init__(self, parent, dao: PayableDAO, sup_dao: SupplierDAO):
        super().__init__(parent); self.dao, self.sup_dao = dao, sup_dao
        self._build(); self._load()

    def _build(self):
        bar=ttk.Frame(self); bar.pack(fill="x",pady=4)
        ttk.Button(bar,text="Nueva factura",command=self._new).pack(side="left")
        ttk.Button(bar,text="Registrar pago",command=self._pay).pack(side="left")

        cols=("ID","Proveedor","Fecha","Concepto","Monto","Pagado","Saldo")
        self.tree=ttk.Treeview(self,columns=cols,show="headings")
        for c in cols: self.tree.heading(c,text=c)
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.dao.list():
            self.tree.insert("","end",
                values=(r["id"], r["supplier"], r["date"], r["concept"],
                        f"{r['amount']:.2f}", f"{r['paid']:.2f}",
                        f"{r['balance']:.2f}"))

    def _new(self):
        sups=self.sup_dao.list()
        if not sups:
            messagebox.showinfo("Sin proveedores","Crea un proveedor primero"); return
        sup_sel=simpledialog.askinteger("Proveedor",
                    "ID proveedor:\n"+"\n".join(f"{s['id']} - {s['name']}" for s in sups),
                    parent=self)
        concept=simpledialog.askstring("Concepto","Descripción:",parent=self)
        amount=float(simpledialog.askstring("Monto","Monto:",parent=self) or 0)
        self.dao.add_invoice(sup_sel, concept, amount); self._load()

    def _pay(self):
        sel=self.tree.focus()
        if not sel: return
        pid=int(self.tree.item(sel)["values"][0])
        amt=float(simpledialog.askstring("Pago","Monto a pagar:",parent=self) or 0)
        self.dao.pay(pid, amt); self._load()
