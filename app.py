from flask import Flask, render_template, request, redirect, session, jsonify
import random
import string
from database import crear_tablas, conectar

app = Flask(__name__)
app.secret_key = "song-battle-clave-secreta"
crear_tablas()


preguntas_prueba = [
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Shape of You",
            "Blinding Lights",
            "Levitating",
            "Bad Guy"
        ],
        "correcta": 0,
        "cancion_id": 1,
        "categoria": "pop"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Shape of You",
            "Blinding Lights",
            "As It Was",
            "Bad Guy"
        ],
        "correcta": 1,
        "cancion_id": 2,
        "categoria": "pop"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Levitating",
            "As It Was",
            "Blinding Lights",
            "Shape of You"
        ],
        "correcta": 0,
        "cancion_id": 3,
        "categoria": "pop"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Bad Guy",
            "Shape of You",
            "As It Was",
            "Levitating"
        ],
        "correcta": 0,
        "cancion_id": 4,
        "categoria": "pop"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Blinding Lights",
            "Levitating",
            "Bad Guy",
            "As It Was"
        ],
        "correcta": 3,
        "cancion_id": 5,
        "categoria": "pop"
    },
        {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Smells Like Teen Spirit",
            "We Will Rock You",
            "It's My Life",
            "Sweet Child o' Mine"
        ],
        "correcta": 0,
        "cancion_id": 6,
        "categoria": "rock"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Another One Bites the Dust",
            "We Will Rock You",
            "Smells Like Teen Spirit",
            "Sweet Child o' Mine"
        ],
        "correcta": 1,
        "cancion_id": 7,
        "categoria": "rock"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "We Will Rock You",
            "It's My Life",
            "Another One Bites the Dust",
            "Smells Like Teen Spirit"
        ],
        "correcta": 2,
        "cancion_id": 8,
        "categoria": "rock"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Sweet Child o' Mine",
            "Smells Like Teen Spirit",
            "We Will Rock You",
            "It's My Life"
        ],
        "correcta": 3,
        "cancion_id": 9,
        "categoria": "rock"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "It's My Life",
            "Another One Bites the Dust",
            "Sweet Child o' Mine",
            "Smells Like Teen Spirit"
        ],
        "correcta": 2,
        "cancion_id": 10,
        "categoria": "rock"
    },
        {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Gasolina",
            "Despacito",
            "EOo",
            "Dákiti"
        ],
        "correcta": 0,
        "cancion_id": 11,
        "categoria": "reggaeton"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Gata Only",
            "Despacito",
            "Gasolina",
            "EOo"
        ],
        "correcta": 1,
        "cancion_id": 12,
        "categoria": "reggaeton"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Dákiti",
            "Gata Only",
            "EOo",
            "Gasolina"
        ],
        "correcta": 2,
        "cancion_id": 13,
        "categoria": "reggaeton"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "EOo",
            "Gasolina",
            "Dákiti",
            "Gata Only"
        ],
        "correcta": 2,
        "cancion_id": 14,
        "categoria": "reggaeton"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Despacito",
            "Dákiti",
            "Gasolina",
            "Gata Only"
        ],
        "correcta": 3,
        "cancion_id": 15,
        "categoria": "reggaeton"
    },
        {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Si Antes Te Hubiera Conocido",
            "LALA",
            "Me Rehúso",
            "Columbia"
        ],
        "correcta": 0,
        "cancion_id": 16,
        "categoria": "latina"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Columbia",
            "LALA",
            "Sigo Extrañándote",
            "Si Antes Te Hubiera Conocido"
        ],
        "correcta": 1,
        "cancion_id": 17,
        "categoria": "latina"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Me Rehúso",
            "Si Antes Te Hubiera Conocido",
            "LALA",
            "Sigo Extrañándote"
        ],
        "correcta": 0,
        "cancion_id": 18,
        "categoria": "latina"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "LALA",
            "Sigo Extrañándote",
            "Columbia",
            "Me Rehúso"
        ],
        "correcta": 2,
        "cancion_id": 19,
        "categoria": "latina"
    },
    {
        "pregunta": "🎧 ¿Qué canción estás escuchando?",
        "opciones": [
            "Columbia",
            "Me Rehúso",
            "Si Antes Te Hubiera Conocido",
            "Sigo Extrañándote"
        ],
        "correcta": 3,
        "cancion_id": 20,
        "categoria": "latina"
    }

]



