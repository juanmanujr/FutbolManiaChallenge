# gui/main_window.py (VERSIÓN OPTIMIZADA - El guardado ocurre en ResultsView)

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QApplication, QMessageBox
from PySide6.QtCore import Qt
import sys
import logging

# Importa el gestor de la DB.
from core.database_manager import DatabaseManager 
# Importa el generador de preguntas
from logic.quiz_generator import QuizGenerator 

# Importamos las vistas (las pantallas de la aplicación)
from gui.menu_principal import MenuPrincipal
from gui.mode_selection_view import ModeSelectionView 
from gui.ranking_view import RankingView
from gui.quiz_app import QuizApp 
from gui.results_view import ResultsView 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MainWindow(QMainWindow):
    """Clase principal que gestiona la navegación entre vistas usando QStackedWidget."""
    
    # Indices para la navegación (Clave para QStackedWidget)
    MENU_INDEX = 0
    MODE_SELECT_INDEX = 1 
    QUIZ_INDEX = 2 
    RESULTS_INDEX = 3
    RANKING_INDEX = 4

    def __init__(self):
        super().__init__()
        
        # 1. Inicialización de Gestores y Generadores (solo una vez)
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database() 
        
        self.quiz_generator = QuizGenerator() 
        
        self.setWindowTitle("Fútbolmanía - La Leyenda")
        self.setGeometry(100, 100, 850, 650)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")
        
        # 2. Crear el QStackedWidget (El núcleo de la navegación)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 3. Inicializar las vistas (Pasando dependencias)
        self.menu_view = MenuPrincipal() 
        self.mode_select_view = ModeSelectionView(quiz_generator=self.quiz_generator) 
        self.quiz_view = QuizApp(quiz_generator=self.quiz_generator) 
        # IMPORTANTE: Pasamos el DatabaseManager a ResultsView
        self.results_view = ResultsView(db_manager=self.db_manager) 
        self.ranking_view = RankingView(db_manager=self.db_manager) 
        
        # MODIFICACIÓN/MEJORA: Aseguramos que el ranking se cargue la primera vez
        self.ranking_view.load_ranking_data() 
        
        # 4. Añadir vistas al stack 
        self.stacked_widget.addWidget(self.menu_view)  # Index 0
        self.stacked_widget.addWidget(self.mode_select_view) # Index 1
        self.stacked_widget.addWidget(self.quiz_view) # Index 2
        self.stacked_widget.addWidget(self.results_view)  # Index 3
        self.stacked_widget.addWidget(self.ranking_view)  # Index 4
        
        # 5. Conectar señales de navegación
        
        # --- Menú ---
        self.menu_view.start_mode_selection.connect(lambda: self.navigate_to(self.MODE_SELECT_INDEX))
        self.menu_view.show_ranking.connect(self.navigate_to_ranking) 
        
        # --- Selección de Modo ---
        self.mode_select_view.start_selected_quiz.connect(self.start_new_quiz) 
        self.mode_select_view.back_to_menu.connect(lambda: self.navigate_to(self.MENU_INDEX))

        # --- Quiz ---
        # NO guarda aquí, solo inicia la transición a ResultsView
        self.quiz_view.quiz_finished.connect(self.handle_quiz_finished) 
            
        # --- Vista de Resultados ---
        # Conexiones sin cambios, pero ahora ResultsView tiene el DBManager
        self.results_view.start_new_quiz_request.connect(lambda: self.navigate_to(self.MODE_SELECT_INDEX))
        self.results_view.show_ranking_request.connect(self.navigate_to_ranking)
        self.results_view.back_to_menu_request.connect(lambda: self.navigate_to(self.MENU_INDEX))
        
        # --- Ranking ---
        self.ranking_view.back_to_menu.connect(lambda: self.navigate_to(self.MENU_INDEX))

        # Iniciar en el menú
        self.navigate_to(self.MENU_INDEX)

    def navigate_to(self, index):
        """Método seguro para cambiar de vista."""
        self.stacked_widget.setCurrentIndex(index)

    def navigate_to_ranking(self):
        """Recarga los datos y navega al ranking."""
        # Se asegura que la lista de ranking esté actualizada antes de mostrarla
        self.ranking_view.load_ranking_data() 
        self.navigate_to(self.RANKING_INDEX)
        
    def start_new_quiz(self, category: str, game_mode: str):
        """
        Inicializa la vista del quiz con los nuevos parámetros y navega.
        """
        self.quiz_view.start_quiz(category=category, game_mode=game_mode) 
        self.navigate_to(self.QUIZ_INDEX)

    def handle_quiz_finished(self, final_score: int):
        """
        Recibe el score final y transfiere la información a ResultsView, 
        donde se pedirá el nombre del jugador y se guardará.
        """
        total_questions = self.quiz_view.total_questions
        game_mode_to_save = self.quiz_view.current_game_mode 
        
        # 1. Actualizar la Vista de Resultados con los datos para su procesamiento
        self.results_view.update_results(final_score, total_questions, game_mode_to_save)
        
        # 2. Navegar a la Vista de Resultados (donde se pedirá el nombre y se guarda)
        self.navigate_to(self.RESULTS_INDEX)

if __name__ == '__main__':
    # Configuración de Logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())