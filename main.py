"""
POS System Base
Autor: ChatGPT
Fecha de creación: 2025-06-11
Python: 3.11+
Equipo: Desger POS
Líder: Desger Madrigal
Integrantes: Desger Madrigal, ChatGPT (IA)

Descripción:
Esta base implementa la estructura fundamental de un sistema Punto de Venta
utilizando Tkinter para la interfaz gráfica y SQLite como base de datos local.
Incluye:
  • Inicialización automática de la base de datos y tablas esenciales.
  • Gestión intuitiva de Productos (alta, búsqueda y listado).
  • Estructura modular preparada para añadir Ventas, Caja, Clientes, Inventario,
    Almacenes, Proveedores y Pagos en iteraciones posteriores.

Ejecución:
  $ python pos_base.py
"""

import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

###############################################################################
# Base de Datos                                                               #
###############################################################################

class POSDatabase:
    """Encapsula la conexión y operaciones básicas sobre SQLite."""

    def __init__(self, db_name: str = "pos.db") -> None:
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row  # Resultados como diccionarios
        self._create_tables()

    # --------------------------------------------------------------------- #
    #                                DDL                                   #
    # --------------------------------------------------------------------- #

    def _create_tables(self) -> None:
        cur = self.conn.cursor()

        cur.execute(
            """CREATE TABLE IF NOT EXISTS products (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode      TEXT UNIQUE,
                    name         TEXT NOT NULL,
                    description  TEXT,
                    unit         TEXT DEFAULT 'pz',
                    price        REAL NOT NULL DEFAULT 0,
                    discount     REAL NOT NULL DEFAULT 0, -- porcentaje 0‑100
                    iva          REAL NOT NULL DEFAULT 0, -- porcentaje 0‑100
                    sku          TEXT,
                    stock        INTEGER NOT NULL DEFAULT 0
                )"""
        )

        # Las tablas siguientes quedan creadas pero sin lógica todavía -------
        cur.execute(
            """CREATE TABLE IF NOT EXISTS clients (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL,
                    phone       TEXT,
                    email       TEXT,
                    address     TEXT,
                    credit_limit REAL DEFAULT 0,
                    balance     REAL DEFAULT 0
                )"""
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS sales (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    date       TEXT NOT NULL,
                    client_id  INTEGER,
                    total      REAL NOT NULL,
                    discount   REAL NOT NULL DEFAULT 0,
                    paid       REAL NOT NULL DEFAULT 0,
                    payment_type TEXT,
                    FOREIGN KEY(client_id) REFERENCES clients(id)
                )"""
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS sale_items (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id    INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity   REAL NOT NULL,
                    price      REAL NOT NULL,
                    discount   REAL NOT NULL DEFAULT 0,
                    iva        REAL NOT NULL DEFAULT 0,
                    FOREIGN KEY(sale_id) REFERENCES sales(id),
                    FOREIGN KEY(product_id) REFERENCES products(id)
                )"""
        )

        # Otras tablas: cash_movements, warehouses, stock_movements, suppliers,
        # payables... se crearán más adelante.

        self.conn.commit()

    # --------------------------------------------------------------------- #
    #                           Operaciones CRUD                           #
    # --------------------------------------------------------------------- #

    # Productos ----------------------------------------------------------- #
    def add_product(
        self,
        barcode: str,
        name: str,
        description: str,
        unit: str,
        price: float,
        discount: float,
        iva: float,
        sku: str,
        stock: int,
    ) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO products(
                   barcode, name, description, unit, price,
                   discount, iva, sku, stock)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                barcode,
                name,
                description,
                unit,
                price,
                discount,
                iva,
                sku,
                stock,
            ),
        )
        self.conn.commit()

    def get_products(self, search: str = ""):
        cur = self.conn.cursor()
        if search:
            like = f"%{search}%"
            cur.execute(
                """SELECT id, barcode, name, unit, price, stock
                       FROM products
                      WHERE barcode LIKE ?
                         OR name    LIKE ?
                         OR sku     LIKE ?
                   ORDER BY name""",
                (like, like, like),
            )
        else:
            cur.execute(
                "SELECT id, barcode, name, unit, price, stock FROM products ORDER BY name"
            )
        return cur.fetchall()

