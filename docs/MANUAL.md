# Manual Completo del Sistema POS

Este documento describe en detalle la estructura del proyecto y el propósito de cada archivo y función.

## Índice
1. [Estructura general](#estructura-general)
2. [Archivos de nivel superior](#archivos-de-nivel-superior)
3. [Módulo `pos`](#modulo-pos)
    - [app.py](#apppy)
    - [db.py](#dbpy)
    - [paquete `models`](#paquete-models)
    - [paquete `ui`](#paquete-ui)
4. [Scripts de arranque](#scripts-de-arranque)

## Estructura general

```
.
├── README.md
├── docs/
│   └── MANUAL.md
├── main.py
├── pos/
│   ├── __init__.py
│   ├── app.py
│   ├── db.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cash.py
│   │   ├── client.py
│   │   ├── inventory.py
│   │   ├── payable.py
│   │   ├── product.py
│   │   ├── sale.py
│   │   ├── supplier.py
│   │   └── warehouse.py
│   └── ui/
│       ├── __init__.py
│       ├── cash_frame.py
│       ├── client_frame.py
│       ├── inventory_frame.py
│       ├── payable_frame.py
│       ├── product_frame.py
│       ├── sale_frame.py
│       ├── supplier_frame.py
│       └── warehouse_frame.py
├── pos.db
└── run_pos.py
```

<a name="archivos-de-nivel-superior"></a>
## Archivos de nivel superior

### `README.md`
Breve descripción del proyecto, requisitos, instrucciones de ejecución y referencias útiles.

### `docs/MANUAL.md`
Este manual detallado.

### `main.py`
Ejemplo de aplicación más extensa con la clase `POSDatabase`, interfaces y lógica de productos. No es utilizado por `run_pos.py` pero sirve como referencia de una implementación más completa.

### `run_pos.py`
Script de arranque que simplemente ejecuta `pos.app` con `run_module`.

<a name="modulo-pos"></a>
## Módulo `pos`

Contiene la lógica principal dividida en submódulos.

<a name="apppy"></a>
### `pos/app.py`
- **`POSApp(tk.Tk)`**: Ventana principal que crea un `Notebook` con pestañas para cada módulo.
  - `__init__`: Inicializa DAOs, configura la ventana y llama a `_build_ui`.
  - `_build_ui`: Construye las pestañas y enlaza cada `Frame` de la carpeta `ui`.
- **`main()`**: Punto de entrada si se ejecuta el módulo directamente.

<a name="dbpy"></a>
### `pos/db.py`
- **`get_connection()`**: Devuelve una conexión a la base de datos SQLite y crea las tablas si no existen.
- **`_create_tables(conn)`** *(privada)*: Ejecuta las sentencias `CREATE TABLE` para todas las entidades del sistema.

<a name="paquete-models"></a>
### Paquete `models`
Contiene los objetos de acceso a datos (DAOs) que encapsulan la lógica de base de datos.

- **`product.py`** — `ProductDAO`
  - `add(...)`: Inserta un nuevo producto.
  - `search(text="")`: Busca por código, nombre o SKU.
  - `barcode_exists(barcode)`: Comprueba si existe un código de barras.

- **`client.py`** — `ClientDAO`
  - `add(...)`: Crea un cliente.
  - `list()`: Devuelve todos los clientes.
  - `get(client_id)`: Obtiene un cliente por ID.
  - `update_balance(client_id, delta)`: Modifica el saldo.

- **`sale.py`** — `SaleDAO`
  - `create_sale(client_id, cart, discount_global=0, paid=0)`: Registra una venta y sus elementos.

- **`cash.py`** — `CashDAO`
  - `add(concept, amount)`: Registra un movimiento de caja (positivo o negativo).
  - `list()`: Lista todos los movimientos.
  - `total_shift()`: Devuelve el total acumulado del turno.

- **`inventory.py`** — `InventoryDAO`
  - `move(product_id, warehouse_id, qty, concept="")`: Registra movimientos de inventario y actualiza el stock.
  - `movements(product_id=None)`: Lista movimientos, filtrando opcionalmente por producto.

- **`warehouse.py`** — `WarehouseDAO`
  - `add(name, location="")`: Crea un nuevo almacén.
  - `list()`: Devuelve todos los almacenes registrados.

- **`supplier.py`** — `SupplierDAO`
  - `add(legal_id, name, phone="", email="", bank_info="")`: Agrega un proveedor.
  - `list()`: Lista proveedores ordenados por nombre.

- **`payable.py`** — `PayableDAO`
  - `add_invoice(supplier_id, concept, amount)`: Registra una factura por pagar.
  - `pay(payable_id, amount)`: Aplica un pago a la factura indicada.
  - `list(pending_only=False)`: Devuelve todas las cuentas o solo las pendientes.

<a name="paquete-ui"></a>
### Paquete `ui`
Contiene los `Frame` de la interfaz. Cada archivo define una ventana o pestaña.

- **`product_frame.py`** — `ProductFrame` y `AddProductWindow`
  - `ProductFrame._build_widgets()`: Crea barra de búsqueda y tabla.
  - `ProductFrame._load()`: Llena la tabla de productos.
  - `ProductFrame._open_add()`: Muestra la ventana para agregar.
  - `AddProductWindow._new_barcode()`: Genera un código único.
  - `AddProductWindow._save()`: Guarda el producto en la base de datos.

- **`client_frame.py`** — `ClientFrame` y `AddClientWindow`
  - `_build()` / `_load()` / `_open_add()`
  - `AddClientWindow._save()`

- **`sale_frame.py`** — `SaleFrame`
  - `_build_widgets()`
  - `_add_by_search()` / `_add_to_cart()` / `_refresh_table()` / `_checkout()`

- **`cash_frame.py`** — `CashFrame`
  - `_build()` / `_load()` / `_add(sign)`

- **`inventory_frame.py`** — `InventoryFrame`
  - `_build()` / `_load()` / `_move(sign)`

- **`warehouse_frame.py`** — `WarehouseFrame`
  - `_build()` / `_load()` / `_new()`

- **`supplier_frame.py`** — `SupplierFrame`
  - `_build()` / `_load()` / `_add()`

- **`payable_frame.py`** — `PayableFrame`
  - `_build()` / `_load()` / `_new()` / `_pay()`

<a name="scripts-de-arranque"></a>
## Scripts de arranque

- **`run_pos.py`**: ejecuta `pos.app.main()` para iniciar la interfaz.

## Ejecución rápida

En la raíz del proyecto:
```bash
python run_pos.py
```
Asegúrese de contar con Python 3.11 o superior y el módulo Tkinter instalado.

