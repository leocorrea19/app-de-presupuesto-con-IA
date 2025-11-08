import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox
import database 
import datetime
# -------------------------------------------------------------------
# CLASE: FormularioIngreso (¡MODIFICADA PARA EDICIÓN!)
# -------------------------------------------------------------------
class FormularioIngreso(ttk.Toplevel):
    def __init__(self, parent, transaccion_id=None):
        
        self.parent = parent
        self.transaccion_id = transaccion_id # Guardar el ID
        
        # Título dinámico
        title = "Editar Ingreso" if self.transaccion_id else "Cargar Nuevo Ingreso"
        
        super().__init__(master=parent, title=title)
        
        self.geometry("450x350"); self.place_window_center(); self.resizable(False, False)
        
        frame = ttk.Frame(self, padding=20); frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(frame, text="Detalle:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=10, sticky=W)
        self.detalle_entry = ttk.Entry(frame, width=30); self.detalle_entry.grid(row=0, column=1, padx=5, pady=10); self.detalle_entry.focus_set()
        
        ttk.Label(frame, text="Categoría:", font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=10, sticky=W)
        categorias_ingreso = database.obtener_categorias('ingreso') 
        self.categoria_combo = ttk.Combobox(frame, values=categorias_ingreso, width=28, state="readonly")
        if categorias_ingreso: self.categoria_combo.current(0)
        self.categoria_combo.grid(row=1, column=1, padx=5, pady=10)
        
        ttk.Label(frame, text="Fecha:", font=("Helvetica", 10)).grid(row=2, column=0, padx=5, pady=10, sticky=W)
        self.fecha_entry = DateEntry(frame, width=12, firstweekday=0, dateformat="%d/%m/%Y"); self.fecha_entry.grid(row=2, column=1, padx=5, pady=10, sticky=W)
        
        ttk.Label(frame, text="Total ($):", font=("Helvetica", 10)).grid(row=3, column=0, padx=5, pady=10, sticky=W)
        self.monto_entry = ttk.Entry(frame, width=30); self.monto_entry.grid(row=3, column=1, padx=5, pady=10)
        
        btn_frame = ttk.Frame(frame); btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Botón dinámico
        btn_texto = "Actualizar" if self.transaccion_id else "Guardar Ingreso"
        
        ttk.Button(btn_frame, text=btn_texto, command=self.guardar_ingreso, bootstyle=SUCCESS).pack(side=LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy, bootstyle=SECONDARY).pack(side=LEFT, padx=10)
        
        # Si estamos en modo edición, cargar los datos
        if self.transaccion_id:
            self._cargar_datos_edicion()

    def _cargar_datos_edicion(self):
        """
        Obtiene los datos de la BD y rellena el formulario.
        """
        # (fecha, detalle, monto, tipo, categoria_nombre)
        data = database.obtener_transaccion_por_id(self.transaccion_id)
        if data:
            fecha_str, detalle, monto, tipo, categoria = data
            
            # Rellenar campos
            self.detalle_entry.insert(0, detalle)
            self.monto_entry.insert(0, f"{monto:.2f}")
            self.categoria_combo.set(categoria)
            
            # Convertir fecha de 'YYYY-MM-DD' a objeto date
            try:
                fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                self.fecha_entry.set_date(fecha_obj)
            except ValueError:
                pass # Dejar la fecha de hoy si hay error

    def guardar_ingreso(self):
        detalle = self.detalle_entry.get(); categoria = self.categoria_combo.get()
        fecha_obj = self.fecha_entry.get_date(); fecha_str = fecha_obj.strftime("%Y-%m-%d")
        monto_str = self.monto_entry.get().replace(',', '.')
        
        if not detalle or not categoria or not monto_str:
            messagebox.showerror("Error de validación", "Todos los campos son obligatorios.", parent=self); return
        try:
            monto = float(monto_str)
            if monto <= 0: raise ValueError("El monto debe ser positivo")
        except ValueError:
            messagebox.showerror("Error de validación", "El 'Total' debe ser un número válido y positivo.", parent=self); return
        
        try:
            if self.transaccion_id:
                # --- MODO ACTUALIZAR ---
                database.actualizar_transaccion(self.transaccion_id, fecha_str, detalle, monto, 'ingreso', categoria)
                messagebox.showinfo("Éxito", "Ingreso actualizado correctamente.", parent=self)
            else:
                # --- MODO CREAR ---
                database.agregar_transaccion(fecha_str, detalle, monto, 'ingreso', categoria)
                messagebox.showinfo("Éxito", "Ingreso guardado correctamente.", parent=self)
                
            self.parent.refrescar_datos_globales()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error en Base de Datos", f"No se pudo guardar el ingreso:\n{e}", parent=self)
