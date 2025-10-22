import sqlite3
import pandas as pd
import os
from contextlib import contextmanager

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# ----------------------------------------------------------------------

# Define la ruta base del proyecto (un nivel arriba del directorio 'core')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Define la ruta a la base de datos (en la raíz del proyecto)
DATABASE_FILE = os.path.join(BASE_DIR, 'futbolmania.db')
# Define la ruta a la carpeta de datos CSV
DATA_DIR = os.path.join(BASE_DIR, 'data')

# ----------------------------------------------------------------------
# CLASE DATABASE MANAGER
# ----------------------------------------------------------------------

class DatabaseManager:
    """
    Clase para gestionar la conexión y la carga de datos 
    desde archivos CSV a la base de datos SQLite.
    """
    def __init__(self, db_path=DATABASE_FILE, data_dir=DATA_DIR):
        self.db_path = db_path
        self.data_dir = data_dir

    @contextmanager
    def connect(self):
        """Context Manager para manejar la conexión a SQLite."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except sqlite3.Error as e:
            print(f"Error de conexión a la base de datos: {e}")
        finally:
            if conn:
                conn.close()

    def initialize_database(self):
        """
        Conecta a la base de datos (o la crea si no existe) e inicia
        el proceso de carga de todos los archivos CSV.
        """
        print(f"Conexión exitosa a la base de datos: {self.db_path}")
        self.load_all_data()

    def load_data_from_csv(self, file_name, table_name):
        """
        Carga un archivo CSV específico en una tabla SQLite.
        Aplica corrección de codificación y manejo de errores.
        """
        file_path = os.path.join(self.data_dir, file_name)
        
        try:
            # Intentar cargar con 'latin1' (ISO-8859-1) para manejar caracteres especiales
            # low_memory=False se usa por seguridad en datasets grandes
            df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
            
            # Limpieza básica: rellenar NaN en columnas que deberían ser numéricas si es necesario
            # Se recomienda hacer esta limpieza en el DataAnalyzer, pero aquí lo haremos básico
            df = df.fillna(value='')
            
            with self.connect() as conn:
                if conn:
                    # Sobrescribe la tabla si ya existe (para recarga)
                    df.to_sql(table_name, conn, if_exists='replace', index=False)
                    # print(f"✅ Tabla '{table_name}' cargada con {len(df):,} registros.")
                    return True
            
        except FileNotFoundError:
            print(f"❌ Error: Archivo CSV no encontrado en la ruta: {file_path}")
            return False
        except pd.errors.ParserError as e:
            print(f"❌ Error de parsing en '{file_name}': {e}")
            return False
        except Exception as e:
            print(f"❌ Error desconocido al cargar '{file_name}' en la tabla '{table_name}': {e}")
            return False
        
        return False

    def load_all_data(self):
        """Coordina la carga de todos los archivos CSV a SQLite."""
        
        # LISTA COMPLETA DE TODOS LOS ARCHIVOS CSV A CARGAR
        # (Nombre de la tabla, Nombre del archivo CSV)
        csv_files = [
            # 5 Archivos originales
            ('players', 'players.csv'),
            ('clubs', 'clubs.csv'),
            ('appearances', 'appearances.csv'),
            ('transfers', 'transfers.csv'),
            ('game_events', 'game_events.csv'),
            
            # 15 Archivos adicionales identificados
            ('past_data', 'past-data.csv'),
            ('world_cup_players', 'WorldCupPlayers.csv'),
            ('full_dataset', 'Full_Dataset.csv'),
            ('libertadores_finals', 'libertadores_finals.csv'),
            ('competitions', 'competitions.csv'),
            ('world_cups', 'WorldCups.csv'),
            ('world_cup_matches', 'WorldCupMatches.csv'),
            ('libertadores_matches', 'Libertadores.csv'),
            ('ucl_finals', 'UCL_Finals_1955-2023.csv'),
            ('ucl_performance', 'UCL_AllTime_Performance_Table.csv'),
            ('ballon_dor', 'ballon_dor_rankings.csv'),
            ('general_dataset', 'dataset.csv'),
            ('shootouts', 'shootouts.csv'),
            ('match_results', 'results.csv'),
            ('match_goalscorers', 'goalscorers.csv'),
        ]

        print("\n--- Iniciando Carga de Datos ---")
        
        for table_name, file_name in csv_files:
            file_path = os.path.join(self.data_dir, file_name)
            
            if not os.path.exists(file_path):
                print(f" Archivo NO encontrado: {file_name}. Saltando esta tabla.")
                continue
            
            success = self.load_data_from_csv(file_name, table_name)
            
            if success:
                print(f" Tabla '{table_name}' cargada exitosamente.")

        print("\n--- Carga de Datos Finalizada. Commits guardados. ---")


# ----------------------------------------------------------------------
# BLOQUE DE PRUEBA (SOLO PARA VERIFICACIÓN)
# ----------------------------------------------------------------------
if __name__ == '__main__':
    # ⚠️ ADVERTENCIA: Esta ejecución borrará el archivo futbolmania.db y lo recreará 
    # con TODAS las 20 tablas. Puede tardar varios minutos.
    
    # Opcional: Borrar la base de datos antigua antes de empezar
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print(f"Archivo antiguo '{os.path.basename(DATABASE_FILE)}' eliminado.")
        
    db_manager = DatabaseManager()
    db_manager.initialize_database()

    print("\n--- Verificación de Tablas Creadas ---")
    try:
        with db_manager.connect() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"Tablas cargadas ({len(tables)}): {', '.join(tables)}")
    except Exception as e:
        print(f"Error de verificación: {e}")