# gui/results_view.py (VERSIÓN FINAL QUE USA .ui y GUARDA EL SCORE)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Signal, Qt
from core.database_manager import DatabaseManager # Importación necesaria
import os
import logging

# Define la ruta al archivo .ui
UI_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'results_view.ui')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 

class ResultsView(QWidget):
    # Señales 
    start_new_quiz_request = Signal()
    show_ranking_request = Signal()
    back_to_menu_request = Signal()

    # Variables de estado para el score
    _score = 0
    _total = 0
    _mode = ""

    # Recibe el db_manager de MainWindow para guardar los resultados
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.score_saved = False # Flag para evitar guardar dos veces
        
        # 1. Carga el diseño visual 
        loader = QUiLoader()
        self.ui = loader.load(UI_FILE, self)
        
        if self.ui:
            layout = QVBoxLayout(self)
            layout.addWidget(self.ui)
            layout.setContentsMargins(0, 0, 0, 0)
            self._find_ui_widgets()
        else:
            logger.error(f" ERROR: Archivo .ui no encontrado en {UI_FILE}. No se puede inicializar la vista.")
            return

        # 3. Conexiones
        if self.replay_button:
            self.replay_button.clicked.connect(self.start_new_quiz_request.emit)
        if self.ranking_button:
            # Conectamos directamente el ranking, pero primero guardamos por si el usuario olvidó hacerlo
            self.ranking_button.clicked.connect(self._save_score_and_show_ranking)
        if self.menu_button:
            self.menu_button.clicked.connect(self._save_score_and_go_menu)

        # Conexión del campo de entrada (Player Name)
        if self.name_entry:
             # Conectamos la pulsación de ENTER al guardado
            self.name_entry.returnPressed.connect(self._save_current_score)
            
        # Añadir un botón explícito de "Guardar" si existe en el UI
        # self.save_button = self.ui.findChild(QPushButton, 'btn_save_score') 
        # if self.save_button:
        #     self.save_button.clicked.connect(self._save_current_score)

        self.setStyleSheet("background-color: #2e2e2e; color: white;")
        
    def _find_ui_widgets(self):
        """Busca y asigna los widgets cargados del .ui a variables de instancia."""
        self.title_label = self.ui.findChild(QLabel, 'lbl_title')
        self.score_label = self.ui.findChild(QLabel, 'lbl_score')
        self.name_entry = self.ui.findChild(QLineEdit, 'txt_player_name') # Nuevo widget
        self.replay_button = self.ui.findChild(QPushButton, 'btn_replay')
        self.ranking_button = self.ui.findChild(QPushButton, 'btn_ranking')
        self.menu_button = self.ui.findChild(QPushButton, 'btn_menu')
        
        # Asegura el foco inicial en el campo de nombre
        if self.name_entry:
            self.name_entry.setPlaceholderText("Ingresa tu Nombre...")
            self.name_entry.setFocus()


    def update_results(self, score: int, total: int, mode: str):
        """Actualiza la vista con los resultados de la partida y resetea el estado."""
        self._score = score
        self._total = total
        self._mode = mode
        self.score_saved = False # Permite guardar de nuevo

        mode_text = "CLÁSICA" if "Clasica" in mode else "TEMÁTICA"
        
        if self.title_label:
             self.title_label.setText(" ¡QUIZ TERMINADO! ")
             self.title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #007bff;")
             
        if self.score_label:
            self.score_label.setText(f"Puntuación Final: {score} de {total} ({mode_text})")
            self.score_label.setStyleSheet("font-size: 28px; color: #28a745; margin-bottom: 30px;")

        if self.name_entry:
             self.name_entry.clear()
             self.name_entry.setEnabled(True)
             self.name_entry.setFocus()
             self.name_entry.setStyleSheet("background-color: #444444; color: white; padding: 10px; border: 1px solid #007bff;")


    def _save_current_score(self):
        """Valida el nombre e invoca la función de guardado en la DB."""
        if self.score_saved:
            QMessageBox.information(self, "Ya Guardado", "Tu puntuación ya ha sido guardada en el ranking.")
            return

        player_name = self.name_entry.text().strip()
        
        if not player_name:
            QMessageBox.warning(self, "Error de Nombre", "Por favor, ingresa tu nombre para guardar tu puntuación.")
            self.name_entry.setFocus()
            return

        try:
            self.db_manager.save_score(
                player_name=player_name,
                score=self._score, 
                total_questions=self._total, 
                game_mode=self._mode
            )
            self.score_saved = True
            self.name_entry.setEnabled(False) # Deshabilita la entrada una vez guardado
            self.name_entry.setText(f"{player_name} (Puntaje Guardado)")
            logger.info(f"Score guardado para {player_name}: {self._score}/{self._total} | Modo: {self._mode}")
            QMessageBox.information(self, "¡Éxito!", f"¡{player_name}, tu puntuación ha sido registrada!")

        except Exception as e:
            logger.error(f"Error al guardar score en DB para {player_name}: {e}")
            QMessageBox.critical(self, "Error de Guardado", "Ocurrió un error al intentar guardar la puntuación.")

    def _save_score_and_show_ranking(self):
        """Intenta guardar el score y luego navega al ranking."""
        if not self.score_saved:
            self._save_current_score()
        
        if self.score_saved:
             self.show_ranking_request.emit()

    def _save_score_and_go_menu(self):
        """Intenta guardar el score y luego navega al menú principal."""
        if not self.score_saved:
            self._save_current_score()

        if self.score_saved:
             self.back_to_menu_request.emit()