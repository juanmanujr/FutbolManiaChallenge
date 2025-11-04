# logic/data_analyzer.py

import pandas as pd
from functools import lru_cache 
from datetime import datetime # Para la sugerencia del año dinámico
import logging 
from core.database_manager import DatabaseManager 

# Configuración básica de logging para un mejor seguimiento
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAnalyzer:
    """
    Clase responsable de la consulta a la base de datos (DB) con caché y validación.
    Proporciona data analítica lista para usar por el QuizGenerator.
    """
    #  Conjunto de estadísticas válidas para validación de seguridad
    VALID_STATS = {"goals", "assists", "minutes_played", "yellow_cards", "red_cards", "appearances"}

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.latest_year = self.get_latest_data_year() 

    def get_latest_data_year(self) -> int:
        """Consulta la tabla APPEARANCES para encontrar el año más reciente disponible."""
        query = """
        SELECT SUBSTR(date, 1, 4) AS Year FROM appearances
        ORDER BY date DESC
        LIMIT 1;
        """
        result = self.db_manager.query(query)

        if not result.empty:
            try:
                return int(result.iloc[0]['Year'])
            except ValueError:
                # Usar el año actual como fallback más seguro.
                return datetime.now().year
        else:
            return datetime.now().year


    #  maxsize aumentado para cachear diferentes límites de Top Scorers
    @lru_cache(maxsize=50)
    def get_top_scorers(self, limit: int = 100, min_goals: int = 100) -> pd.DataFrame:
        """Calcula y devuelve una lista de los máximos goleadores históricos."""
        
        query = f"""
        SELECT
            T1.player_id,
            T2.name AS Player_Name,
            SUM(T1.goals) AS Total_Goals
        FROM
            appearances AS T1
        INNER JOIN
            players AS T2 ON T1.player_id = T2.player_id
        GROUP BY
            T1.player_id, T2.name
        HAVING
            Total_Goals >= ?
        ORDER BY
            Total_Goals DESC
        LIMIT ?;
        """
        df = self.db_manager.query(query, params=(min_goals, limit))
        
        if df.empty: 
            logger.warning("No se encontraron Top Scorers (Verifica la tabla 'appearances').")
            #  Devolver DF vacío con las columnas esperadas para evitar fallos de lógica.
            return pd.DataFrame(columns=["player_id", "Player_Name", "Total_Goals"])
        return df


    @lru_cache(maxsize=1)
    def get_ballon_dor_winners(self) -> pd.DataFrame:
        """Obtiene TODOS los rankings de Balón de Oro (ganadores y nominados)."""

        query = """
        SELECT Year, Player, Club, Rank FROM ballon_dor
        WHERE Rank IS NOT NULL
        ORDER BY Year DESC;
        """
        df = self.db_manager.query(query)
        if df.empty: 
            logger.warning("No se encontraron ganadores de Balón de Oro (Verifica la tabla 'ballon_dor').")
            return pd.DataFrame(columns=["Year", "Player", "Club", "Rank"])
        return df
    
    
    #  maxsize aumentado para cachear diferentes ligas
    @lru_cache(maxsize=50) 
    def get_top_performance_by_league(self, league_code: str, stat: str = 'goals', limit: int = 100) -> pd.DataFrame:
        """
        Calcula y devuelve los jugadores con mejor rendimiento para una liga específica 
        en la última temporada COMPLETA.
        """
        
        #  Validación de seguridad contra estadísticas no permitidas
        if stat not in self.VALID_STATS:
            logger.error(f"Estadística no válida: '{stat}'. Se intentó usar 'goals' en su lugar.")
            stat = 'goals' # Fallback seguro
            
        target_season = self.latest_year - 1 
        stat_column = stat # Ya validado como seguro
        
        # Stat_column debe inyectarse vía f-string ya que SQLite no permite placeholders para nombres de columnas.
        query = f"""
        SELECT
            T1.player_id,
            T3.name AS Player_Name,
            T2.name AS Club_Name,
            SUM(T1.{stat_column}) AS Total_Stat
        FROM
            appearances AS T1
        INNER JOIN
            clubs AS T2 ON T1.player_club_id = T2.club_id
        INNER JOIN
            players AS T3 ON T1.player_id = T3.player_id
        WHERE
            T2.domestic_competition_id = ? AND
            T2.last_season = ?
        GROUP BY
            T1.player_id, T3.name, T2.name
        ORDER BY
            Total_Stat DESC
        LIMIT ?;
        """
        
        params = (league_code, target_season, limit)
        df = self.db_manager.query(query, params=params)
        
        if df.empty: 
            logger.warning(f"No se encontró Top {stat.capitalize()} de {league_code} para {target_season}.")
            #  Devolver DF vacío con las columnas esperadas.
            return pd.DataFrame(columns=["player_id", "Player_Name", "Club_Name", f"Total_{stat.capitalize()}"])
            
        return df.rename(columns={'Total_Stat': f'Total_{stat.capitalize()}'})