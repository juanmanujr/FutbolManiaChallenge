# logic/quiz_generator.py

import pandas as pd
import random
import time 
from typing import Dict, Any, List, Optional
import logging 
import os 

# Importamos las clases core
from core.database_manager import DatabaseManager
from logic.data_analyzer import DataAnalyzer 

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE LOGGING
# ----------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 

class QuizGenerator:
    """
    Genera preguntas de trivia de fútbol basándose ÚNICAMENTE en preguntas fijas 
    cargadas desde la base de datos para máxima velocidad y variedad de contenido propio.
    """
    
    # Mapeo de prefijos rotos a sus nombres correctos para la UX
    PREFIX_MAPPING = {
        'aradona': 'Maradona',
        'ruyff': 'Cruyff',
        'eymar': 'Neymar',
        'ele': 'Pele',
        'eckenbauer': 'Beckenbauer',
    }
    
    def __init__(self):
        self.db = DatabaseManager() 
        self.analyzer = DataAnalyzer() 
        self.AVAILABLE_LEAGUES = ['GB1', 'ES1', 'IT1', 'FR1', 'DE1']

        self.used_questions: set = set()

        # --- Carga de Cachés Dinámicos: ESTABLECIDOS COMO VACÍOS (Acelera la inicialización) ---
        self.scorers_cache = pd.DataFrame()
        self.ballon_dor_cache = pd.DataFrame()
        self.league_scorers_cache = {}
        self.league_assists_cache = {}
        
        #  CACHÉ PRINCIPAL: Preguntas Fijas Generales (Es la única que se carga realmente)
        self.general_questions_cache = self._load_general_questions_cache()
        
        # Diccionario que mapea nombres de preguntas a sus métodos generadores
        self.question_types = {
            'general_quiz_question': self._generate_general_question, 
        }
        
        # Valida qué tipos de preguntas tienen data cargada para usarlos (Solo será 'general_quiz_question')
        self.available_question_types = self._get_available_question_types()
        
        logger.info("QuizGenerator inicializado. Listo para generar preguntas.")

    def reset_used_questions(self):
        """Limpia el historial de preguntas usadas para permitir un nuevo quiz."""
        self.used_questions.clear()
        logger.info("Historial de preguntas usadas reseteado.")

    #  Simplificación y Corrección de Nombres
    def get_available_categories(self) -> List[str]:
        """
        Consulta la tabla 'quiz_questions', corrige prefijos, agrupa por el prefijo
        y retorna una lista de categorías simplificadas para mostrar al usuario.
        """
        try:
            # 1. Obtener todas las categorías únicas del caché
            categories_raw = self.general_questions_cache['Type'].dropna().unique().tolist()
            categories_raw = [str(c).strip() for c in categories_raw if c]
            
            # 2. Simplificar, agrupar y corregir
            simplified_categories = set()
            for cat in categories_raw:
                
                # Obtener el prefijo (parte antes del primer '_')
                simplified = cat.split('_')[0]
                
                # Aplicar corrección si el prefijo está roto (ej: 'ruyff' -> 'Cruyff')
                if simplified in self.PREFIX_MAPPING:
                    simplified = self.PREFIX_MAPPING[simplified]
                
                # Excluimos nombres vacíos o muy cortos
                if len(simplified) > 2:
                    simplified_categories.add(simplified)
            
            # 3. Formato final y adición de 'General'
            categories_final = sorted(list(simplified_categories))
            
            # Asegurar que 'General' esté siempre en la lista
            if "General" not in categories_final:
                categories_final.insert(0, "General")
            
            logger.debug(f"Categorías simplificadas disponibles: {categories_final}")
            return categories_final

        except Exception as e:
            logger.error(f"Error al obtener categorías simplificadas: {e}")
            return ["General"] 


    # --- Métodos de Carga de Cachés ---

    def _load_general_questions_cache(self) -> pd.DataFrame:
        """Carga el caché de las preguntas generales fijas desde la DB."""
        logger.info("Cargando Banco de Preguntas Generales Fijas...")
        TABLE_NAME = "quiz_questions"
        
        try:
            df = self.db.query(f"SELECT * FROM {TABLE_NAME};") 
            
            if df.empty:
                logger.warning(f"La tabla {TABLE_NAME} está vacía (0 filas).")
                
            # CRÍTICO: Aseguramos que la columna 'Type' exista para filtrado
            if 'Type' not in df.columns:
                df['Type'] = 'General'
                logger.warning("Columna 'Type' no encontrada, asignando 'General' por defecto.")
                
            df['Type'] = df['Type'].astype(str).str.strip()
            
            logger.info(f"Cargadas {len(df)} preguntas generales.")
            return df
            
        except Exception as e:
            logger.error(f"Error al cargar/acceder la tabla de preguntas generales ({TABLE_NAME}): {e}")
            return pd.DataFrame()

    # Otros métodos de carga omitidos por ser esqueletos
    def _load_scorers_cache(self) -> pd.DataFrame:
        logger.debug("Omitting Top Scorers Cache load for speed.")
        return pd.DataFrame()

    def _load_ballon_dor_cache(self) -> pd.DataFrame:
        logger.debug("Omitting Ballon d'Or Cache load for speed.")
        return pd.DataFrame()

    def _load_league_performance_cache(self, stat: str) -> Dict[str, pd.DataFrame]:
        logger.debug(f"Omitting Top {stat.capitalize()} Cache load for speed.")
        return {}
    # FIN DE FUNCIONES DE CARGA DINÁMICA


    #  FUNCIÓN DE DISPONIBILIDAD 
    def _get_available_question_types(self) -> List[str]:
        """
        Verifica qué tipos de preguntas tienen datos disponibles.
        """
        if not self.general_questions_cache.empty:
            logger.info(f"Usando SOLO preguntas generales fijas ({len(self.general_questions_cache)} disponibles) para mantener la variedad deseada.")
            return ['general_quiz_question'] 
        
        logger.error("¡ERROR FATAL! No hay datos disponibles para generar preguntas.")
        return []

    # --- Generación de Distractores y Auxiliares (Sin cambios) ---
    def _get_distractors(self, df: pd.DataFrame, correct_name: str, column_name: str, num_distractors: int = 3) -> List[str]:
        # ... (Lógica de distractores) ...
        try:
            potential_distractors = df[df[column_name] != correct_name][column_name].tolist()
            potential_distractors = list(set(potential_distractors))
            
            if len(potential_distractors) < num_distractors:
                num_distractors = len(potential_distractors)
            
            return random.sample(potential_distractors, num_distractors)
            
        except Exception as e:
            return []

    # ... (Generadores de preguntas específicas omitidos) ...
    def _generate_top_scorer_question(self) -> Optional[Dict[str, Any]]:
        df = self.scorers_cache
        if df.empty: return None
        return None 

    def _generate_ballon_dor_question(self) -> Optional[Dict[str, Any]]:
        df = self.ballon_dor_cache
        if df.empty: return None
        return None

    def _generate_league_scorer_question(self) -> Optional[Dict[str, Any]]:
        if not self.league_scorers_cache: return None
        return None

    def _generate_league_assists_question(self) -> Optional[Dict[str, Any]]:
        if not self.league_assists_cache: return None
        return None
        
    #  GENERADOR: Preguntas de conocimiento general 
    #  Filtrado por Prefijo (incluyendo los corregidos)
    def _generate_general_question(self, category: str = "General") -> Optional[Dict[str, Any]]:
        """Genera una pregunta a partir del banco de preguntas fijas, filtrando por el prefijo de categoría."""
        
        df = self.general_questions_cache
        if df.empty: 
            logger.warning("El caché de preguntas generales está vacío.")
            return None

        #  FILTRADO CRÍTICO: Usamos el nombre simplificado para buscar todas las subcategorías
        if category and category != "General":
            
            # 1. Determinamos qué prefijos reales buscamos en la columna 'Type' de la DB
            search_prefixes = [category]
            
            # 2. Si la categoría simplificada coincide con un nombre corregido (ej. 'Maradona'),
            #    también buscamos su versión original rota (ej. 'aradona') en la DB.
            reverse_mapping = {v: k for k, v in self.PREFIX_MAPPING.items()}
            if category in reverse_mapping:
                search_prefixes.append(reverse_mapping[category])

            # 3. Construimos la máscara de filtrado
            # Busca categorías que comienzan con el prefijo o que son exactamente el prefijo (ej: 'CAN' o 'CAN_Historia')
            mask = df['Type'].str.startswith(tuple(p + '_' for p in search_prefixes), na=False) | \
                   (df['Type'].isin(search_prefixes))

            filtered_df = df[mask]
            
            if filtered_df.empty:
                # Si el filtro específico falla, volvemos al DF original para que el fallback general
                # en get_random_question maneje la búsqueda, evitando el doble filtro aquí.
                # Devolvemos None aquí si no encontramos nada específico
                logger.debug(f"No se encontraron preguntas para el prefijo: {category} o subcategoría.")
                return None
        else:
            # Si es General, usa el DF completo
            filtered_df = df

        # Selecciona una fila del DataFrame filtrado
        if filtered_df.empty:
            logger.warning("El DataFrame filtrado quedó vacío. Imposible generar pregunta.")
            return None

        question_row = filtered_df.sample(n=1).iloc[0]
        
        correct_answer = str(question_row['Correct_Answer']).strip()
        incorrect_options_text = str(question_row['Options']).strip()
        incorrect_options = [opt.strip() for opt in incorrect_options_text.split(';') if opt.strip()]
        question_slug = str(question_row['Question']).strip()

        return {
            'type': 'general_quiz_question',
            'question': question_slug,
            'correct_answer': correct_answer,
            'options': incorrect_options, 
            'hint': f"Tema: {str(question_row.get('Type', 'General')).strip()}",
        }


    # --- Método Principal de Generación (CON LÓGICA DE FALLBACK A 'General') ---
    def get_random_question(self, category: str = "General") -> Optional[Dict[str, Any]]:
        """
        Selecciona un tipo de pregunta aleatorio de los disponibles, 
        genera la pregunta y garantiza un formato estándar, filtrando por categoría.
        """
        if not self.available_question_types:
            logger.error("No hay tipos de preguntas disponibles para generar.")
            return None

        # --------------------------------------------------------
        # PRIMER INTENTO (Específico): Generar pregunta de la categoría solicitada
        # --------------------------------------------------------
        for _ in range(20): 
            q_type = random.choice(self.available_question_types)
            generator_func = self.question_types[q_type]
            
            # Pasa la categoría específica
            question_data = generator_func(category=category) 

            if question_data and question_data['question'] not in self.used_questions:
                logger.debug(f"Pregunta generada (Específica): {q_type} (Categoría: {category})")
                return self._format_question_data(question_data)

            elif question_data and question_data['question'] in self.used_questions:
                logger.debug("Pregunta ya usada (Específica), intentando generar otra.")
            
            # Si question_data es None, es porque _generate_general_question no encontró 
            # preguntas para la categoría específica (ej: CAN).

        logger.warning(f"Fallo en 20 intentos para la categoría '{category}'. Intentando con 'General'.")
        
        # --------------------------------------------------------
        # SEGUNDO INTENTO (Fallback): Generar pregunta de la categoría 'General'
        # --------------------------------------------------------
        if category != "General":
            for _ in range(20):
                q_type = random.choice(self.available_question_types)
                generator_func = self.question_types[q_type]
                
                # Pasa la categoría 'General' para el fallback
                question_data = generator_func(category="General")
                
                if question_data and question_data['question'] not in self.used_questions:
                    logger.debug(f"Pregunta generada (FALLBACK): {q_type} (Categoría: General)")
                    return self._format_question_data(question_data)
                
                elif question_data and question_data['question'] in self.used_questions:
                    logger.debug("Pregunta ya usada (General), intentando generar otra.")

        logger.warning("Fallo al generar una pregunta única después de 40 intentos (Específica + General).")
        return None 

    def _format_question_data(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica el formato final, mezcla opciones y registra la pregunta como usada."""
        correct = question_data['correct_answer']
        options = question_data.get('options', [])
        
        # 1. Asegurar que la respuesta correcta esté en las opciones
        if correct not in options:
            options.append(correct)
            
        final_options = options
        
        # 2. Si hay demasiadas opciones, seleccionar 3 distractores al azar + la correcta
        if len(final_options) > 4:
            options_without_correct = [o for o in options if o != correct]
            num_distractors = min(3, len(options_without_correct))
            distractors = random.sample(options_without_correct, num_distractors)
            final_options = distractors + [correct]
            
        # 3. Mezclar y aplicar
        random.shuffle(final_options)
        question_data['options'] = final_options
        self.used_questions.add(question_data['question'])
        
        return question_data