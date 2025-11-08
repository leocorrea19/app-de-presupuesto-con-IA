import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
import database
from tkinter import messagebox
import datetime
# (Maneja la pestaña "Reportes" y su lógica de filtros)
class TabReportes(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app # <--- Referencia a la app principal

        self._crear_widgets()

    def _crear_widgets(self):
        filtro_frame = ttk.Frame(self, padding=10); filtro_frame.pack(fill=X)
        
        ttk.Label(filtro_frame, text="Tipo de Reporte:").pack(side=LEFT, padx=(5, 2))
        self.reporte_tipo_combo = ttk.Combobox(filtro_frame, values=["Gastos", "Ingresos"], width=10, state="readonly")
        self.reporte_tipo_combo.current(0); self.reporte_tipo_combo.pack(side=LEFT, padx=5)
        self.reporte_tipo_combo.bind("<<ComboboxSelected>>", self.actualizar_filtro_categorias_reporte)
        
        ttk.Label(filtro_frame, text="Desde:").pack(side=LEFT, padx=(15, 2))
        self.reporte_fecha_desde = DateEntry(filtro_frame, width=12, firstweekday=0, dateformat="%d/%m/%Y"); self.reporte_fecha_desde.pack(side=LEFT, padx=5)
        hoy = datetime.date.today(); primero_del_mes = hoy.replace(day=1); self.reporte_fecha_desde.set_date(primero_del_mes)
        
        ttk.Label(filtro_frame, text="Hasta:").pack(side=LEFT, padx=(15, 2))
        self.reporte_fecha_hasta = DateEntry(filtro_frame, width=12, firstweekday=0, dateformat="%d/%m/%Y"); self.reporte_fecha_hasta.pack(side=LEFT, padx=5)
        self.reporte_fecha_hasta.set_date(hoy)
        
        ttk.Label(filtro_frame, text="Categoría:").pack(side=LEFT, padx=(15, 2))
        self.reporte_categoria_combo = ttk.Combobox(filtro_frame, values=[" [Todas las Categorías] "], width=20, state="readonly")
        self.reporte_categoria_combo.current(0); self.reporte_categoria_combo.pack(side=LEFT, padx=5)
        
        btn_generar = ttk.Button(filtro_frame, text="Generar Reporte", command=self.generar_reporte, bootstyle=SUCCESS); btn_generar.pack(side=LEFT, padx=20)
        
        self.actualizar_filtro_categorias_reporte() 
        
        tree_frame = ttk.Frame(self); tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=(5,0))
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        self.tree_reportes = ttk.Treeview(tree_frame, columns=("id", "fecha", "detalle", "monto", "categoria"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_reportes.yview); scrollbar.pack(side=RIGHT, fill=Y); self.tree_reportes.pack(fill=BOTH, expand=True)
        self.tree_reportes.heading("id", text="ID"); self.tree_reportes.heading("fecha", text="Fecha"); self.tree_reportes.heading("detalle", text="Detalle"); self.tree_reportes.heading("monto", text="Monto ($)"); self.tree_reportes.heading("categoria", text="Categoría")
        self.tree_reportes.column("id", width=50, anchor=CENTER); self.tree_reportes.column("fecha", width=100, anchor=CENTER); self.tree_reportes.column("detalle", width=300); self.tree_reportes.column("monto", width=100, anchor=E); self.tree_reportes.column("categoria", width=150, anchor=CENTER)

    def actualizar_filtro_categorias_reporte(self, event=None):
        tipo_ui = self.reporte_tipo_combo.get()
        tipo_bd = 'gasto' if tipo_ui == 'Gastos' else 'ingreso'
        categorias = [" [Todas las Categorías] "] + database.obtener_categorias(tipo_bd)
        self.reporte_categoria_combo['values'] = categorias
        self.reporte_categoria_combo.current(0)
        
    def generar_reporte(self):
        tipo_ui = self.reporte_tipo_combo.get(); tipo_bd = 'gasto' if tipo_ui == 'Gastos' else 'ingreso'
        fecha_desde_obj = self.reporte_fecha_desde.get_date(); fecha_desde_str = fecha_desde_obj.strftime("%Y-%m-%d")
        fecha_hasta_obj = self.reporte_fecha_hasta.get_date(); fecha_hasta_str = fecha_hasta_obj.strftime("%Y-%m-%d")
        categoria_sel = self.reporte_categoria_combo.get()
        
        if fecha_desde_obj > fecha_hasta_obj:
            messagebox.showerror("Error de Fechas", "La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.", parent=self.app); return
        
        categoria_filtro = None
        if categoria_sel != " [Todas las Categorías] ": categoria_filtro = categoria_sel
        
        try:
            resultados = database.obtener_transacciones_reporte(tipo=tipo_bd, fecha_inicio=fecha_desde_str, fecha_fin=fecha_hasta_str, categoria_nombre=categoria_filtro)
            for item in self.tree_reportes.get_children(): self.tree_reportes.delete(item)
            if not resultados:
                messagebox.showinfo("Sin Resultados", f"No se encontraron {tipo_bd}s que coincidan con los filtros.", parent=self.app)
            else:
                for trans in resultados: self.tree_reportes.insert(parent="", index=END, values=trans)
        except Exception as e:
            messagebox.showerror("Error en Base de Datos", f"No se pudo generar el reporte:\n{e}", parent=self.app)