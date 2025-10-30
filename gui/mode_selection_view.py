# gui/mode_selection_view.py (VERSIÓN FINAL QUE USA .ui)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QRadioButton, QComboBox, QPushButton
)
from PySide6.QtUiTools import QUiLoader # <--- Importación clave para cargar el .ui
from PySide6.QtCore import Qt, Signal
import os
import logging
from logic.quiz_generator import QuizGenerator 

# Define la ruta al archivo .ui
UI_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'mode_selection_view.ui')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ModeSelectionView(QWidget):
    """
    Vista que permite al usuario seleccionar el modo de juego (Clásica/Temática)
    y la categoría, y emitir una señal para iniciar el quiz.
    """
    # Señales para la navegación en MainWindow
    start_selected_quiz = Signal(str, str) # category, game_mode
    back_to_menu = Signal()

    def __init__(self, quiz_generator: QuizGenerator):
        super().__init__()
        
        self.quiz_generator = quiz_generator 
        self.categories = self.quiz_generator.get_available_categories()
        
        self.selected_mode = "TriviaClasica" 
        self.selected_category = "General" 
        
        # 1. Carga el diseño visual desde el .ui
        loader = QUiLoader()
        self.ui = loader.load(UI_FILE, self)
        
        if self.ui:
            # Configura el layout principal para contener el diseño cargado
            layout = QVBoxLayout(self)
            layout.addWidget(self.ui)
            layout.setContentsMargins(0, 0, 0, 0)
            self._find_ui_widgets() # Llama al nuevo método para buscar widgets
        else:
            logger.error(f" ERROR: Archivo .ui no encontrado en {UI_FILE}. No se puede inicializar la vista.")
            return
            
        # 3. Conexiones
        # Las conexiones ahora llaman a tus métodos existentes, pero desde los nuevos widgets
        if self.rb_clasica:
            # Usamos _set_mode dentro de una lambda que verifica si está checkeado
            self.rb_clasica.toggled.connect(lambda checked: self._set_mode("TriviaClasica") if checked else None)
        if self.rb_tematica:
            self.rb_tematica.toggled.connect(lambda checked: self._set_mode("Tematico") if checked else None)
        if self.cmb_category:
            self.cmb_category.currentTextChanged.connect(self._update_selected_category)
        if self.btn_start_quiz:
            self.btn_start_quiz.clicked.connect(self._start_quiz)
        if self.btn_back:
            self.btn_back.clicked.connect(self.back_to_menu.emit)
            
        # 4. Inicialización
        self._populate_categories()
        # Asegura que el estado inicial de la categoría esté correcto
        self._set_mode("TriviaClasica") # Inicia en modo Clásico


    def _find_ui_widgets(self):
        """Busca y asigna los widgets cargados del .ui a variables de instancia."""
        # Estos objectName DEBEN coincidir con los del archivo mode_selection_view.ui
        self.rb_clasica = self.ui.findChild(QRadioButton, 'rb_clasica')
        self.rb_tematica = self.ui.findChild(QRadioButton, 'rb_tematica')
        self.cmb_category = self.ui.findChild(QComboBox, 'cmb_category')
        self.btn_start_quiz = self.ui.findChild(QPushButton, 'btn_start_quiz')
        self.btn_back = self.ui.findChild(QPushButton, 'btn_back')

        # Si el ComboBox inicia deshabilitado, lo hacemos aquí:
        if self.cmb_category:
             self.cmb_category.setEnabled(False) 
        
    def _populate_categories(self):
        """Llena el QComboBox con las categorías disponibles del QuizGenerator."""
        if not self.cmb_category: return

        self.cmb_category.clear()
        
        # Asegura que 'General' sea una opción si existe
        if 'General' in self.categories:
            self.cmb_category.addItem('General')
            temp_categories = [c for c in self.categories if c != 'General']
        else:
            temp_categories = self.categories
            
        for cat in sorted(temp_categories):
            self.cmb_category.addItem(cat)
            
        # Establece el valor inicial
        self.selected_category = self.cmb_category.currentText()
        
    def _set_mode(self, mode: str):
        """
        Actualiza el modo seleccionado y controla la interfaz (habilita/deshabilita ComboBox).
        """
        self.selected_mode = mode
        is_tematico = (mode == "Tematico")
        
        # Habilita/Deshabilita el selector de categoría
        if self.cmb_category:
            self.cmb_category.setEnabled(is_tematico)
        
        if not is_tematico:
            # Si volvemos a Clásico, la categoría es "General"
            self.selected_category = "General"
            
            # Sincroniza visualmente el ComboBox a "General" si existe
            if self.cmb_category:
                index = self.cmb_category.findText('General')
                if index != -1:
                    self.cmb_category.setCurrentIndex(index)
            
        logger.info(f"Modo seleccionado: {self.selected_mode}. Categoría activa: {self.selected_category}")

    def _update_selected_category(self, text: str):
        """Actualiza la categoría seleccionada por el usuario en el ComboBox."""
        if self.cmb_category and self.cmb_category.isEnabled():
            self.selected_category = text
        
    def _start_quiz(self):
        """Emite la señal para que MainWindow inicie el Quiz con los parámetros seleccionados."""
        
        category_to_use = self.selected_category
        mode_to_save = self.selected_mode
        
        # Si está en modo Clásico, siempre jugamos la categoría General
        if mode_to_save == "TriviaClasica":
            category_to_use = "General"
        
        logger.info(f"Iniciando Quiz: Modo={mode_to_save}, Categoría={category_to_use}")
        
        # Emitimos la categoría (para el generador) y el modo (para guardar en la DB)
        self.start_selected_quiz.emit(category_to_use, mode_to_save)