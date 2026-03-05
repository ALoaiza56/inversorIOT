import sqlite3
import os

DB_PATH = 'database.db'

def init_db():
    # Eliminar si ya existe para empezar de cero (opcional)
    # if os.path.exists(DB_PATH):
    #     os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla para datos de sensores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS datos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voltaje1 REAL,
        voltaje2 REAL,
        corriente1 REAL,
        corriente2 REAL,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla para estado de control
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS control (
        id INTEGER PRIMARY KEY,
        estado TEXT,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insertar registro inicial si no existe
    cursor.execute("INSERT OR IGNORE INTO control (id, estado) VALUES (1, 'OFF')")
    
    conn.commit()
    conn.close()
    print(f"Base de datos SQLite inicializada en {DB_PATH}")

if __name__ == '__main__':
    init_db()
