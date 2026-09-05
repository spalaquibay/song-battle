from flask import Flask, render_template, request, redirect, session, jsonify
import random
import string
from database import crear_tablas, conectar

app = Flask(__name__)
app.secret_key = "song-battle-clave-secreta"
crear_tablas()


preguntas_prueba = [
    {
        "pregunta": "¿Quién canta Shape of You?",
        "opciones": [
            "Ed Sheeran",
            "Bruno Mars",
            "Justin Bieber",
            "The Weeknd"
        ],
        "correcta": 0,
        "cancion_id": 1
    },
    {
        "pregunta": "¿Quién canta Bad Guy?",
        "opciones": [
            "Taylor Swift",
            "Billie Eilish",
            "Ariana Grande",
            "Dua Lipa"
        ],
        "correcta": 1,
        "cancion_id": 2
    },
    {
        "pregunta": "¿Quién canta Blinding Lights?",
        "opciones": [
            "The Weeknd",
            "Drake",
            "Ed Sheeran",
            "Post Malone"
        ],
        "correcta": 0,
        "cancion_id": 1
    }
]


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/crear-partida", methods=["GET", "POST"])
def crear_partida():
    if request.method == "POST":
        nickname = request.form["nickname"]
        categoria = request.form["categoria"]
        preguntas = request.form["preguntas"]

        codigo = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=4
            )
        )


        # Guardar la partida en SQLite
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO partidas
            (codigo, categoria, total_preguntas, estado)
            VALUES (?, ?, ?, ?)
            """,
            (codigo, categoria, int(preguntas), "esperando")
        )

        # Obtener el ID de la partida
        partida_id = cursor.lastrowid

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
        SELECT id, codigo, categoria, total_preguntas, estado
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
        categoria=partida_db["categoria"],
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

    cursor.execute(
        """
        SELECT p.id, p.codigo, j.puntos, j.pregunta_actual
        FROM partidas p
        JOIN jugadores j ON j.partida_id = p.id
        WHERE p.codigo = ? AND j.id = ?
        """,
        (codigo, player_id)
    )

    datos = cursor.fetchone()
    conexion.close()

    if not datos:
        return "El jugador no pertenece a esta partida."

    indice = datos["pregunta_actual"]
    puntos = datos["puntos"]

    if indice >= len(preguntas_prueba):
        return render_template(
            "resultado.html",
            resultado="🎉 ¡Partida terminada!",
            puntos=puntos,
            puntos_ganados=0,
            siguiente=False,
            codigo=codigo
        )

    pregunta = preguntas_prueba[indice]

    # Buscar la canción correspondiente a la pregunta
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT titulo, artista, categoria, archivo
        FROM canciones
        WHERE id = ?
        """,
        (pregunta["cancion_id"],)
    )

    cancion = cursor.fetchone()
    conexion.close()

    return render_template(
        "juego.html",
        codigo=codigo,
        pregunta=pregunta,
        numero_pregunta=indice + 1,
        total_preguntas=len(preguntas_prueba),
        cancion=cancion
    )      

@app.route("/responder/<codigo>", methods=["POST"])
def responder(codigo):
    player_id = session.get("player_id")

    if not player_id:
        return "No hay un jugador identificado."

    respuesta = int(request.form["respuesta"])

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT p.id, j.puntos, j.pregunta_actual
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

    indice = datos["pregunta_actual"]
    puntos = datos["puntos"]

    if indice >= len(preguntas_prueba):
        conexion.close()

        return render_template(
            "resultado.html",
            resultado="🎉 ¡Partida terminada!",
            puntos=puntos,
            puntos_ganados=0,
            siguiente=False,
            codigo=codigo
        )

    pregunta = preguntas_prueba[indice]

    if respuesta == pregunta["correcta"]:
        puntos += 1
        resultado = "¡Correcto! 🎉"
        puntos_ganados = 1
    else:
        resultado = "Respuesta incorrecta ❌"
        puntos_ganados = 0

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

    siguiente = indice < len(preguntas_prueba)

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