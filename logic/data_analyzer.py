import sqlite3
import pandas as pd
import os

# Define la ruta a la base de datos (se asume que está en la raíz del proyecto)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_FILE = os.path.join(BASE_DIR, 'futbolmania.db')

class DataAnalyzer:
    """
    Clase que contiene la lógica para consultar y analizar los datos 
    almacenados en la base de datos futbolmania.db.
    Utiliza Pandas para ejecutar consultas SQL y devolver DataFrames.
    """
    def __init__(self, db_path=DATABASE_FILE):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Conecta a la base de datos SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            # Optimización para manejo de datos: 
            # Permite usar columnas por nombre en los resultados
            self.conn.row_factory = sqlite3.Row 
            return True
        except sqlite3.Error as e:
            print(f"Error al conectar con SQLite: {e}")
            return False

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()

    def get_top_scorers(self, limit=10):
        """
        Consulta que devuelve los Top N jugadores con más goles
        en el historial de partidos.
        """
        if not self.connect():
            return pd.DataFrame() 

        query = f"""
        SELECT
            T1.name AS Player_Name,
            -- Convierte goles a entero, tratando NULLs como '0' antes de la suma
            SUM(CAST(COALESCE(T2.goals, '0') AS INTEGER)) AS Total_Goals
        FROM players AS T1
        JOIN appearances AS T2 ON T1.player_id = T2.player_id
        GROUP BY 1
        HAVING Total_Goals > 0
        ORDER BY Total_Goals DESC
        LIMIT {limit};
        """
        
        try:
            # Pandas lee la consulta SQL directamente y crea el DataFrame
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error al ejecutar la consulta SQL de Goleadores: {e}")
            return pd.DataFrame()
        finally:
            self.close()

    def get_most_expensive_transfers(self, limit=5):
        """
        Consulta que devuelve las N transferencias más caras de la historia.
        """
        if not self.connect():
            return pd.DataFrame()

        # Convertimos el monto de transferencia a un valor numérico (millones de euros/libras, asumiendo formato)
        # y filtramos las transferencias que no son gratuitas ('0')
        query = f"""
        SELECT
            T1.name AS Player,
            T2.date AS Transfer_Date,
            T2.transfer_fee AS Fee_Text,
            REPLACE(REPLACE(T2.transfer_fee, '€', ''), 'm', '') AS Fee_Numeric,
            T3.name AS Club_In
        FROM players AS T1
        JOIN transfers AS T2 ON T1.player_id = T2.player_id
        JOIN clubs AS T3 ON T2.club_id_in = T3.club_id
        WHERE T2.transfer_fee NOT IN ('-', '?', '€0') 
          AND T2.transfer_fee IS NOT NULL
        ORDER BY 
            -- Ordenar por el valor numérico de la transferencia de forma descendente
            CAST(REPLACE(REPLACE(T2.transfer_fee, '€', ''), 'm', '') AS REAL) DESC
        LIMIT {limit};
        """
        
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error al ejecutar la consulta SQL de Transferencias: {e}")
            return pd.DataFrame()
        finally:
            self.close()


# --- Bloque de Prueba para Verificación ---
if __name__ == '__main__':
    analyzer = DataAnalyzer()
    
    # Prueba 1: Goleadores
    print("\n--- Top 10 Máximos Goleadores Históricos ---")
    top_scorers_df = analyzer.get_top_scorers(limit=10)
    
    if not top_scorers_df.empty:
        # Usamos to_string para imprimir todo el DataFrame sin truncar
        print(top_scorers_df.to_string(index=False))
    else:
        print(" No se pudo obtener el ranking de goleadores. Revisa la base de datos o la codificación.")

    # Prueba 2: Transferencias
    print("\n--- Top 5 Transferencias Más Caras (Estimado) ---")
    top_transfers_df = analyzer.get_most_expensive_transfers(limit=5)

    if not top_transfers_df.empty:
        # Formateo simple del DataFrame para una mejor lectura
        print(top_transfers_df[['Player', 'Club_In', 'Fee_Text', 'Transfer_Date']].to_string(index=False))
    else:
        print(" No se pudo obtener el ranking de transferencias. Revisa la base de datos o los datos de transfer_fee.")