import tkinter as tk
from tkinter import ttk
from .db import get_connection
from .models.product import ProductDAO
from .ui.product_frame import ProductFrame
from .models.product import ProductDAO
from .models.client  import ClientDAO
from .models.sale    import SaleDAO
from .ui.product_frame import ProductFrame
from .ui.client_frame  import ClientFrame
from .ui.sale_frame    import SaleFrame
from .models.cash       import CashDAO
from .models.inventory  import InventoryDAO
from .models.warehouse  import WarehouseDAO
from .models.supplier   import SupplierDAO
from .models.payable    import PayableDAO


from .ui.cash_frame      import CashFrame
from .ui.inventory_frame import InventoryFrame
from .ui.warehouse_frame import WarehouseFrame
from .ui.supplier_frame  import SupplierFrame
from .ui.payable_frame   import PayableFrame

class POSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Punto de Venta"); self.geometry("1024x768")

        conn = get_connection()

        # DAOs existentes
        self.dao_product = ProductDAO(conn)
        self.dao_client  = ClientDAO(conn)
        self.dao_sale    = SaleDAO(conn)

        # Nuevos DAOs
        self.dao_cash      = CashDAO(conn)
        self.dao_inventory = InventoryDAO(conn)
        self.dao_warehouse = WarehouseDAO(conn)
        self.dao_supplier  = SupplierDAO(conn)
        self.dao_payable   = PayableDAO(conn)

        self._build_ui()

    def _build_ui(self):
        nb = ttk.Notebook(self); nb.pack(fill="both",expand=True)
        nb.add(ProductFrame(nb, self.dao_product), text="Productos")
        nb.add(SaleFrame(nb, self.dao_product, self.dao_client, self.dao_sale),
               text="Ventas")
        nb.add(CashFrame(nb, self.dao_cash), text="Caja")
        nb.add(ClientFrame(nb, self.dao_client), text="Clientes")
        nb.add(InventoryFrame(nb,self.dao_product,self.dao_inventory,self.dao_warehouse),text="Inventario")
        nb.add(WarehouseFrame(nb, self.dao_warehouse), text="Almacenes")
        nb.add(SupplierFrame(nb, self.dao_supplier), text="Proveedores")
        nb.add(PayableFrame(nb, self.dao_payable, self.dao_supplier), text="Pagos")

def main():
    POSApp().mainloop()

if __name__ == "__main__":
    main()
