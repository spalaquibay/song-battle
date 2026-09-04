from flask import Flask, render_template, request, redirect, session, jsonify
import random
import string
from database import crear_tablas

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

        categoria = request.form["categoria"]
        preguntas = request.form["preguntas"]

        codigo = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=4)
        )

        partidas[codigo] = {
            "categoria": categoria,
            "preguntas": preguntas,
            "jugadores": [],
            "puntos": {},
            "estado": "esperando",
            "pregunta_actual": {}
        }

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
    nickname = session.get("nickname")

    if not nickname:
        return "No hay un jugador identificado."

    if nickname not in partida["pregunta_actual"]:
        partida["pregunta_actual"][nickname] = 0

    indice = partida["pregunta_actual"][nickname]

    if indice >= len(preguntas_prueba):
        return render_template(
            "resultado.html",
            resultado="🎉 ¡Partida terminada!",
            puntos=partida["puntos"][nickname]
        )

    pregunta = preguntas_prueba[indice]

    return render_template(
        "juego.html",
        codigo=codigo,
        preguntas=partida["preguntas"],
        pregunta=pregunta,
        numero_pregunta=indice + 1,
        total_preguntas=len(preguntas_prueba)
    )

@app.route("/responder/<codigo>", methods=["POST"])
def responder(codigo):
    if codigo not in partidas:
        return "La partida no existe."

    nickname = session.get("nickname")

    if not nickname:
        return "No hay un jugador identificado."

    respuesta = int(request.form["respuesta"])

    partida = partidas[codigo]

    if nickname not in partida["puntos"]:
        partida["puntos"][nickname] = 0

    if nickname not in partida["pregunta_actual"]:
        partida["pregunta_actual"][nickname] = 0

    indice = partida["pregunta_actual"][nickname]

    if indice >= len(preguntas_prueba):
        return render_template(
            "resultado.html",
            resultado="🎉 ¡Partida terminada!",
            puntos=partida["puntos"][nickname]
        )

    pregunta = preguntas_prueba[indice]

    if respuesta == pregunta["correcta"]:
        partida["puntos"][nickname] += 1
        resultado = "¡Correcto! 🎉"
        puntos_ganados = 1
    else:
        resultado = "Respuesta incorrecta ❌"
        puntos_ganados = 0

    partida["pregunta_actual"][nickname] += 1

    siguiente = (
        partida["pregunta_actual"][nickname] < len(preguntas_prueba)
    )

    return render_template(
        "resultado.html",
        resultado=resultado,
        puntos=partida["puntos"][nickname],
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

        if nickname not in partidas[codigo]["jugadores"]:
            partidas[codigo]["jugadores"].append(nickname)

        partidas[codigo]["puntos"][nickname] = 0
        partidas[codigo]["pregunta_actual"][nickname] = 0

        session["nickname"] = nickname
        session["codigo"] = codigo
        session["pregunta_actual"] = 0

        return render_template(
            "jugador.html",
            codigo=codigo,
            nickname=nickname
        )

    return render_template("unirse.html")


if __name__ == "__main__":
    app.run(debug=True)