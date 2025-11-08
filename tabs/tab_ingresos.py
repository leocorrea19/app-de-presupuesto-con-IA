import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import database
from tkinter import messagebox

#(Maneja la pestaña "Ver Ingresos", su tabla y su lógica de CRUD)
class TabIngresos(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=(10, 0))
        self.app = app # <--- Referencia a la app principal

        self._crear_widgets()

    def _crear_widgets(self):
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=X, padx=10, pady=5)
        
        ttk.Label(action_frame, text="Haz doble clic en una fila para editar.", bootstyle=INFO).pack(side=LEFT)
        
        btn_eliminar = ttk.Button(action_frame, text="Eliminar Seleccionado", 
                                    command=self.eliminar_ingreso_seleccionado, bootstyle=DANGER)
        btn_eliminar.pack(side=RIGHT)
        
        tree_frame = ttk.Frame(self); tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0,10))
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        
        self.tree_ingresos = ttk.Treeview(tree_frame, columns=("id", "fecha", "detalle", "monto", "categoria"), show="headings", yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree_ingresos.yview); scrollbar.pack(side=RIGHT, fill=Y); self.tree_ingresos.pack(fill=BOTH, expand=True)
        self.tree_ingresos.heading("id", text="ID"); self.tree_ingresos.heading("fecha", text="Fecha"); self.tree_ingresos.heading("detalle", text="Detalle"); self.tree_ingresos.heading("monto", text="Monto ($)"); self.tree_ingresos.heading("categoria", text="Categoría")
        self.tree_ingresos.column("id", width=50, anchor=CENTER); self.tree_ingresos.column("fecha", width=100, anchor=CENTER); self.tree_ingresos.column("detalle", width=300); self.tree_ingresos.column("monto", width=100, anchor=E); self.tree_ingresos.column("categoria", width=150, anchor=CENTER)
        
        self.tree_ingresos.bind("<Double-1>", self.on_ingreso_double_click)

    def actualizar_tabla(self):
        for item in self.tree_ingresos.get_children(): self.tree_ingresos.delete(item)
        transacciones = database.obtener_transacciones('ingreso')
        for trans in transacciones: self.tree_ingresos.insert(parent="", index=END, values=trans)

    def on_ingreso_double_click(self, event):
        selection = self.tree_ingresos.selection()
        if not selection: return
        
        item_id_str = selection[0]
        item_values = self.tree_ingresos.item(item_id_str, 'values')
        transaccion_id = item_values[0] 
        
        # --- Llama a la App principal para abrir el form ---
        self.app.abrir_form_ingreso(transaccion_id=transaccion_id)
        
    def eliminar_ingreso_seleccionado(self):
        selection = self.tree_ingresos.selection()
        if not selection:
            messagebox.showwarning("Sin selección", "Por favor, selecciona un ingreso de la lista para eliminar.", parent=self.app)
            return
            
        item_id_str = selection[0]
        item_values = self.tree_ingresos.item(item_id_str, 'values')
        transaccion_id = item_values[0]
        detalle = item_values[2] 
        
        if messagebox.askyesno("Confirmar Eliminación", 
                                f"¿Estás seguro de que deseas eliminar el ingreso:\n\n'{detalle}'?",
                                parent=self.app):
            try:
                database.eliminar_transaccion(transaccion_id)
                messagebox.showinfo("Éxito", "Ingreso eliminado.", parent=self.app)
                self.app.refrescar_datos_globales() # Llama a la App principal
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}", parent=self.app)