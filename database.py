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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS canciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            artista TEXT NOT NULL,
            categoria TEXT NOT NULL,
            archivo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preguntas_partida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            cancion_id INTEGER NOT NULL,
            orden INTEGER NOT NULL,
            FOREIGN KEY (partida_id) REFERENCES partidas(id),
            FOREIGN KEY (cancion_id) REFERENCES canciones(id)
        )
    """)


    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada correctamente.")