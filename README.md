#  FutbolManía Challenge

###  Descripción
**FutbolManía Challenge** es un juego tipo *quiz futbolero interactivo* desarrollado en **Python** utilizando **PySide6 (Qt for Python)**.  
El objetivo del juego es responder preguntas de fútbol, acumular puntos y competir en un ranking global.

---

###  Estructura del proyecto

FutbolMania/
├── data/ # Archivos CSV con preguntas y datos
├── ui/ # Interfaces creadas en Qt Designer
│ ├── menu_principal.ui
│ ├── mode_selection_view.ui
│ ├── quiz_app.ui
│ ├── ranking_view.ui
│ └── results_view.ui
├── logic/ # (Si corresponde) Archivos de lógica del juego
├── main.py # Archivo principal que inicia la aplicación
└── README.md # Este archivo





###  Funcionalidades principales
-  Carga de preguntas desde archivos CSV.
-  Evaluación de respuestas y cálculo de puntaje.
-  Pantalla de resultados con nombre del jugador.
-  Guardado y visualización del ranking de puntuaciones.
-  Navegación fluida entre todas las pantallas del juego.

---

###  Archivos de datos (CSV utilizados)
El proyecto utiliza múltiples datasets futboleros para generar preguntas y estadísticas, entre ellos:
- `preguntas.csv`
- `WorldCups.csv`
- `UCL_AllTime_Performance_Table.csv`
- `ranking.csv` *(para guardar los puntajes de los jugadores)*

---

###  Tecnologías utilizadas
- **Python 3**
- **PySide6 (Qt Designer)**
- **Pandas** (para manejar CSV)
- **GitHub** (control de versiones)
- **Trello** (organización del proyecto)

---

###  Ejecución del proyecto

#### Requisitos previos:
1. Tener **Python 3.10+** instalado.
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
(si no tenés ese archivo, podés instalar PySide6 y pandas directamente)


pip install PySide6 pandas

Ejecutar el juego:

python main.py

 Organización del proyecto
El desarrollo se gestionó mediante un tablero de Trello con las listas:

Por hacer
En proceso
Hecho

Cada tarjeta representó una tarea específica con fechas actualizadas.

 Autor
Juan Manuel Gómez Achurrarro
Estudiante de Ingeniería Informática – UniNorte Caacupé
 juan.gomez.793@alumnos.uninorte.edu.py

 Enlaces
 Repositorio GitHub: https://github.com/juanmanujr/FutbolManiaChallenge


 Tablero Trello: https://trello.com/invite/b/6909347c45ee222ee3a99cdd/ATTI992482316297ad56ee09a8bd17d390df1E73346D/futbolmania-challenge


