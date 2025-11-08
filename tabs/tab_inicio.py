import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import database
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# (Maneja el Dashboard, KPIs y el gráfico)
class TabInicio(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app # <--- Referencia a la app principal

        self._crear_widgets()

    def _crear_widgets(self):
        # --- 0. Título del Mes ---
        self.dashboard_mes_var = ttk.StringVar(value="Resumen del Mes")
        ttk.Label(self, textvariable=self.dashboard_mes_var, font=("Helvetica", 18, "bold"), bootstyle=PRIMARY)\
            .pack(pady=(5, 10))

        # --- 1. Frame Superior para KPIs ---
        kpi_frame = ttk.Frame(self, padding=10)
        kpi_frame.pack(fill=X)
        
        self.kpi_ingreso_mes_var = ttk.StringVar(value="Ingreso del Mes: $0.00")
        self.kpi_gasto_mes_var = ttk.StringVar(value="Gasto del Mes: $0.00")
        self.kpi_balance_mes_var = ttk.StringVar(value="Balance del Mes: $0.00")

        kpi_frame.columnconfigure(0, weight=1)
        kpi_frame.columnconfigure(1, weight=1)
        kpi_frame.columnconfigure(2, weight=1)

        ttk.Label(kpi_frame, textvariable=self.kpi_ingreso_mes_var, font=("Helvetica", 14), bootstyle=SUCCESS)\
            .grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(kpi_frame, textvariable=self.kpi_gasto_mes_var, font=("Helvetica", 14), bootstyle=DANGER)\
            .grid(row=0, column=1, padx=10, pady=10)
        ttk.Label(kpi_frame, textvariable=self.kpi_balance_mes_var, font=("Helvetica", 14), bootstyle=INFO)\
            .grid(row=0, column=2, padx=10, pady=10)
            
        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)

        # --- 2. Frame Inferior (Gráfico y Botones) ---
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=BOTH, expand=True)

        self.chart_frame = ttk.Frame(bottom_frame, padding=10)
        self.chart_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        ttk.Label(self.chart_frame, text="Gastos del Mes por Categoría", font=("Helvetica", 16, "bold"), bootstyle=PRIMARY)\
            .pack(pady=5)
        
        self.crear_dashboard_chart(self.chart_frame)

        button_frame = ttk.Frame(bottom_frame, padding=40)
        button_frame.pack(side=RIGHT, fill=Y)

        ttk.Label(button_frame, text="Menú de opciones", font=("Helvetica", 16, "bold"), bootstyle=PRIMARY)\
            .pack(pady=20)
        
        # --- Botones llaman a la App principal ---
        btn_ingreso = ttk.Button(button_frame, text="Cargar nuevo ingreso", 
                                    command=self.app.abrir_form_ingreso, bootstyle=SUCCESS, width=30)
        btn_ingreso.pack(pady=10, ipady=10)
        
        btn_gasto = ttk.Button(button_frame, text="Cargar nuevo gasto", 
                                command=self.app.abrir_form_gasto, bootstyle=DANGER, width=30)
        btn_gasto.pack(pady=10, ipady=10)
        
        btn_salir = ttk.Button(button_frame, text="Salir", 
                                command=self.app.quit, bootstyle=SECONDARY, width=30)
        btn_salir.pack(pady=40, ipady=10)

    def crear_dashboard_chart(self, parent_frame):
        style = ttk.Style()
        bg_color = style.colors.get('bg')
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor=bg_color)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(bg_color)
        self.ax.set_title("Cargando datos...", color=style.colors.get('fg'))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        self.canvas.draw()

    def actualizar_dashboard(self):
        ahora = datetime.datetime.now()
        meses_es = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
        mes_actual = meses_es[ahora.month - 1]; titulo = f"Resumen de {mes_actual} {ahora.year}"; self.dashboard_mes_var.set(titulo)
        
        ingreso_mes = database.obtener_resumen_mes('ingreso'); gasto_mes = database.obtener_resumen_mes('gasto'); balance_mes = ingreso_mes - gasto_mes
        self.kpi_ingreso_mes_var.set(f"Ingreso del Mes: ${ingreso_mes:,.2f}"); self.kpi_gasto_mes_var.set(f"Gasto del Mes: ${gasto_mes:,.2f}"); self.kpi_balance_mes_var.set(f"Balance del Mes: ${balance_mes:,.2f}")
        
        datos_grafico = database.obtener_gastos_por_categoria_mes()
        self.ax.clear(); style = ttk.Style(); text_color = style.colors.get('fg'); self.ax.set_facecolor(style.colors.get('bg')); self.fig.set_facecolor(style.colors.get('bg'))
        
        if not datos_grafico:
            self.ax.set_title("No hay gastos este mes", color=text_color)
        else:
            etiquetas = [item[0] for item in datos_grafico]; montos = [item[1] for item in datos_grafico]
            wedges, texts, autotexts = self.ax.pie(montos, labels=etiquetas, autopct='%1.1f%%', startangle=90, textprops={'color': text_color})
            self.ax.axis('equal'); self.ax.set_title("Gastos del Mes", color=text_color)
        
        self.canvas.draw()