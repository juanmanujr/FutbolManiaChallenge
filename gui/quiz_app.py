# gui/quiz_app.py (VERSIÓN FINAL QUE USA .ui)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QSizePolicy
)
from PySide6.QtUiTools import QUiLoader # <--- Importación clave para cargar el .ui
from PySide6.QtCore import Qt, Signal 
from logic.quiz_generator import QuizGenerator
import logging
import os

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE LOGGING
# ----------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 

# Define la ruta al archivo .ui (Debe coincidir con el nombre que creaste)
UI_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'quiz_app.ui')

# ----------------------------------------------------------------------
# CLASE PRINCIPAL DE LA APLICACIÓN
# ----------------------------------------------------------------------

class QuizApp(QWidget):
    # SEÑAL CLAVE: Emite el puntaje final
    quiz_finished = Signal(int)

    # El constructor recibe el QuizGenerator ya cargado
    def __init__(self, quiz_generator=None): 
        super().__init__()
        
        self.quiz_generator = quiz_generator 
        self.current_question = None
        self.score = 0
        self.question_count = 0
        self.total_questions = 10 
        
        # Variables para gestionar la lógica de Modo/Categoría
        self.current_game_mode = "TriviaClasica" 
        self.category_filter = "General" 
        
        # 1. Cargar el diseño .ui
        loader = QUiLoader()
        self.ui = loader.load(UI_FILE, self)
        
        if self.ui:
            # Configura el layout principal para contener el diseño cargado
            self.main_layout = QVBoxLayout(self)
            self.main_layout.addWidget(self.ui)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(15) 
            self._find_ui_widgets() # Llama al nuevo método para buscar widgets
        else:
            logger.error(f" ERROR: Archivo .ui no encontrado en {UI_FILE}. No se puede inicializar la vista.")
            # Opcional: Si el .ui falla, podrías llamar a self.init_ui() de tu versión anterior
            return

        self.setStyleSheet("background-color: #2e2e2e;")
        self.toggle_options(False)

    def _find_ui_widgets(self):
        """Busca y asigna los widgets cargados del .ui a variables de instancia."""
        # Estos objectName DEBEN coincidir con los del archivo quiz_app.ui
        self.score_label = self.ui.findChild(QLabel, 'score_label')
        self.question_label = self.ui.findChild(QLabel, 'question_label')
        self.options_container = self.ui.findChild(QWidget, 'options_container')
        self.control_button = self.ui.findChild(QPushButton, 'control_button')
        
        # Busca los 4 botones de opción por sus objectNames
        self.option_buttons = []
        for i in range(4):
            btn = self.ui.findChild(QPushButton, f'option_btn_{i}')
            if btn:
                self.option_buttons.append(btn)
            
    # --- Estilos y Toggles (Lógica de juego sin cambios) ---

    def toggle_options(self, enable):
        """Habilita/Deshabilita los botones de opción."""
        for btn in self.option_buttons:
            btn.setEnabled(enable)
            if enable:
                self._set_default_button_style(btn)
    
    # NOTA: Esta función DEBE sobreescribir el estilo del .ui para funcionar correctamente
    def _set_default_button_style(self, btn):
        """Estilo base para los botones de opción."""
        btn.setStyleSheet("""
            QPushButton {
                padding: 12px; 
                font-size: 16px;
                border: none;
                border-radius: 4px;
                background-color: #555555;
                color: white;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)

    # start_quiz ahora recibe los parámetros del juego
    def start_quiz(self, category="General", game_mode="TriviaClasica"):
        """
        Inicializa un nuevo quiz con la configuración de modo y categoría.
        Llamado desde MainWindow.
        """
        if self.control_button:
            self.control_button.setVisible(True)

        self.category_filter = category
        self.current_game_mode = game_mode
        self.score = 0
        self.question_count = 0
        
        if self.quiz_generator:
            self.quiz_generator.reset_used_questions()
            
        if self.score_label:
            self.score_label.setText(f"Puntuación: 0/{self.total_questions}")
        
        mode_display = "Clásica" if game_mode == "TriviaClasica" else f"Temática ({category})"
        
        if self.question_label:
            self.question_label.setText(f"¡Modo: {mode_display} ({self.total_questions} preguntas)! Presiona para empezar.")
            self.question_label.setStyleSheet("font-size: 24px; margin: 20px 0; padding: 15px; background-color: #007bff; color: white; border-radius: 5px;")
        
        if self.control_button:
            self.control_button.setText("Comenzar Quiz") 
            self.control_button.setStyleSheet("background-color: #28a745; color: white; padding: 18px; font-size: 20px; margin-top: 30px; border-radius: 8px;")
            self.control_button.setEnabled(True)
            
            try:
                self.control_button.clicked.disconnect()
            except TypeError: 
                pass
            
            self.control_button.clicked.connect(self.next_question)
        logger.info(f"Quiz preparado: Modo={game_mode}, Categoría={category}")


    def next_question(self):
        """Carga y muestra la siguiente pregunta."""
        
        if self.control_button and not self.control_button.isEnabled() and self.question_count > 0:
            logger.warning("next_question: Ignorando clic rápido duplicado.")
            return
            
        if self.control_button:
            self.control_button.setEnabled(False)
        
        if self.quiz_generator is None:
            logger.error("Intentando llamar a next_question sin QuizGenerator.")
            if self.control_button:
                self.control_button.setEnabled(True)
            return

        if self.question_count >= self.total_questions:
            self.end_quiz()
            return
        
        self.question_count += 1
        
        current_question = self.quiz_generator.get_random_question(category=self.category_filter) 
        self.current_question = current_question
        
        if self.current_question and self.question_label:
            question_text = self.current_question['question'].replace('**', '<b>', 1).replace('**', '</b>', 1)
            self.question_label.setText(f"Pregunta {self.question_count}: {question_text}")
            self.question_label.setStyleSheet("font-size: 24px; margin: 20px 0; padding: 15px; background-color: #444444; color: white; border-radius: 5px;")
            
            for i, option in enumerate(self.current_question['options']):
                if i < len(self.option_buttons):
                    btn = self.option_buttons[i]
                    btn.setText(option)
                    self._set_default_button_style(btn)
                    
                    try:
                        btn.clicked.disconnect()
                    except TypeError:
                        pass
                    
                    btn.clicked.connect(lambda checked, text=option: self.check_answer(text)) 

            self.toggle_options(True)
            if self.control_button:
                self.control_button.setText("Siguiente Pregunta")
        else:
            if self.question_label:
                self.question_label.setText("Error: No hay más preguntas únicas disponibles en esta categoría. Finalizando.")
            self.toggle_options(False)
            if self.control_button:
                self.control_button.setEnabled(True)
            self.end_quiz()

    def check_answer(self, selected_option_text):
        """Verifica si la opción seleccionada es correcta."""
        self.toggle_options(False)
        if self.control_button:
            self.control_button.setEnabled(True)
        
        correct_answer = self.current_question['correct_answer']
        is_correct = (selected_option_text == correct_answer)

        if is_correct:
            self.score += 1
            QMessageBox.information(self, "¡Correcto!", "¡Respuesta correcta! Ganaste un punto.")
        else:
            QMessageBox.critical(self, "Incorrecto", f"Respuesta incorrecta. La respuesta correcta era: {correct_answer}")

        if self.score_label:
            self.score_label.setText(f"Puntuación: {self.score}/{self.total_questions}")
        self.highlight_answer(selected_option_text, correct_answer)

    def highlight_answer(self, selected, correct):
        """Colorea los botones para dar feedback."""
        for btn in self.option_buttons:
            if btn.text() == correct:
                btn.setStyleSheet("background-color: #28a745; color: white; padding: 12px; font-size: 16px; border-radius: 4px;")
            elif btn.text() == selected:
                btn.setStyleSheet("background-color: #dc3545; color: white; padding: 12px; font-size: 16px; border-radius: 4px;")
            else:
                self._set_default_button_style(btn)

    def end_quiz(self):
        """Muestra un mensaje de fin de quiz, oculta el botón de control y emite la señal de guardado."""
        if self.question_label:
            self.question_label.setText("Quiz Terminado. Procesando resultados...")
            self.question_label.setStyleSheet("font-size: 24px; margin: 20px 0; padding: 15px; background-color: #f0ad4e; color: white; border-radius: 5px;")
        
        self.toggle_options(False)
        if self.control_button:
            self.control_button.setVisible(False)
        
        self.quiz_finished.emit(self.score)