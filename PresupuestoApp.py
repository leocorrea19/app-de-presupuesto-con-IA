import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import database 

# --- Importar las Pestañas ---
from tabs.tab_inicio import TabInicio
from tabs.tab_ingresos import TabIngresos
from tabs.tab_gastos import TabGastos
from tabs.tab_reportes import TabReportes
from tabs.tab_categorias import TabCategorias

# --- Importar los Formularios ---
from classes import FormularioIngreso, FormularioGasto

class PresupuestoApp(ttk.Window):

    def __init__(self):
        super().__init__(themename="litera", title="Mi Gestor de Presupuesto")
        self.geometry("1000x600") 
        self.place_window_center()

        database.inicializar_bd()
        self._crear_widgets()
        
        self.refrescar_datos_globales()

    def _crear_widgets(self):
        # --- Cabecera ---
        header_frame = ttk.Frame(self, padding=10, bootstyle=PRIMARY)
        header_frame.pack(fill=X, side=TOP)
        self.presupuesto_var = ttk.StringVar(value="Balance Total: $0.00")
        ttk.Label(header_frame, textvariable=self.presupuesto_var, 
                    font=("Helvetica", 16, "bold"), bootstyle=INVERSE).pack(side=RIGHT, padx=10)
        
        # --- Notebook (Contenedor de Pestañas) ---
        notebook = ttk.Notebook(self, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- Crear e Instanciar cada Pestaña ---
        # Pasamos 'notebook' (el padre) y 'self' (la app principal)
        
        self.tab_inicio = TabInicio(notebook, self)
        notebook.add(self.tab_inicio, text="Inicio")

        self.tab_ingresos = TabIngresos(notebook, self)
        notebook.add(self.tab_ingresos, text="Ver Ingresos")

        self.tab_gastos = TabGastos(notebook, self)
        notebook.add(self.tab_gastos, text="Ver Gastos")
        
        self.tab_reportes = TabReportes(notebook, self)
        notebook.add(self.tab_reportes, text="Reportes y Comparativas")
        
        self.tab_categorias = TabCategorias(notebook, self)
        notebook.add(self.tab_categorias, text="Gestión de Categorías")

    # --- Funciones "Globales" que las pestañas pueden llamar ---

    def refrescar_datos_globales(self):
        """
        Actualiza todos los componentes de la app que muestran datos.
        Delega la actualización a cada pestaña.
        """
        self.actualizar_header_global()
        
        # Delegar a cada pestaña que actualice su propia data
        self.tab_inicio.actualizar_dashboard() 
        self.tab_ingresos.actualizar_tabla()
        self.tab_gastos.actualizar_tabla()
        self.tab_reportes.actualizar_filtro_categorias_reporte()
        self.tab_categorias.actualizar_tabla()

    def actualizar_header_global(self):
        """Actualiza el balance total en la cabecera."""
        balance = database.obtener_balance_total()
        self.presupuesto_var.set(f"Balance Total: ${balance:,.2f}")

    def abrir_form_ingreso(self, transaccion_id=None):
        """
        Abre el formulario de ingresos.
        (Llamado desde tab_inicio y tab_ingresos)
        """
        form = FormularioIngreso(parent=self, transaccion_id=transaccion_id) 
        form.grab_set()
        
    def abrir_form_gasto(self, transaccion_id=None):
        """
        Abre el formulario de gastos.
        (Llamado desde tab_inicio y tab_gastos)
        """
        form = FormularioGasto(parent=self, transaccion_id=transaccion_id) 
        form.grab_set()