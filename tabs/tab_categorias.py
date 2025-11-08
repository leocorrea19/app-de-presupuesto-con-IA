import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import database
from tkinter import messagebox
import sqlite3

# (Maneja la pestaña "Gestión de Categorías" y su lógica de CRUD/Fusión)
class TabCategorias(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app # <--- Referencia a la app principal
        self.cat_selected_id = None

        self._crear_widgets()
        self.actualizar_tabla() # Carga inicial

    def _crear_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, pady=10)
        
        form_frame = ttk.Frame(main_frame, padding=20); form_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        ttk.Label(form_frame, text="Crear / Editar Categoría", font=("Helvetica", 16, "bold"), bootstyle=PRIMARY).pack(pady=(0, 20))
        
        ttk.Label(form_frame, text="Nombre de Categoría:").pack(fill=X, pady=5)
        self.cat_nombre_entry = ttk.Entry(form_frame, width=30); self.cat_nombre_entry.pack(fill=X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Tipo:").pack(fill=X, pady=5)
        self.cat_tipo_combo = ttk.Combobox(form_frame, values=["ingreso", "gasto"], width=28, state="readonly"); self.cat_tipo_combo.pack(fill=X, pady=(0, 20))
        
        btn_frame = ttk.Frame(form_frame); btn_frame.pack(fill=X)
        
        self.cat_btn_nuevo = ttk.Button(btn_frame, text="Nuevo / Limpiar", command=self.cat_limpiar_formulario, bootstyle=INFO); self.cat_btn_nuevo.pack(side=LEFT, expand=True, fill=X, padx=(0, 5))
        self.cat_btn_guardar = ttk.Button(btn_frame, text="Guardar", command=self.cat_guardar, bootstyle=SUCCESS, state=DISABLED); self.cat_btn_guardar.pack(side=LEFT, expand=True, fill=X)
        
        self.cat_btn_eliminar = ttk.Button(form_frame, text="Eliminar Seleccionado", command=self.cat_eliminar, bootstyle=DANGER, state=DISABLED); self.cat_btn_eliminar.pack(fill=X, pady=(15, 0))

        tree_frame = ttk.Frame(main_frame); tree_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        ttk.Label(tree_frame, text="Categorías Existentes", font=("Helvetica", 16, "bold"), bootstyle=PRIMARY).pack(pady=(0, 20))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL)
        self.tree_categorias = ttk.Treeview(tree_frame, columns=("id", "nombre", "tipo"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_categorias.yview); scrollbar.pack(side=RIGHT, fill=Y); self.tree_categorias.pack(fill=BOTH, expand=True)
        
        self.tree_categorias.heading("id", text="ID"); self.tree_categorias.heading("nombre", text="Nombre"); self.tree_categorias.heading("tipo", text="Tipo")
        self.tree_categorias.column("id", width=50, anchor=CENTER); self.tree_categorias.column("nombre", width=200); self.tree_categorias.column("tipo", width=100, anchor=CENTER)
        
        self.tree_categorias.bind("<<TreeviewSelect>>", self.on_categoria_select)
        
        self.cat_limpiar_formulario()

    def actualizar_tabla(self):
        for item in self.tree_categorias.get_children():
            self.tree_categorias.delete(item)
        categorias = database.obtener_todas_las_categorias()
        for cat in categorias: self.tree_categorias.insert(parent="", index=END, values=cat)
            
    def on_categoria_select(self, event=None):
        selection = self.tree_categorias.selection();
        if not selection: return
        item_id = selection[0]; item_values = self.tree_categorias.item(item_id, 'values')
        cat_id = item_values[0]; cat_nombre = item_values[1]; cat_tipo = item_values[2]
        self.cat_nombre_entry.delete(0, END); self.cat_nombre_entry.insert(0, cat_nombre)
        self.cat_tipo_combo.set(cat_tipo); self.cat_selected_id = cat_id
        self.cat_btn_guardar.config(text="Actualizar", state=NORMAL); self.cat_btn_eliminar.config(state=NORMAL)

    def cat_limpiar_formulario(self):
        self.cat_nombre_entry.delete(0, END); self.cat_tipo_combo.set(""); self.cat_selected_id = None
        self.cat_btn_guardar.config(text="Guardar", state=NORMAL); self.cat_btn_eliminar.config(state=DISABLED)
        self.tree_categorias.selection_remove(self.tree_categorias.selection())
        
    def cat_guardar(self):
        nombre = self.cat_nombre_entry.get(); tipo = self.cat_tipo_combo.get()
        if not nombre or not tipo:
            messagebox.showerror("Error", "El Nombre y el Tipo son obligatorios.", parent=self.app); return
        
        try:
            if self.cat_selected_id is None:
                database.crear_categoria(nombre, tipo)
                messagebox.showinfo("Éxito", "Categoría creada correctamente.", parent=self.app)
            else:
                database.actualizar_categoria(self.cat_selected_id, nombre, tipo)
                messagebox.showinfo("Éxito", "Categoría actualizada correctamente.", parent=self.app)

        except ValueError as e:
            messagebox.showerror("Error de Lógica", str(e), parent=self.app)
            
        except sqlite3.IntegrityError:
            msg = f"La categoría '{nombre}' ya existe. ¿Deseas fusionar todos los movimientos de la categoría seleccionada dentro de '{nombre}'?"
            if messagebox.askyesno("Fusionar Categorías", msg, parent=self.app):
                try:
                    target = database.obtener_categoria_por_nombre(nombre, tipo)
                    if not target:
                        messagebox.showerror("Error", "No se encontró la categoría de destino.", parent=self.app); return
                    id_destino = target[0]; id_origen = self.cat_selected_id
                    if id_origen == id_destino:
                        messagebox.showwarning("Aviso", "No se puede fusionar una categoría consigo misma.", parent=self.app); return
                    database.fusionar_categorias(id_origen, id_destino)
                    messagebox.showinfo("Éxito", "Categorías fusionadas correctamente.", parent=self.app)
                except Exception as e_merge:
                    messagebox.showerror("Error de Fusión", f"No se pudo completar la fusión:\n{e_merge}", parent=self.app)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{e}", parent=self.app)

        finally:
            self.cat_limpiar_formulario()
            self.app.refrescar_datos_globales() # Llama a la App principal

    def cat_eliminar(self):
        if self.cat_selected_id is None:
            messagebox.showwarning("Aviso", "No hay ninguna categoría seleccionada.", parent=self.app); return
        
        if messagebox.askyesno("Confirmar Eliminación", "¿Estás seguro de que deseas eliminar esta categoría? Esta acción no se puede deshacer.", parent=self.app):
            try:
                database.eliminar_categoria(self.cat_selected_id)
                messagebox.showinfo("Éxito", "Categoría eliminada.", parent=self.app)
            except ValueError as e:
                messagebox.showerror("Error de Lógica", str(e), parent=self.app)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la categoría:\n{e}", parent=self.app)
            finally:
                self.cat_limpiar_formulario()
                self.app.refrescar_datos_globales() # Llama a la App principal