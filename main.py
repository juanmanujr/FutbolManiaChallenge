# main.py

import os
import time
import io
import sys
import logging
from PySide6.QtWidgets import QApplication
from core.database_manager import DatabaseManager
from gui.main_window import MainWindow  

# =================================================================
# CONFIGURACIÓN INICIAL
# =================================================================

# 1. Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 2. Corrección de Codificación (UTF-8)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# =================================================================
# FUNCIÓN DE SETUP DE DATOS (Optimizado para la carga mínima)
# =================================================================

def setup_data():
    """
    Inicializa la base de datos de forma simple, garantizando que
    los datos de preguntas fijas y la tabla Ranking existan antes de
    iniciar la GUI.
    """
    db_manager = DatabaseManager()
    
    # Verificamos si el archivo DB existe antes de cualquier operación
    db_exists_before = os.path.exists(db_manager.db_path)
    
    start_time = time.time() # Inicia el cronómetro
    
    # initialize_database() se encarga de:
    # 1. Cargar las preguntas (si el archivo DB NO existe)
    # 2. Asegurar que la tabla Ranking exista (SIEMPRE)
    db_manager.initialize_database()

    end_time = time.time()
    
    # Mensaje de retroalimentación
    if not db_exists_before:
        logger.info(f"FASE II COMPLETADA: Carga inicial de preguntas fijas tomó {end_time - start_time:.2f} segundos.")
    else:
        logger.info("Base de datos ya existente. Saltando la carga inicial de preguntas.")
    
    return db_manager 
# =================================================================
# PUNTO DE ARRANQUE PRINCIPAL
# =================================================================

if __name__ == '__main__':
    
    # 1. Garantizar que la DB y los datos mínimos estén listos
    setup_data() 
    
    # 2.  INICIAMOS LA APLICACIÓN GRÁFICA
    logger.info("Iniciando la aplicación Fútbolmanía...")
    
    try:
        # A. Crear la instancia de QApplication
        app = QApplication(sys.argv)
        
        # B. Crear la ventana principal (que contiene toda la navegación)
        main_window = MainWindow()
        main_window.show()
        
        # C. Ejecutar el bucle de eventos de la aplicación
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Error CRÍTICO al iniciar la aplicación gráfica: {e}")
        sys.exit(1)




        