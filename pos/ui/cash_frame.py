import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ..models.cash import CashDAO

class CashFrame(ttk.Frame):
    def __init__(self, parent, dao: CashDAO):
        super().__init__(parent)
        self.dao = dao
        self._build(); self._load()

    def _build(self):
        bar=ttk.Frame(self); bar.pack(fill="x",pady=4)
        ttk.Button(bar,text="+ Entrada",command=lambda:self._add(1)).pack(side="left")
        ttk.Button(bar,text="- Salida", command=lambda:self._add(-1)).pack(side="left")
        ttk.Button(bar,text="Arqueo", command=self._arqueo).pack(side="left")
        ttk.Button(bar,text="Cerrar turno", command=self._close_shift).pack(side="left")
        self.lbl_total=ttk.Label(bar,text="Total turno: 0.00")
        self.lbl_total.pack(side="right")

        cols=("ID","Fecha","Concepto","Monto")
        self.tree=ttk.Treeview(self,columns=cols,show="headings")
        for c in cols: self.tree.heading(c,text=c)
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.dao.list():
            self.tree.insert("", "end",
                values=(r["id"], r["date"], r["concept"], f"{r['amount']:.2f}"))
        self.lbl_total["text"]=f"Total turno: {self.dao.total_shift():.2f}"

    def _add(self, sign: int):
        concept=simpledialog.askstring("Concepto","Descripción:",parent=self)
        if not concept: return
        try:
            amount=float(simpledialog.askstring("Monto","Monto:",parent=self))
            self.dao.add(concept, sign*amount)
            self._load()
        except Exception as e:
            messagebox.showerror("Error",str(e))

    def _arqueo(self):
        contado = float(simpledialog.askstring("Arqueo",
                "Efectivo contado en caja:", parent=self) or 0)
        diferencia = contado - self.dao.total_shift()
        messagebox.showinfo("Resultado",
            f"Total sistema: {self.dao.total_shift():.2f}\n"
            f"Contado físico: {contado:.2f}\n"
            f"Diferencia: {diferencia:+.2f}")

    def _close_shift(self):
        fname, total = self.dao.close_shift()
        # genera imprimible muy simple
        with open(fname, "w", encoding="utf8") as f:
            f.write("CORTE DE CAJA\n")
            for mov in self.dao.list():
                f.write(f"{mov['date']}  {mov['concept']:<20} {mov['amount']:>8.2f}\n")
            f.write(f"\nTOTAL: {total:.2f}\n")
        messagebox.showinfo("Corte generado", f"Archivo {fname} listo para imprimir")
        self._load()
        
