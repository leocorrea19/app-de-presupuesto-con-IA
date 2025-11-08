import sqlite3
import datetime 

DB_NAME = "presupuesto.db"

# --- En database.py ---

def inicializar_bd():
    """
    Crea las tablas y carga los datos de ejemplo SÓLO SI es necesario.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Crear Tablas (sin cambios)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT_NULL UNIQUE,
        tipo TEXT NOT_NULL CHECK(tipo IN ('ingreso', 'gasto'))
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        detalle TEXT NOT NULL,
        monto REAL NOT NULL,
        tipo TEXT NOT_NULL CHECK(tipo IN ('ingreso', 'gasto')),
        categoria_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
    )
    """)
    
    # --- ¡LA LÓGICA CORREGIDA! ---
    # 1. Comprobar si la tabla de categorías ya tiene datos
    cursor.execute("SELECT COUNT(*) FROM categorias")
    count = cursor.fetchone()[0]
    
    # 2. Si está vacía (count=0), cargar los datos de ejemplo
    if count == 0:
        print("Base de datos vacía. Cargando categorías de ejemplo...")
        categorias_ejemplo = [
            ('Salario', 'ingreso'), 
            ('Otros Ingresos', 'ingreso'),
            ('Supermercado', 'gasto'), 
            ('Alquiler', 'gasto'),
            ('Servicios', 'gasto'), 
            ('Ocio', 'gasto'), 
            ('Transporte', 'gasto')
        ]
        
        cursor.executemany("INSERT OR IGNORE INTO categorias (nombre, tipo) VALUES (?, ?)", categorias_ejemplo)
        conn.commit()
    # 3. Si ya tiene datos, no hacer nada.
    
    conn.close()

