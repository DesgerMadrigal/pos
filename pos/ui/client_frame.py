# POS/ui/client_frame.py
import tkinter as tk
from tkinter import ttk, messagebox
from ..models.client import ClientDAO

class ClientFrame(ttk.Frame):
    def __init__(self, parent: tk.Misc, dao: ClientDAO):
        super().__init__(parent)
        self.dao = dao
        self._build()
        self._load()

    def _build(self):
        bar = ttk.Frame(self); bar.pack(fill="x", pady=4)
        ttk.Button(bar, text="Nuevo cliente", command=self._open_add).pack(side="right")

        cols = ("ID", "Nombre", "Teléfono", "Email", "Saldo")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.dao.list():
            self.tree.insert("", "end", values=tuple(row))

    # -------- ventana emergente ----------
    def _open_add(self):
        AddClientWindow(self, self.dao, on_save=self._load)

class AddClientWindow(tk.Toplevel):
    def __init__(self, master, dao: ClientDAO, on_save):
        super().__init__(master)
        self.dao, self.on_save = dao, on_save
        self.title("Nuevo cliente"); self.resizable(False, False)
        self.columnconfigure(1, weight=1)

        fields = [("name","Nombre*"),("phone","Teléfono"),
                  ("email","Email"),("address","Dirección"),
                  ("credit_limit","Límite de crédito")]
        self.inp={}
        for i,(k,lbl) in enumerate(fields):
            ttk.Label(self,text=lbl).grid(row=i,column=0,sticky="e",padx=4,pady=2)
            e = ttk.Entry(self); e.grid(row=i,column=1,sticky="we",padx=4); self.inp[k]=e
        ttk.Button(self,text="Guardar",command=self._save).grid(row=len(fields),
                                                                columnspan=2,pady=8)

    def _save(self):
        d={k:v.get() for k,v in self.inp.items()}
        if not d["name"]:
            messagebox.showerror("Falta nombre","El nombre es obligatorio"); return
        try:
            self.dao.add(name=d["name"], phone=d["phone"], email=d["email"],
                         address=d["address"],
                         credit_limit=float(d["credit_limit"] or 0))
            self.on_save(); self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
