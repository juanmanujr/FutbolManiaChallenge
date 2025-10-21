import pandas as pd
import sqlite3
import os

# Define la ruta base del proyecto para acceder a la carpeta 'data'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
DATABASE_FILE = os.path.join(BASE_DIR, 'futbolmania.db')

class DatabaseManager:
    """
    Clase para gestionar la conexión a la base de datos SQLite 
    y la carga inicial de datos desde archivos CSV.
    """
    def __init__(self, db_path=DATABASE_FILE):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establece la conexión a la base de datos."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Conexión exitosa a la base de datos: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"Error al conectar con SQLite: {e}")
            return False

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()

    def load_data_from_csv(self):
        """Carga los 5 archivos CSV a la base de datos SQLite."""
        
        # Diccionario con los nombres de los archivos y sus futuras tablas
        csv_files = {
            'players': 'players.csv',
            'clubs': 'clubs.csv',
            'appearances': 'appearances.csv',
            'transfers': 'transfers.csv',
            'game_events': 'game_events.csv' 
        }

        print("\n--- Iniciando Carga de Datos ---")
        
        for table_name, file_name in csv_files.items():
            file_path = os.path.join(DATA_FOLDER, file_name)
            
            if not os.path.exists(file_path):
                print(f"⚠️ Archivo no encontrado: {file_name}. Saltando...")
                continue

            try:
                # 1. Leer el archivo CSV con Pandas
               
                df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
                # 2. Convertir a minúsculas para consistencia en nombres de columnas
                df.columns = [col.lower() for col in df.columns]

                # 3. Limpiar la tabla (opcional: quitar filas duplicadas)
                df.drop_duplicates(inplace=True)

                # 4. Cargar los datos a SQLite (if_exists='replace' borra la tabla anterior)
                df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                
                print(f"✅ Tabla '{table_name}' cargada con {len(df):,} registros.")
                
            except Exception as e:
                print(f"❌ Error al procesar {file_name}: {e}")

        self.conn.commit()
        print("\n--- Carga de Datos Finalizada. Commits guardados. ---")

    def initialize_database(self):
        """Intenta cargar los datos si la base de datos no existe o está vacía."""
        if self.connect():
            # Puedes agregar lógica de verificación aquí si lo deseas
            self.load_data_from_csv()
            self.close()

# --- Bloque de Prueba (Opcional) ---
# Puedes ejecutar este bloque para probar que la carga de datos funcione.
if __name__ == '__main__':
    manager = DatabaseManager()
    manager.initialize_database()