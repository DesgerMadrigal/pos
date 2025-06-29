# Punto de Venta — Guía de proyecto

Este documento explica **cómo está organizado y cómo funciona** el sistema de punto de venta que acabas de descargar.  Se dirige a estudiantes que están **empezando** con Python y con los conceptos de programación GUI, bases de datos y arquitectura por capas.

---

## 1 · Estructura general del proyecto

```text
pos/                      ← paquete principal
 ├─ __init__.py           ← marca la carpeta como paquete Python
 ├─ app.py                ← crea la ventana principal y todas las pestañas
 ├─ run_pos.py            ← pequeño _launcher_ para iniciar la app
 ├─ db.py                 ← crea / abre la base SQLite y sus tablas
 │
 ├─ models/               ← **capa de acceso a datos (DAO)**
 │   ├─ product.py        ← CRUD de productos
 │   ├─ client.py         ← CRUD de clientes
 │   ├─ sale.py           ← ventas y sus ítems
 │   ├─ inventory.py      ← movimientos y traspasos de inventario
 │   ├─ warehouse.py      ← almacenes físicos
 │   ├─ cash.py           ← cortes y arqueos de caja
 │   ├─ supplier.py       ← proveedores
 │   └─ payable.py        ← cuentas por pagar
 │
 └─ ui/                   ← **capa de interfaz gráfica (Tkinter)**
     ├─ product_frame.py  ← pestaña Productos
     ├─ sale_frame.py     ← pestaña Ventas
     ├─ cash_frame.py     ← pestaña Caja
     ├─ client_frame.py   ← pestaña Clientes
     ├─ inventory_frame.py← pestaña Inventario (entradas, salidas, traspasos)
     ├─ warehouse_frame.py← pestaña Almacenes
     ├─ supplier_frame.py ← pestaña Proveedores
     └─ payable_frame.py  ← pestaña Pagos
```

> **¿Por qué separar en carpetas *models/* y *ui/*?**  
> Para aplicar el patrón **MVC simplificado**: los *modelos* hablan con la base de datos; las *vistas* muestran datos y capturan acciones del usuario.  Esto facilita el mantenimiento y las pruebas.

---

## 2 · ¿Qué es `__init__.py`?

- Es un archivo vacío (o casi) que **convierte la carpeta** en un *paquete Python*.
- Gracias a él podemos importar con `from pos.models.product import ProductDAO` en vez de usar rutas más largas.

---

## 3 · Capa **models/** — Data Access Objects (DAO)

En esta carpeta vive **la lógica de acceso a datos**.  Cada archivo declara una clase que sigue el patrón **DAO** (Data Access Object): un objeto cuyas únicas responsabilidades son **hablar con la base de datos** y **devolver/recibir estructuras Python limpias** (tuplas, listas, diccionarios).

### ¿Por qué usar DAOs?

| Ventaja               | Explicación sencilla                                                                                            |
| --------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Aislamiento**       | El resto de la app nunca escribe SQL directo; si mañana cambiamos SQLite por PostgreSQL, solo tocamos los DAOs. |
| **Reutilización**     | Los mismos métodos (`add`, `list`, `search`) se pueden llamar desde la GUI, scripts de pruebas o servicios web. |
| **Seguridad**         | Cada consulta usa parámetros (`?`) → elimina inyección SQL.                                                     |
| **Transacciones**     | El `with self.conn:` encapsula un bloque atómico; si algo falla, `sqlite3` hace *rollback*.                     |
| **Validación mínima** | El DAO comprueba reglas de negocio básicas: stock suficiente, saldo ≠ negativo, clave única…                    |

### Anatomía de un DAO (`ProductDAO` resumido)

```python
class ProductDAO:
    def __init__(self, conn):
        self.conn = conn             # conexión única a SQLite

    def add(self, **campos):          # C  (Create)
        self.conn.execute(
            """INSERT INTO products(... ) VALUES (...)""",
            (...)
        )
        self.conn.commit()

    def search(self, text=""):        # R  (Read)
        return self.conn.execute(
            "SELECT ... WHERE name LIKE ?", (f"%{text}%",)
        )

    # U y D (Update / Delete) se implementan igual
```

> **Tip didáctico**: un DAO equivale a “el librero” del proyecto: sabe dónde está cada libro (tabla) y trae los que pidas.

---

## 4 · Capa **ui/** — Tkinter Frames (Vistas)

La carpeta `ui/` contiene **las vistas**.  Cada archivo hereda de `ttk.Frame` y actúa como «mini‑pantalla» dentro del `Notebook`.

### Filosofía

1. **Un frame = una pestaña (caso de uso)**. Ej.: `sale_frame.py` = ventas.  
2. **Sin SQL aquí**: el frame solo pide datos al DAO y los muestra.  
3. **Eventos, no acoplamiento**: para hablar entre pestañas usamos eventos virtuales (`<<AddToCart>>`, `<<ClientAdded>>`).  

### Ejemplo rápido de frame

```python
class InventoryFrame(ttk.Frame):
    def __init__(self, parent, prod_dao, inv_dao, wh_dao):
        ...
        self._build_widgets()
        self._load()

    def _build_widgets(self):
        ttk.Combobox(...)
        ttk.Button(text="Entrada", command=lambda: self._move(+1))
        ttk.Button(text="Traspasar", command=self._transfer)

    def _load(self):
        stock = self.inv_dao.stock(pid, warehouse_id=wid)
        self.tree.insert(...)
```

* `_build_widgets()` = dibuja controles.  
* `_load()` = solicita datos al DAO y actualiza la tabla.

---

## 5 · `app.py` — el orquestador

```python
root = POSApp()
root.mainloop()
```

* Conecta a SQLite (`db.get_connection()`).  
* Instancia **todos** los DAOs y los pasa a cada frame (*inyección de dependencias*).  
* Crea un `ttk.Notebook` y agrega las pestañas.

---

## 6 · `run_pos.py` — entry‑point sencillo

```python
from runpy import run_module
run_module('pos.app', run_name='__main__')
```

* Permite iniciar con `python run_pos.py`.  
* Útil al empaquetar con **PyInstaller**.

---

## 7 · Flujo de una venta

1. **Inventario**: stock inicial con `InventoryDAO.move()`.  
2. **Venta**: el carrito pasa a `SaleDAO.create_sale()` → inserta venta + ítems y descuenta stock.  
3. **Caja**: `CashDAO.add()` registra la entrada de dinero.

---

## 8 · Requisitos académicos cubiertos

| Requisito | Dónde se cumple |
|-----------|-----------------|
| Estructuras de control | Bucles y `if` en frames y DAOs |
| Listas, diccionarios, tuplas | `cart` en ventas, tuplas SQL |
| App Python de complejidad media | CRUD + GUI + SQLite |
| Funciones de PV, Caja, Inventario… | Frames + DAOs correspondientes |

---

## 9 · Más recursos

* Regex en Python → <https://docs.python.org/3/howto/regex.html>  
* Reportes en PDF con ReportLab → <https://www.reportlab.com/docs/reportlab-userguide.pdf>  
* Módulo estándar `csv` → <https://docs.python.org/3/library/csv.html>  
* Empaquetar con PyInstaller → <https://pyinstaller.org/en/stable/index.html>
