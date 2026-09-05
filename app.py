from flask import Flask, render_template, request, redirect, session, jsonify
import random
import string
from database import crear_tablas, conectar

app = Flask(__name__)
app.secret_key = "song-battle-clave-secreta"
crear_tablas()


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

    cursor.execute(
        """
        UPDATE jugadores
        SET puntos = puntos + ?, pregunta_actual = pregunta_actual + 1
        WHERE id = ? AND pregunta_actual = ?
        """,
        (puntos_ganados, player_id, indice)
    )

    if cursor.rowcount == 0:
        conexion.rollback()
        conexion.close()
        return "Esta pregunta ya fue respondida."

    conexion.commit()

    cursor.execute(
        """
        SELECT puntos, pregunta_actual
        FROM jugadores
        WHERE id = ?
        """,
        (player_id,)
    )

    jugador_actualizado = cursor.fetchone()

    puntos = jugador_actualizado["puntos"]
    indice = jugador_actualizado["pregunta_actual"]

    conexion.close()

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