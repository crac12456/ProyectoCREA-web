from flask import Flask, render_template
from paho import client 

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