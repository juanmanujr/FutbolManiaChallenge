# insert_test_scores.py
from core.database_manager import DatabaseManager

# Instancia del manager (asegúrate de que la ruta sea correcta)
db_manager = DatabaseManager()

# Lista de puntajes de prueba
test_scores = [
    (8, 10, 'TriviaClasica'),
    (5, 10, 'TriviaClasica'),
    (10, 10, 'TriviaClasica'),
    (7, 10, 'TriviaClasica'),
    (6, 10, 'TriviaClasica'),
]

for score, total, mode in test_scores:
    db_manager.save_score(score, total, mode)
    print(f"Puntaje guardado: {score}/{total} ({mode})")

print(" Inserción de puntajes finalizada.")
