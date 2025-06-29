# Sistema Punto de Venta (POS)

Este proyecto implementa una base para un sistema Punto de Venta utilizando
Python y SQLite. La interfaz gráfica está construida con **Tkinter** y cuenta
con módulos para gestionar productos, ventas, caja, clientes, inventario,
almacenes, proveedores y pagos. Todas las tablas necesarias se crean de forma
automática en `pos.db` al ejecutar la aplicación.

## Requisitos

- Python 3.11 o superior
- Tkinter (normalmente incluido con Python)

## Ejecución

1. Sitúese en la raíz del proyecto.
2. Ejecute:
   ```bash
   python run_pos.py
   ```
  Esto iniciará la interfaz gráfica del sistema.

## Referencias

- [Documentación oficial de Tkinter](https://docs.python.org/3/library/tkinter.html)
- [Documentación oficial de sqlite3](https://docs.python.org/3/library/sqlite3.html)

Para una descripción completa de cada módulo y función consulte el manual en
[docs/MANUAL.md](docs/MANUAL.md).
