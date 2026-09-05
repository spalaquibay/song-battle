import sqlite3

DATABASE = "database.db"


def conectar():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas():

    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla de partidas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            categoria TEXT NOT NULL,
            total_preguntas INTEGER NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    # Tabla de jugadores
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

    # Tabla de canciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS canciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            artista TEXT NOT NULL,
            categoria TEXT NOT NULL,
            archivo TEXT NOT NULL
        )
    """)

    # Tabla de preguntas de cada partida
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

    # Cargar las 15 canciones si la tabla está vacía
    cursor.execute("SELECT COUNT(*) AS total FROM canciones")
    total_canciones = cursor.fetchone()["total"]

    if total_canciones == 0:

        canciones = [

            # =========================
            # POP
            # =========================

            (
                "Shape of You",
                "Ed Sheeran",
                "pop",
                "audio_pop_1.mp3"
            ),

            (
                "Blinding Lights",
                "The Weeknd",
                "pop",
                "audio_pop_2.mp3"
            ),

            (
                "Levitating",
                "Dua Lipa",
                "pop",
                "audio_pop_3.mp3"
            ),

            (
                "Bad Guy",
                "Billie Eilish",
                "pop",
                "audio_pop_4.mp3"
            ),

            (
                "As It Was",
                "Harry Styles",
                "pop",
                "audio_pop_5.mp3"
            ),

            # =========================
            # ROCK
            # =========================

            (
                "Smells Like Teen Spirit",
                "Nirvana",
                "rock",
                "audio_rock_1.mp3"
            ),

            (
                "We Will Rock You",
                "Queen",
                "rock",
                "audio_rock_2.mp3"
            ),

            (
                "Another One Bites the Dust",
                "Queen",
                "rock",
                "audio_rock_3.mp3"
            ),

            (
                "It's My Life",
                "Bon Jovi",
                "rock",
                "audio_rock_4.mp3"
            ),

            (
                "Sweet Child o' Mine",
                "Guns N' Roses",
                "rock",
                "audio_rock_5.mp3"
            ),

            # =========================
            # REGGAETÓN
            # =========================

            (
                "Gasolina",
                "Daddy Yankee",
                "reggaeton",
                "audio_reggaeton_1.mp3"
            ),

            (
                "Despacito",
                "Luis Fonsi ft. Daddy Yankee",
                "reggaeton",
                "audio_reggaeton_2.mp3"
            ),

            (
                "EOo",
                "Bad Bunny",
                "reggaeton",
                "audio_reggaeton_3.mp3"
            ),

            (
                "Dákiti",
                "Bad Bunny ft. Jhay Cortez",
                "reggaeton",
                "audio_reggaeton_4.mp3"
            ),

            (
                "Gata Only",
                "FloyyMenor & Cris Mj",
                "reggaeton",
                "audio_reggaeton_5.mp3"
            )
        ]

        cursor.executemany("""
            INSERT INTO canciones
            (titulo, artista, categoria, archivo)
            VALUES (?, ?, ?, ?)
        """, canciones)

        conexion.commit()

    conexion.close()


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada correctamente.")