from flask import Flask, render_template
from paho import client 
import sqlite3 as sql

#creacion de la base de datos 

conn = sql.connect("database.bd")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXIST mediciones(
    id INTEGRER PRIMARY KEY AUTOINCREMENT,
    dispositivo TEXT,
    temperatura REAL,
    ph INTEGRER,
    turbidez REAL,
    latitud REAL,
    longitud REAL,
    altitud REAL,
    velocidad REAL,
    )
""")
conn.commit()
conn.close

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)