###############################################################################
# Interfaz Gráfica                                                            #
###############################################################################

class ProductFrame(ttk.Frame):
    """Frame con el CRUD básico de Productos."""

    def __init__(self, parent: tk.Misc, db: POSDatabase):
        super().__init__(parent)
        self.db = db
        self._build_widgets()
        self._load_products()

    # ------------------------- UI Builders ------------------------------ #
    def _build_widgets(self):
        # Barra superior de búsqueda y botones --------------------------------
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=4)

        self.search_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.search_var, width=30).pack(side="left", padx=4)
        ttk.Button(bar, text="Buscar", command=self._load_products).pack(side="left")
        ttk.Button(bar, text="Agregar Producto", command=self._open_add_window).pack(
            side="right", padx=4
        )

        # Tabla ---------------------------------------------------------------
        cols = ("ID", "Código", "Nombre", "Unidad", "Precio", "Stock")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

    # --------------------------- Helpers -------------------------------- #
    def _load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for prod in self.db.get_products(self.search_var.get()):
            self.tree.insert("", "end", values=prod)

    def _open_add_window(self):
        AddProductWindow(self, self.db, on_save=self._load_products)


class AddProductWindow(tk.Toplevel):
    """Formulario emergente para crear un producto nuevo."""

    def __init__(self, parent: tk.Misc, db: POSDatabase, on_save):
        super().__init__(parent)
        self.db = db
        self.on_save = on_save
        self.title("Agregar Producto")
        self.geometry("420x420")
        self.resizable(False, False)
        self.columnconfigure(1, weight=1)

        # Campos del formulario ----------------------------------------------
        self.inputs = {}
        fields = [
            ("barcode", "Código de barras"),
            ("name", "Nombre"),
            ("description", "Descripción"),
            ("unit", "Unidad"),
            ("price", "Precio"),
            ("discount", "Descuento (%)"),
            ("iva", "IVA (%)"),
            ("sku", "Clave/SKU"),
            ("stock", "Existencia"),
        ]
        for i, (key, label) in enumerate(fields):
            ttk.Label(self, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=4)
            entry = ttk.Entry(self)
            entry.grid(row=i, column=1, sticky="we", padx=5)
            self.inputs[key] = entry

        ttk.Button(self, text="Guardar", command=self._save).grid(
            row=len(fields), columnspan=2, pady=12
        )

    def _save(self):
        try:
            data = {k: v.get() for k, v in self.inputs.items()}
            self.db.add_product(
                barcode=data["barcode"],
                name=data["name"],
                description=data["description"],
                unit=data["unit"] or "pz",
                price=float(data["price"] or 0),
                discount=float(data["discount"] or 0),
                iva=float(data["iva"] or 0),
                sku=data["sku"],
                stock=int(data["stock"] or 0),
            )
            messagebox.showinfo("Éxito", "Producto registrado correctamente")
            self.on_save()
            self.destroy()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"Código o SKU duplicado:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

###############################################################################
# App Principal                                                              #
###############################################################################

class POSApp(tk.Tk):
    """Ventana maestro con pestañas para cada módulo."""

    def __init__(self):
        super().__init__()
        self.title("Sistema Punto de Venta")
        self.geometry("1024x768")
        self.db = POSDatabase()

        self._build_notebook()

    def _build_notebook(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Pestaña Productos ---------------------------------------------------
        nb.add(ProductFrame(nb, self.db), text="Productos")

        # Pestañas vacías como placeholders ----------------------------------
        nb.add(ttk.Frame(nb), text="Ventas")
        nb.add(ttk.Frame(nb), text="Caja")
        nb.add(ttk.Frame(nb), text="Clientes")
        nb.add(ttk.Frame(nb), text="Inventario")
        nb.add(ttk.Frame(nb), text="Almacenes")
        nb.add(ttk.Frame(nb), text="Proveedores")
        nb.add(ttk.Frame(nb), text="Pagos")

###############################################################################
# Main Entrypoint                                                            #
###############################################################################

def main():
    POSApp().mainloop()


if __name__ == "__main__":
    main()