@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/crear-partida", methods=["GET", "POST"])
def crear_partida():
    if request.method == "POST":
        nickname = request.form["nickname"]
        total_preguntas = int(request.form["total_preguntas"])

        codigo = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=4
            )
        )

        # Conectar a SQLite
        conexion = conectar()
        cursor = conexion.cursor()

        # Crear la partida
        cursor.execute(
            """
            INSERT INTO partidas
            (codigo, categoria, total_preguntas, estado)
            VALUES (?, ?, ?, ?)
            """,
            (codigo, "mixto", total_preguntas, "esperando")
        )

        # Obtener el ID de la partida
        partida_id = cursor.lastrowid

        cursor.execute(
            """
            SELECT id, categoria
            FROM canciones
            WHERE categoria IN ('pop', 'rock', 'reggaeton')
            ORDER BY id
            """
        )

        canciones = cursor.fetchall()

        # Seleccionar aleatoriamente 3 o 5 canciones
        canciones_seleccionadas = random.sample(
            canciones,
            total_preguntas
        )

        # Guardar las canciones seleccionadas para esta partida
        for orden, cancion in enumerate(canciones_seleccionadas):
            cursor.execute(
                """
                INSERT INTO preguntas_partida
                (partida_id, cancion_id, orden)
                VALUES (?, ?, ?)
                """,
                (partida_id, cancion["id"], orden)
            )

        # Registrar al anfitrión como jugador
        cursor.execute(
            """
            INSERT INTO jugadores
            (partida_id, nickname, puntos, pregunta_actual)
            VALUES (?, ?, ?, ?)
            """,
            (partida_id, nickname, 0, 0)
        )

        # Obtener ID único del anfitrión
        player_id = cursor.lastrowid

        conexion.commit()
        conexion.close()

        # Guardar identificación del anfitrión en su sesión
        session["nickname"] = nickname
        session["codigo"] = codigo
        session["player_id"] = player_id

        return redirect(f"/sala/{codigo}")

    return render_template("crear_partida.html")

@app.route("/sala/<codigo>")
def sala(codigo):
  

    conexion = conectar()
    cursor = conexion.cursor()

    # Buscar la partida en SQLite
    cursor.execute(
        """
        SELECT id, codigo, total_preguntas, estado
        FROM partidas
        WHERE codigo = ?
        """,
        (codigo,)
    )

    partida_db = cursor.fetchone()

    if not partida_db:
        conexion.close()
        return "La partida no existe en la base de datos."

    # Buscar los jugadores de esa partida
    cursor.execute(
        """
        SELECT nickname
        FROM jugadores
        WHERE partida_id = ?
        """,
        (partida_db["id"],)
    )

    jugadores_db = cursor.fetchall()

    conexion.close()

    # Convertir los resultados a una lista de nombres
    jugadores = [jugador["nickname"] for jugador in jugadores_db]

    return render_template(
        "sala.html",
        codigo=partida_db["codigo"],
        preguntas=partida_db["total_preguntas"],
        jugadores=jugadores
    )


@app.route("/jugadores/<codigo>")
def jugadores(codigo):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT p.id
        FROM partidas p
        WHERE p.codigo = ?
        """,
        (codigo,)
    )

    partida_db = cursor.fetchone()

    if not partida_db:
        conexion.close()
        return jsonify({"jugadores": []})

    cursor.execute(
        """
        SELECT nickname
        FROM jugadores
        WHERE partida_id = ?
        ORDER BY id
        """,
        (partida_db["id"],)
    )

    jugadores_db = cursor.fetchall()
    conexion.close()

    jugadores = [jugador["nickname"] for jugador in jugadores_db]

    return jsonify({
        "jugadores": jugadores
    })

@app.route("/iniciar/<codigo>", methods=["POST"])
def iniciar(codigo):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE partidas
        SET estado = ?
        WHERE codigo = ?
        """,
        ("jugando", codigo)
    )

    if cursor.rowcount == 0:
        conexion.close()
        return "La partida no existe."

    conexion.commit()
    conexion.close()

    return redirect(f"/juego/{codigo}")

@app.route("/estado/<codigo>")
def estado(codigo):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT estado FROM partidas WHERE codigo = ?",
        (codigo,)
    )

    partida_db = cursor.fetchone()
    conexion.close()

    if not partida_db:
        return jsonify({"estado": "no_existe"})

    return jsonify({
        "estado": partida_db["estado"]
    })

@app.route("/juego/<codigo>")
def juego(codigo):
    player_id = session.get("player_id")

    if not player_id:
        return "No hay un jugador identificado."

    conexion = conectar()
    cursor = conexion.cursor()

    # Obtener la partida y el progreso del jugador
    cursor.execute(
        """
        SELECT p.id, p.codigo, p.total_preguntas,
               j.puntos, j.pregunta_actual
        FROM partidas p
        JOIN jugadores j ON j.partida_id = p.id
        WHERE p.codigo = ? AND j.id = ?
        """,
        (codigo, player_id)
    )

    datos = cursor.fetchone()

    if not datos:
        conexion.close()
        return "El jugador no pertenece a esta partida."

    partida_id = datos["id"]
    indice = datos["pregunta_actual"]
    puntos = datos["puntos"]
    total_preguntas = datos["total_preguntas"]

    # Comprobar si la partida ya terminó
    if indice >= total_preguntas:
        conexion.close()

        return render_template(
            "resultado.html",
            resultado="🎉 ¡Partida terminada!",
            puntos=puntos,
            puntos_ganados=0,
            siguiente=False,
            codigo=codigo
        )

    # Obtener la canción correspondiente a esta pregunta
    cursor.execute(
        """
        SELECT c.id, c.titulo, c.artista, c.categoria, c.archivo
        FROM preguntas_partida pp
        JOIN canciones c ON c.id = pp.cancion_id
        WHERE pp.partida_id = ? AND pp.orden = ?
        """,
        (partida_id, indice)
    )

    cancion = cursor.fetchone()

    conexion.close()

    if not cancion:
        return "No se encontró la canción de esta pregunta."

    # Opciones de respuesta
    opciones = [
        "Pop",
        "Rock",
        "Reggaetón"
    ]

    return render_template(
        "juego.html",
        codigo=codigo,
        cancion=cancion,
        numero_pregunta=indice + 1,
        total_preguntas=total_preguntas,
        opciones=opciones
    )