# --- Funciones de Transacciones (sin cambios) ---
def agregar_transaccion(fecha, detalle, monto, tipo, categoria_nombre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM categorias WHERE nombre = ? AND tipo = ?", (categoria_nombre, tipo))
    resultado = cursor.fetchone()
    if not resultado:
        conn.close(); raise Exception(f"Error: No se encontró la categoría '{categoria_nombre}'")
    categoria_id = resultado[0]
    try:
        cursor.execute("INSERT INTO transacciones (fecha, detalle, monto, tipo, categoria_id) VALUES (?, ?, ?, ?, ?)", (fecha, detalle, monto, tipo, categoria_id))
        conn.commit()
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()

def obtener_transacciones(tipo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = """
    SELECT 
        t.id, t.fecha, t.detalle, t.monto, c.nombre 
    FROM transacciones AS t
    JOIN categorias AS c ON t.categoria_id = c.id
    WHERE t.tipo = ?
    ORDER BY t.fecha DESC
    """
    cursor.execute(query, (tipo,))
    transacciones = cursor.fetchall()
    conn.close()
    return transacciones

# --- Funciones de Resumen (sin cambios) ---
def obtener_balance_total():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo = 'ingreso'")
    total_ingresos = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo = 'gasto'")
    total_gastos = cursor.fetchone()[0] or 0.0
    conn.close()
    return total_ingresos - total_gastos

# --- ¡FUNCIÓN RE-AGREGADA! ---
# La había borrado por error en el paso anterior.
def obtener_categorias(tipo):
    """
    Obtiene la lista de categorías para los menús desplegables.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM categorias WHERE tipo = ?", (tipo,))
    categorias = [item[0] for item in cursor.fetchall()]
    conn.close()
    return categorias
# --------------------------------

def _obtener_filtro_mes_actual():
    return datetime.datetime.now().strftime("%Y-%m")

def obtener_resumen_mes(tipo):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    filtro_mes = _obtener_filtro_mes_actual()
    query = "SELECT SUM(monto) FROM transacciones WHERE tipo = ? AND strftime('%Y-%m', fecha) = ?"
    cursor.execute(query, (tipo, filtro_mes))
    total = cursor.fetchone()[0] or 0.0
    conn.close()
    return total

def obtener_gastos_por_categoria_mes():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    filtro_mes = _obtener_filtro_mes_actual()
    query = """
    SELECT c.nombre, SUM(t.monto)
    FROM transacciones AS t JOIN categorias AS c ON t.categoria_id = c.id
    WHERE t.tipo = 'gasto' AND strftime('%Y-%m', t.fecha) = ?
    GROUP BY c.nombre HAVING SUM(t.monto) > 0 ORDER BY SUM(t.monto) DESC
    """
    cursor.execute(query, (filtro_mes,))
    datos = cursor.fetchall()
    conn.close()
    return datos

def obtener_transacciones_reporte(tipo, fecha_inicio, fecha_fin, categoria_nombre=None):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    query = """
    SELECT 
        t.id, t.fecha, t.detalle, t.monto, c.nombre 
    FROM transacciones AS t JOIN categorias AS c ON t.categoria_id = c.id
    WHERE t.tipo = ? AND t.fecha BETWEEN ? AND ?
    """
    params = [tipo, fecha_inicio, fecha_fin]
    if categoria_nombre:
        query += " AND c.nombre = ?"; params.append(categoria_nombre)
    query += " ORDER BY t.fecha DESC"
    cursor.execute(query, tuple(params))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

# --- Funciones de Gestión de Categorías (sin cambios) ---
def obtener_todas_las_categorias():
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, tipo FROM categorias ORDER BY tipo, nombre")
    categorias = cursor.fetchall()
    conn.close()
    return categorias

def obtener_categoria_por_nombre(nombre, tipo):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT id FROM categorias WHERE nombre = ? AND tipo = ?", (nombre, tipo))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def crear_categoria(nombre, tipo):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nombre, tipo) VALUES (?, ?)", (nombre, tipo))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback(); raise ValueError(f"La categoría '{nombre}' ya existe.")
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()

def actualizar_categoria(categoria_id, nombre_nuevo, tipo_nuevo):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("UPDATE categorias SET nombre = ?, tipo = ? WHERE id = ?", (nombre_nuevo, tipo_nuevo, categoria_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback(); raise sqlite3.IntegrityError("DUPLICADO") 
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()

def eliminar_categoria(categoria_id):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM transacciones WHERE categoria_id = ? LIMIT 1", (categoria_id,))
        en_uso = cursor.fetchone()
        if en_uso:
            raise ValueError("Esta categoría tiene transacciones asociadas. No se puede eliminar.")
        cursor.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
        conn.commit()
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()

def fusionar_categorias(id_origen, id_destino):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("UPDATE transacciones SET categoria_id = ? WHERE categoria_id = ?", (id_destino, id_origen))
        cursor.execute("DELETE FROM categorias WHERE id = ?", (id_origen,))
        conn.commit()
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()

# --- Funciones CRUD de Transacciones (sin cambios) ---

def obtener_transaccion_por_id(transaccion_id):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    query = """
    SELECT 
        t.fecha, t.detalle, t.monto, t.tipo, c.nombre 
    FROM transacciones AS t JOIN categorias AS c ON t.categoria_id = c.id
    WHERE t.id = ?
    """
    cursor.execute(query, (transaccion_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def actualizar_transaccion(transaccion_id, fecha, detalle, monto, tipo, categoria_nombre):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM categorias WHERE nombre = ? AND tipo = ?", (categoria_nombre, tipo))
        resultado_cat = cursor.fetchone()
        if not resultado_cat:
            conn.close(); raise Exception(f"Error: No se encontró la categoría '{categoria_nombre}'")
        categoria_id = resultado_cat[0]
        query = """
        UPDATE transacciones
        SET fecha = ?, detalle = ?, monto = ?, tipo = ?, categoria_id = ?
        WHERE id = ?
        """
        cursor.execute(query, (fecha, detalle, monto, tipo, categoria_id, transaccion_id))
        conn.commit()
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()

def eliminar_transaccion(transaccion_id):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transacciones WHERE id = ?", (transaccion_id,))
        conn.commit()
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()