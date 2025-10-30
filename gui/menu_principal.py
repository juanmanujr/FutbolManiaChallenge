# gui/menu_principal.py (MODIFICADO para Fase III: Redirección a Selección de Modo)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtUiTools import QUiLoader 
from PySide6.QtCore import Signal
import os

# Define la ruta relativa al archivo .ui que crearás en Qt Designer
UI_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'menu_principal.ui')

class MenuPrincipal(QWidget):
    """
    Vista principal que carga el diseño .ui y emite señales de navegación.
    """
   
    start_mode_selection = Signal() 
    show_ranking = Signal()

    def __init__(self):
        super().__init__()
        
        # 1. Carga el diseño visual desde el archivo .ui
        loader = QUiLoader()
        self.ui = loader.load(UI_FILE, self)
        
        if self.ui:
            # Pasa el control del layout del QWidget principal al objeto cargado
            layout = QVBoxLayout(self)
            layout.addWidget(self.ui)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            #  Fallback de emergencia si el archivo .ui no se encuentra
            print(f" ERROR: Archivo .ui no encontrado en {UI_FILE}. Usando layout de emergencia.")
            self._emergency_layout()
            return
            
        # 2. Conexión de los botones (¡CRÍTICO!)
        try:
            # Botón para ir a la Selección de Modo
            btn_jugar = self.ui.findChild(QPushButton, 'btn_jugar')
            if btn_jugar:
             
                # Conecta el botón a la nueva señal start_mode_selection
                btn_jugar.clicked.connect(self.start_mode_selection.emit) 
            else:
                print("ADVERTENCIA: No se encontró el botón 'btn_jugar'. Revisa el Object Name en Qt Designer.")

            # Botón para ir al Ranking
            btn_ranking = self.ui.findChild(QPushButton, 'btn_ranking')
            if btn_ranking:
                btn_ranking.clicked.connect(self.show_ranking.emit)
            else:
                print("ADVERTENCIA: No se encontró el botón 'btn_ranking'. Revisa el Object Name en Qt Designer.")

        except Exception as e:
            print(f"ERROR: Fallo al conectar botones del Menu Principal: {e}")

    def _emergency_layout(self):
        """Layout simple para evitar errores si el .ui no carga."""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Menú Principal de Emergencia. ¡Crea ui/menu_principal.ui!"))