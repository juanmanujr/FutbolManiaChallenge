# logic/database_inspector.py

import sqlite3
import os

# Define la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_FILE = os.path.join(BASE_DIR, 'futbolmania.db')

def inspect_database_schema(db_path):
    """
    Conecta a la base de datos y muestra el esquema (tablas y columnas)
    para identificar inconsistencias en los nombres (mayúsculas/minúsculas).
    """
    print(f"--- INSPECCIÓN DE ESQUEMA: {os.path.basename(db_path)} ---")
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Obtener la lista de todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print(" No se encontraron tablas en la base de datos.")
            return

        # 2. Iterar sobre cada tabla e imprimir su esquema
        for (table_name,) in tables:
            print(f"\n[TABLA: {table_name.upper()}]")
            
            # Consulta PRAGMA para obtener las columnas de la tabla
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Formato de impresión
            print("  ID | Nombre de Columna | Tipo de Dato")
            print("  ---|-------------------|--------------")
            for cid, name, type_name, notnull, default_value, pk in columns:
                print(f"  {cid:2} | {name:<17} | {type_name}")

    except sqlite3.Error as e:
        print(f" Error al conectar o consultar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    inspect_database_schema(DATABASE_FILE)