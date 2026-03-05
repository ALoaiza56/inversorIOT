from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# En Vercel, necesitamos usar /tmp para tener permisos de escritura en SQLite
# pero recuerda que los datos NO persistirán entre reinicios.
DB_PATH = '/tmp/database.db' if os.environ.get('VERCEL') else 'database.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        # Esto permite acceder a las columnas por nombre como un diccionario
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para que el ESP32 guarde datos
@app.route('/guardar', methods=['POST'])
def guardar():
    # Intentar obtener datos de JSON, si no, de form
    data = request.get_json() if request.is_json else request.form
    
    v1 = data.get('v1')
    v2 = data.get('v2')
    i1 = data.get('i1')
    i2 = data.get('i2')

    if not all([v1, v2, i1, i2]):
        return "ERROR: Missing values", 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO datos (voltaje1, voltaje2, corriente1, corriente2) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (v1, v2, i1, i2))
            conn.commit()
            return "OK"
        except sqlite3.Error as e:
            return f"DATABASE ERROR: {e}", 500
        finally:
            conn.close()
    return "DB CONNECTION ERROR", 500

# Ruta que consulta el ESP32 para saber el estado
@app.route('/comando', methods=['GET'])
def comando():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT estado FROM control WHERE id = 1")
            result = cursor.fetchone()
            if result:
                return str(result['estado'])
            return "OFF"
        except sqlite3.Error as e:
            return "OFF", 500
        finally:
            conn.close()
    return "OFF", 500

# Ruta para cambiar el estado desde la web
@app.route('/cambiar_estado', methods=['POST'])
def cambiar_estado():
    nuevo_estado = request.form.get('estado')
    if nuevo_estado not in ['ON', 'OFF']:
        return jsonify({"status": "error", "message": "Invalid state"}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "UPDATE control SET estado = ? WHERE id = 1"
            cursor.execute(query, (nuevo_estado,))
            conn.commit()
            return jsonify({"status": "success", "estado": nuevo_estado})
        except sqlite3.Error as e:
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"status": "error", "message": "DB connection error"}), 500

# Ruta que devuelve los últimos 20 datos en JSON para la gráfica
@app.route('/datos_json', methods=['GET'])
def datos_json():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM datos ORDER BY fecha DESC LIMIT 20")
            rows = cursor.fetchall()
            # Convertimos sqlite3.Row a diccionarios para jsonify
            data = [dict(row) for row in rows]
            # Invertimos para que la gráfica se vea de izquierda a derecha (pasado a presente)
            return jsonify(data[::-1])
        except sqlite3.Error as e:
            return jsonify([]), 500
        finally:
            conn.close()
    return jsonify([]), 500

# Inicializar la base de datos al importar el módulo (necesario para Vercel)
if not os.path.exists(DB_PATH):
    from init_sqlite import init_db
    # Pasamos el DB_PATH para que cree la base de datos en el lugar correcto
    import init_sqlite
    init_sqlite.DB_PATH = DB_PATH
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
