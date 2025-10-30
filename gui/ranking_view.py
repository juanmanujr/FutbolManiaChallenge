# gui/ranking_view.py (MODIFICACIÓN: Muestra la columna 'NOMBRE' y ajusta índices)

from PySide6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, 
    QPushButton, QLabel, QHeaderView
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Signal, Qt
import pandas as pd
import os
import logging

# Define la ruta relativa al archivo .ui que crearás en Qt Designer
UI_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'ranking_view.ui')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 

class RankingView(QWidget):
    """
    Vista que muestra el ranking de puntajes cargando datos desde DatabaseManager.
    """
    back_to_menu = Signal()

    def __init__(self, db_manager=None):
        super().__init__()
        self.db_manager = db_manager 
        
        # 1. Carga el diseño visual (TU .ui)
        loader = QUiLoader()
        self.ui = loader.load(UI_FILE, self)
        
        if self.ui:
            layout = QVBoxLayout(self)
            layout.addWidget(self.ui)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            logger.error(f" ERROR: Archivo .ui no encontrado en {UI_FILE}. No se puede inicializar la vista.")
            return

        # 2. Encuentra los widgets (los nombres coinciden con tu .ui)
        self.ranking_table = self.ui.findChild(QTableWidget, 'ranking_table')
        self.back_button = self.ui.findChild(QPushButton, 'btn_volver')

        # 3. Conexión y Aplicación de Estilos
        if self.back_button:
            self.back_button.clicked.connect(self.back_to_menu.emit)
        
        if self.ranking_table:
            self.ranking_table.setColumnCount(5) # ¡Aseguramos 5 columnas!
            self.ranking_table.setHorizontalHeaderLabels(['NOMBRE', 'Puntuación', 'Preguntas', 'Modo', 'Fecha'])
            self._setup_table_style()


    def _setup_table_style(self):
        """Aplica estilos QSS y configuración final a la tabla para asegurar que los datos sean visibles."""
        
        # Ocultar el encabezado vertical (los números de fila)
        self.ranking_table.verticalHeader().setVisible(False)
        
        # APLICACIÓN CRÍTICA DE ESTILOS QSS (Esto hace visible el texto)
        self.ranking_table.setStyleSheet("""
            QTableWidget {
                background-color: #444444; 
                gridline-color: #555555;
                color: white; /* ESTO HACE EL TEXTO VISIBLE */
                font-size: 16px;
                border: 1px solid #555555;
            }
            QHeaderView::section { 
                background-color: #555555; 
                color: #007bff; /* Color de los títulos de columna */
                padding: 5px; 
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #3a3a3a; /* Color de las filas pares */
            }
        """)

        # Ajustar el ancho de las columnas
        header = self.ranking_table.horizontalHeader()
        # Columna de Nombre (índice 0) estirado
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # Modo (índice 3) y Fecha (índice 4) ajustados al contenido
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        

    def load_ranking_data(self):
        """Carga y muestra los datos del ranking desde la DB (Llamado desde MainWindow al navegar)."""
        if not self.ranking_table or not self.db_manager:
            logger.warning("RankingView: No se puede cargar el ranking (tabla o DBManager nulo).")
            return

        logger.info("RankingView: Cargando datos desde la base de datos...")
        
        # 1. Obtener datos del ranking (fetch_top_scores debe retornar player_name)
        df = self.db_manager.fetch_top_scores(limit=15)
        
        # 2. Limpiar la tabla antes de llenarla
        self.ranking_table.clearContents()
        self.ranking_table.setRowCount(df.shape[0])

        if df.empty:
            logger.info("RankingView: No hay datos en el ranking.")
            return

        # 3. Llenar la tabla fila por fila (AHORA CON 5 COLUMNAS)
        for row_index, row_data in df.iterrows():
            date_str = pd.to_datetime(row_data['date_played']).strftime('%Y-%m-%d %H:%M')
            
            # Columna 0: NOMBRE (Nuevo)
            self.ranking_table.setItem(row_index, 0, QTableWidgetItem(row_data['player_name'])) 
            
            # Columna 1: Puntuación
            self.ranking_table.setItem(row_index, 1, QTableWidgetItem(str(row_data['score']))) 
            
            # Columna 2: Preguntas
            self.ranking_table.setItem(row_index, 2, QTableWidgetItem(str(row_data['total_questions'])))
            
            # Columna 3: Modo
            self.ranking_table.setItem(row_index, 3, QTableWidgetItem(row_data['game_mode']))
            
            # Columna 4: Fecha
            self.ranking_table.setItem(row_index, 4, QTableWidgetItem(date_str))

        # 4. Ajustar columnas y refrescar visualmente
        self.ranking_table.resizeColumnsToContents()
        self.ranking_table.viewport().update()
        self.ranking_table.repaint()

        logger.info(f"RankingView: Tabla actualizada con {len(df)} registros.")