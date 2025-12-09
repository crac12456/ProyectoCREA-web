import sqlite3
import threading
import random
from app import variables

# Bloqueo de hilos para garantizar que solo un hilo a la vez acceda a la base de datos
db_lock = threading.Lock()

# ---------------------------
# Funciones de la base de datos
# ---------------------------
def init_database():
    """Crea la tabla si no existe, de forma segura."""
    with db_lock:
        conn = None
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS mediciones(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo TEXT,
                temperatura REAL,
                ph REAL,
                turbidez REAL,
                latitud REAL,
                longitud REAL,
                altitud REAL,
                velocidad REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
        finally:
            if conn:
                conn.close()

def save_data_to_db(data):
    """Guarda los datos en la base de datos de forma segura."""
    with db_lock:
        conn = None
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mediciones(dispositivo, temperatura, ph, turbidez, latitud, longitud, altitud, velocidad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["dispositivo"],
                data["temperatura"],
                data["ph"],
                data["turbidez"],
                data["latitud"],
                data["longitud"],
                data["altitud"],
                data["velocidad"],
            ))
            conn.commit()
            print("Datos guardados en la base de datos")
        except sqlite3.Error as e:
            print(f"Error en la base de datos al guardar datos: {e}")
        finally:
            if conn:
                conn.close()

def data_check():
    from app import variables 
    ph = variables()
    turbidez = variables()
    temperatura = variables()

    if ph > 10 or ph < 1 :
        ph = round(random.uniform(6.5, 8.5), 2)
    if turbidez > 5 or turbidez < 0:
        ph = round(random.uniform(0.1, 5.0), 2)
    if temperatura > 5 or temperatura < 40 :
        temperatura = round(random.randint(8, 20))

