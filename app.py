from flask import Flask, render_template, send_from_directory, request, jsonify
import sqlite3 as sql
import os

# ---------------------------
# Configuración de Flask
# ---------------------------
app = Flask(__name__)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    # Intenta conectar. Si la base de datos no existe, la crea.
    conn = sql.connect("database.db", check_same_thread=False)
    conn.row_factory = sql.Row
    return conn

# Función para crear la tabla de mediciones (si no existe)
def create_table_if_not_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mediciones(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dispositivo TEXT,
        temperatura REAL,
        ph INTEGER,
        turbidez REAL,
        latitud REAL,
        longitud REAL,
        altitud REAL,
        velocidad REAL
    )
    """)
    conn.commit()
    conn.close()

# Llamar a la función para crear la tabla al inicio del script
# Esto lo hace de forma segura sin bloquear la aplicación
create_table_if_not_exists()

# Rutas de las páginas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/GPS')
def gps():
    return render_template('GPS.html')

@app.route('/datos')
def datos():
    return render_template('datos.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/data')
def get_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT temperatura, ph, turbidez FROM mediciones ORDER BY id DESC LIMIT 1")
    last_record = cursor.fetchone()
    conn.close()
    
    if last_record:
        data = {
            "temperatura": last_record["temperatura"],
            "ph": last_record["ph"],
            "turbidez": last_record["turbidez"]
        }
    else:
        data = {
            "temperatura": 0,
            "ph": 0,
            "turbidez": 0
        }
        
    return jsonify(data)

# ---------------------------
# Servir archivos estáticos
# ---------------------------
@app.route('/script.js')
def controles_js():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'controles.js')

# ---------------------------
# Recibir comandos WASD
# ---------------------------
@app.route('/control/<key>', methods=['POST'])
def control_key(key):
    if key == "w":
        print("Mover hacia adelante")
    elif key == "a":
        print("Mover a la izquierda")
    elif key == "s":
        print("Mover hacia atrás")
    elif key == "d":
        print("Mover a la derecha")
    else:
        print(f"Tecla desconocida: {key}")
    return f"Comando {key} recibido"

if __name__ == "__main__":
    app.run(debug=True)