@app.route("/responder/<codigo>", methods=["POST"])
def responder(codigo):
    player_id = session.get("player_id")

    if not player_id:
        return "No hay un jugador identificado."

    respuesta = request.form["respuesta"].lower()

    if respuesta == "reggaetón":
        respuesta = "reggaeton"

    conexion = conectar()
    cursor = conexion.cursor()

    # Obtener la partida y el progreso del jugador
    cursor.execute(
        """
        SELECT p.id, p.total_preguntas,
               j.puntos, j.pregunta_actual
        FROM partidas p
        JOIN jugadores j ON j.partida_id = p.id
        WHERE p.codigo = ? AND j.id = ?
        """,
        (codigo, player_id)
    )

    datos = cursor.fetchone()

    if not datos:
        conexion.close()
        return "El jugador no pertenece a esta partida."

    partida_id = datos["id"]
    indice = datos["pregunta_actual"]
    puntos = datos["puntos"]
    total_preguntas = datos["total_preguntas"]

    # Comprobar si la partida ya terminó
    if indice >= total_preguntas:
        conexion.close()

        return render_template(
            "resultado.html",
            resultado="🎉 ¡Partida terminada!",
            puntos=puntos,
            puntos_ganados=0,
            siguiente=False,
            codigo=codigo
        )

    # Obtener la canción correspondiente a la pregunta actual
    cursor.execute(
        """
        SELECT c.categoria
        FROM preguntas_partida pp
        JOIN canciones c ON c.id = pp.cancion_id
        WHERE pp.partida_id = ? AND pp.orden = ?
        """,
        (partida_id, indice)
    )

    cancion = cursor.fetchone()

    if not cancion:
        conexion.close()
        return "No se encontró la canción de esta pregunta."

    # Comprobar la respuesta
    genero_correcto = cancion["categoria"]

    if respuesta == genero_correcto:
        puntos += 1
        resultado = "¡Correcto! 🎉"
        puntos_ganados = 1
    else:
        resultado = "Respuesta incorrecta ❌"
        puntos_ganados = 0

    # Avanzar a la siguiente pregunta
    indice += 1

    cursor.execute(
        """
        UPDATE jugadores
        SET puntos = ?, pregunta_actual = ?
        WHERE id = ?
        """,
        (puntos, indice, player_id)
    )

    conexion.commit()
    conexion.close()

    # Comprobar si quedan preguntas
    siguiente = indice < total_preguntas

    return render_template(
        "resultado.html",
        resultado=resultado,
        puntos=puntos,
        puntos_ganados=puntos_ganados,
        siguiente=siguiente,
        codigo=codigo
    )


@app.route("/ranking/<codigo>")
def ranking(codigo):

    conexion = conectar()
    cursor = conexion.cursor()

    # Buscar la partida en SQLite
    cursor.execute(
        "SELECT id FROM partidas WHERE codigo = ?",
        (codigo,)
    )

    partida_db = cursor.fetchone()

    if not partida_db:
        conexion.close()
        return "La partida no existe en la base de datos."

    # Obtener los jugadores ordenados por puntos
    cursor.execute(
        """
        SELECT nickname, puntos
        FROM jugadores
        WHERE partida_id = ?
        ORDER BY puntos DESC
        """,
        (partida_db["id"],)
    )

    jugadores = cursor.fetchall()

    conexion.close()

    return render_template(
        "ranking.html",
        jugadores=jugadores,
        codigo=codigo
    )

@app.route("/unirse", methods=["GET", "POST"])
def unirse():
    if request.method == "POST":
        codigo = request.form["codigo"].upper()
        nickname = request.form["nickname"]

        conexion = conectar()
        cursor = conexion.cursor()

        # Buscar la partida en SQLite
        cursor.execute(
            """
            SELECT id, estado
            FROM partidas
            WHERE codigo = ?
            """,
            (codigo,)
        )

        partida_db = cursor.fetchone()

        if not partida_db:
            conexion.close()
            return "La partida no existe."

        # Registrar al jugador en SQLite
        cursor.execute(
            """
            INSERT INTO jugadores
            (partida_id, nickname, puntos, pregunta_actual)
            VALUES (?, ?, ?, ?)
            """,
            (partida_db["id"], nickname, 0, 0)
        )

        player_id = cursor.lastrowid

        conexion.commit()
        conexion.close()

        # Guardar datos del jugador en su sesión
        session["nickname"] = nickname
        session["codigo"] = codigo
        session["player_id"] = player_id

        return render_template(
            "jugador.html",
            codigo=codigo,
            nickname=nickname
        )

    return render_template("unirse.html")


if __name__ == "__main__":
    app.run(debug=True)