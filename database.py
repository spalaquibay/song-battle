import sqlite3

DATABASE = "database.db"


def conectar():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            categoria TEXT NOT NULL,
            total_preguntas INTEGER NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            nickname TEXT NOT NULL,
            puntos INTEGER DEFAULT 0,
            pregunta_actual INTEGER DEFAULT 0,
            FOREIGN KEY (partida_id) REFERENCES partidas(id)
        )
    """)

    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada correctamente.")