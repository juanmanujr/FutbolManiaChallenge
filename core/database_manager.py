# core/database_manager.py (VERSIÓN CORREGIDA Y FINAL PARA EL RANKING)

import sqlite3
import pandas as pd
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_FILE = os.path.join(BASE_DIR, 'futbolmania.db')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# ----------------------------------------------------------------------
# CLASE DATABASE MANAGER
# ----------------------------------------------------------------------

class DatabaseManager:
    """
    Clase para gestionar la conexión, la carga inicial de datos 
    y la persistencia (guardado de Ranking) en SQLite.
    """
    def __init__(self, db_path=DATABASE_FILE, data_dir=DATA_DIR):
        self.db_path = db_path
        self.data_dir = data_dir

    @contextmanager
    def connect(self):
        """Context Manager para manejar la conexión a SQLite de forma segura."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Asegura la conversión de tipos (ej. TIME, DATE) para pandas
            conn.row_factory = sqlite3.Row 
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Error de conexión a la base de datos: {e}")
            # print(f"Error de conexión a la base de datos: {e}") # Usamos logger
        finally:
            if conn:
                conn.close()
    
    def query(self, sql_query, params=None):
        """
        Ejecuta una consulta SQL y devuelve los resultados como un DataFrame de Pandas.
        """
        with self.connect() as conn:
            if not conn:
                return pd.DataFrame()
            try:
                # Usamos read_sql_query de Pandas, que es ideal para SELECTs
                return pd.read_sql_query(sql_query, conn, params=params)
            except Exception as e:
                logger.error(f"ERROR en la ejecución de consulta SQL: {e}")
                # print(f"ERROR en la ejecución de consulta SQL: {e}") # Usamos logger
                return pd.DataFrame()

    # --- LÓGICA DE PERSISTENCIA Y RANKING (CORREGIDA) ---
    
    def _create_ranking_table(self):
        """Crea la tabla Ranking si no existe (AÑADIDA COLUMNA player_name)."""
        with self.connect() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Ranking (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,  -- <<-- ¡CORREGIDO!
                        score INTEGER NOT NULL,
                        total_questions INTEGER NOT NULL,
                        game_mode TEXT NOT NULL,
                        date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # FIX CRÍTICO: Si la tabla ya existe y le falta la columna 'player_name', la añadimos.
                try:
                    cursor.execute("ALTER TABLE Ranking ADD COLUMN player_name TEXT NOT NULL DEFAULT 'Anónimo';")
                    logger.info("Columna 'player_name' añadida a la tabla Ranking.")
                except sqlite3.OperationalError as e:
                    if 'duplicate column name' in str(e):
                        pass # La columna ya existe, no hacemos nada.
                    else:
                        logger.error(f"Error al intentar añadir columna a Ranking: {e}")
                        
                conn.commit()

    def save_score(self, player_name: str, score: int, total_questions: int, game_mode: str = "TriviaClasica"):
        """Guarda un puntaje en la base de datos (AÑADIDO player_name)."""
        self._create_ranking_table() # Asegura que la tabla exista antes de insertar
        
        # Saneamiento básico del nombre
        player_name = player_name.strip() if player_name else "Anónimo"
        
        with self.connect() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Ranking (player_name, score, total_questions, game_mode)
                    VALUES (?, ?, ?, ?)
                """, (player_name, score, total_questions, game_mode))
                conn.commit()
                
    def fetch_top_scores(self, limit: int = 10) -> pd.DataFrame:
        """Obtiene los mejores puntajes del ranking (AÑADIDO player_name)."""
        self._create_ranking_table() # Asegura que la tabla exista antes de consultar
        sql = """
            SELECT player_name, score, total_questions, game_mode, date_played 
            FROM Ranking 
            ORDER BY score DESC, date_played DESC 
            LIMIT ?
        """
        # Usamos el método 'query' ya definido para obtener un DataFrame
        return self.query(sql, params=(limit,))


    # --- LÓGICA DE CARGA INICIAL (SIN CAMBIOS) ---
    
    # ... Resto del código load_csv_to_db, initialize_database, load_all_data y create_indices.
    # El resto del código no requiere cambios a menos que el ALTER TABLE no funcione
    # y necesites borrar la DB.
    # ...


    def initialize_database(self):
        """Inicializa la DB, carga las preguntas si es la primera vez y asegura la tabla Ranking."""
        db_exists = os.path.exists(self.db_path)
        
        if db_exists:
            print("Base de datos ya existente. Saltando la carga inicial de preguntas.")
        else:
            print(f"Conexión exitosa a la base de datos: {self.db_path}")
            print(" INICIANDO CARGA MÍNIMA: SOLO PREGUNTAS FIJAS.")
            self.load_all_data() 
            
            with self.connect() as conn:
                if conn:
                    self.create_indices(conn) 

        # IMPORTANTE: Asegura que la tabla de Ranking exista y esté actualizada.
        self._create_ranking_table()

    # ... [El resto de las funciones (load_all_data, load_csv_to_db, etc.) siguen igual]


# ----------------------------------------------------------------------
# BLOQUE DE PRUEBA (SOLO PARA VERIFICACIÓN)
# ----------------------------------------------------------------------
if __name__ == '__main__':
    
    # Opcional: Eliminar la DB para forzar la recarga y probar la velocidad
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print(f"Base de datos antigua eliminada: {DATABASE_FILE}")
        
    db_manager = DatabaseManager()
    
    print("--- INICIANDO PRUEBA DE CARGA MÍNIMA DE BASE DE DATOS ---")
    db_manager.initialize_database()

    print("\n--- Verificación de Tablas Creadas ---")
    try:
        with db_manager.connect() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"Tablas cargadas ({len(tables)}): {', '.join(tables)}")
                
                # Verificación de la tabla Ranking y un test de guardado
                if 'Ranking' in tables:
                    # ¡CORREGIDO: AHORA INCLUYE player_name!
                    db_manager.save_score(player_name='TestPlayer', score=8, total_questions=10, game_mode='Test_Clasico')
                    ranking_data = db_manager.fetch_top_scores(limit=1)
                    print("\n--- Prueba de Guardado y Lectura de Ranking ---")
                    print(ranking_data)
                
                if 'quiz_questions' in tables:
                    quiz_count = db_manager.query("SELECT COUNT(*) FROM quiz_questions;")
                    print(f"\nConteo TOTAL de preguntas en quiz_questions (unificadas): {quiz_count.iloc[0, 0]}")

    except Exception as e:
        print(f"Error de verificación: {e}")