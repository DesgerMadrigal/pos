"""
pos.ui.supplier_frame
---------------------
Gestión de proveedores (alta, listado) con un único formulario integral.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ..models.supplier import SupplierDAO


class SupplierFrame(ttk.Frame):
    """Pestaña principal de Proveedores."""

    def __init__(self, parent: tk.Misc, dao: SupplierDAO) -> None:
        super().__init__(parent)
        self.dao = dao
        self._build()
        self._load()

    # ───────────────────────── UI ─────────────────────────
    def _build(self) -> None:
        ttk.Button(
            self,
            text="Nuevo proveedor",
            command=self._open_add_window,
        ).pack(anchor="e", pady=4)

        cols = ("ID", "Cédula", "Nombre", "Teléfono", "Email")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

    # ──────────────────── helpers / datos ─────────────────
    def _load(self) -> None:
        """Actualiza la tabla con los proveedores existentes."""
        self.tree.delete(*self.tree.get_children())
        for r in self.dao.list():
            self.tree.insert(
                "",
                "end",
                values=(
                    r["id"],
                    r["legal_id"],
                    r["name"],
                    r["phone"],
                    r["email"],
                ),
            )

    # ───────────────────────── altas ───────────────────────
    def _open_add_window(self) -> None:
        """Abre una ventana para capturar todos los datos de un nuevo proveedor."""
        AddSupplierWindow(self, self.dao, on_save=self._load)


# ════════════════════════════════════════════════════════════
#  Ventana emergente de alta de proveedor
# ════════════════════════════════════════════════════════════
class AddSupplierWindow(tk.Toplevel):
    """Formulario completo para registrar un proveedor."""

    def __init__(
        self,
        master: SupplierFrame,
        dao: SupplierDAO,
        on_save,
    ) -> None:
        super().__init__(master)
        self.dao, self.on_save = dao, on_save
        self.title("Nuevo proveedor")
        self.resizable(False, False)
        self.geometry("380x270")
        self.columnconfigure(1, weight=1)

        # Campos y validadores
        self.inputs: dict[str, tk.Entry] = {}
        campos = [
            ("legal_id", "Cédula jurídica"),
            ("name", "Nombre*"),
            ("phone", "Teléfono"),
            ("email", "Email"),
            ("bank_info", "Datos bancarios"),
        ]

        for i, (key, label) in enumerate(campos):
            ttk.Label(self, text=label).grid(
                row=i, column=0, sticky="e", padx=6, pady=3
            )
            ent = ttk.Entry(self)
            ent.grid(row=i, column=1, sticky="we", padx=6, pady=3)
            self.inputs[key] = ent

        ttk.Button(self, text="Guardar", command=self._save).grid(
            row=len(campos), columnspan=2, pady=12
        )

        # foco inicial
        self.inputs["name"].focus_set()

    # ───────────────────────── internals ────────────────────
    def _save(self) -> None:
        """Valida y envía los datos a la DAO."""
        d = {k: v.get().strip() for k, v in self.inputs.items()}

        if not d["name"]:
            messagebox.showwarning(
                "Campo obligatorio", "El campo Nombre es obligatorio", parent=self
            )
            return

        try:
            self.dao.add(
                legal_id=d["legal_id"],
                name=d["name"],
                phone=d["phone"],
                email=d["email"],
                bank_info=d["bank_info"],
            )
            messagebox.showinfo(
                "Éxito", "Proveedor registrado correctamente", parent=self
            )
            self.on_save()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)
