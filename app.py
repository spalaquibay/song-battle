from flask import Flask, render_template, request, redirect, session, jsonify
import random
import string
from database import crear_tablas, conectar

app = Flask(__name__)
app.secret_key = "song-battle-clave-secreta"
crear_tablas()

partidas = {}

preguntas_prueba = [
    {
        "pregunta": "¿Quién canta Shape of You?",
        "opciones": [
            "Ed Sheeran",
            "Bruno Mars",
            "Justin Bieber",
            "The Weeknd"
        ],
        "correcta": 0
    },
    {
        "pregunta": "¿Quién canta Bad Guy?",
        "opciones": [
            "Taylor Swift",
            "Billie Eilish",
            "Ariana Grande",
            "Dua Lipa"
        ],
        "correcta": 1
    },
    {
        "pregunta": "¿Quién canta Blinding Lights?",
        "opciones": [
            "The Weeknd",
            "Drake",
            "Ed Sheeran",
            "Post Malone"
        ],
        "correcta": 0
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

        # Crear la partida en memoria
        partidas[codigo] = {
            "categoria": categoria,
            "preguntas": preguntas,
            "jugadores": [nickname],
            "puntos": {},
            "estado": "esperando",
            "pregunta_actual": {}
        }

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

        # Guardar los datos del anfitrión en memoria
        partidas[codigo]["puntos"][player_id] = 0
        partidas[codigo]["pregunta_actual"][player_id] = 0

        # Guardar identificación del anfitrión en su sesión
        session["nickname"] = nickname
        session["codigo"] = codigo
        session["player_id"] = player_id

        return redirect(f"/sala/{codigo}")

    return render_template("crear_partida.html")

@app.route("/sala/<codigo>")
def sala(codigo):

    if codigo not in partidas:
        return "La partida no existe."

    partida = partidas[codigo]

    return render_template(
        "sala.html",
        codigo=codigo,
        categoria=partida["categoria"],
        preguntas=partida["preguntas"],
        jugadores=partida["jugadores"]
    )

@app.route("/iniciar/<codigo>", methods=["POST"])
def iniciar(codigo):

    if codigo not in partidas:
        return "La partida no existe."

    partidas[codigo]["estado"] = "jugando"

    return redirect(f"/juego/{codigo}")

@app.route("/estado/<codigo>")
def estado(codigo):

    if codigo not in partidas:
        return jsonify({"estado": "no_existe"})

    return jsonify({
        "estado": partidas[codigo]["estado"]
    })

@app.route("/juego/<codigo>")
def juego(codigo):
    if codigo not in partidas:
        return "La partida no existe."

    partida = partidas[codigo]

    player_id = session.get("player_id")

    if not player_id:
        return "No hay un jugador identificado."

    if player_id not in partida["puntos"]:
        return "El jugador no pertenece a esta partida."

    indice = partida["pregunta_actual"][player_id]

    if indice >= len(preguntas_prueba):
        return render_template(
            "resultado.html",
            resultado="🎉 ¡Partida terminada!",
            puntos=partida["puntos"][player_id],
            puntos_ganados=0,
            siguiente=False,
            codigo=codigo
        )

    pregunta = preguntas_prueba[indice]

    return render_template(
        "juego.html",
        codigo=codigo,
        pregunta=pregunta,
        numero_pregunta=indice + 1,
        total_preguntas=len(preguntas_prueba)
    )

@app.route("/responder/<codigo>", methods=["POST"])
def responder(codigo):
    if codigo not in partidas:
        return "La partida no existe."

    player_id = session.get("player_id")

    if not player_id:
        return "No hay un jugador identificado."

    respuesta = int(request.form["respuesta"])

    partida = partidas[codigo]

    if player_id not in partida["puntos"]:
        return "El jugador no pertenece a esta partida."

    indice = partida["pregunta_actual"][player_id]

    if indice >= len(preguntas_prueba):
        return render_template(
            "resultado.html",
            resultado="🎉 ¡Partida terminada!",
            puntos=partida["puntos"][player_id],
            puntos_ganados=0,
            siguiente=False,
            codigo=codigo
        )

    pregunta = preguntas_prueba[indice]

    # Comprobar respuesta
    if respuesta == pregunta["correcta"]:
        partida["puntos"][player_id] += 1
        resultado = "¡Correcto! 🎉"
        puntos_ganados = 1
    else:
        resultado = "Respuesta incorrecta ❌"
        puntos_ganados = 0

    # Pasar a la siguiente pregunta
    partida["pregunta_actual"][player_id] += 1

    # Guardar puntos y pregunta actual en SQLite
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE jugadores
        SET puntos = ?, pregunta_actual = ?
        WHERE id = ?
        """,
        (
            partida["puntos"][player_id],
            partida["pregunta_actual"][player_id],
            player_id
        )
    )

    conexion.commit()
    conexion.close()

    siguiente = (
        partida["pregunta_actual"][player_id] < len(preguntas_prueba)
    )

    return render_template(
        "resultado.html",
        resultado=resultado,
        puntos=partida["puntos"][player_id],
        puntos_ganados=puntos_ganados,
        siguiente=siguiente,
        codigo=codigo
    )

@app.route("/unirse", methods=["GET", "POST"])
def unirse():
    if request.method == "POST":
        codigo = request.form["codigo"].upper()
        nickname = request.form["nickname"]

        if codigo not in partidas:
            return "La partida no existe."

        # Agregar jugador a la partida en memoria
        partidas[codigo]["jugadores"].append(nickname)

        # Guardar jugador en SQLite
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM partidas WHERE codigo = ?",
            (codigo,)
        )

        partida_db = cursor.fetchone()

        if not partida_db:
            conexion.close()
            return "La partida no existe en la base de datos."

        cursor.execute(
            """
            INSERT INTO jugadores
            (partida_id, nickname, puntos, pregunta_actual)
            VALUES (?, ?, ?, ?)
            """,
            (partida_db["id"], nickname, 0, 0)
        )

        # Obtener el ID único del jugador
        player_id = cursor.lastrowid

        conexion.commit()
        conexion.close()

        # Usar el ID del jugador para controlar su partida
        partidas[codigo]["puntos"][player_id] = 0
        partidas[codigo]["pregunta_actual"][player_id] = 0

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