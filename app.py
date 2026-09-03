from flask import Flask, render_template, request, redirect
import random
import string

app = Flask(__name__)

partidas = {}


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
            "jugadores": []
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


@app.route("/unirse", methods=["GET", "POST"])
def unirse():

    if request.method == "POST":

        codigo = request.form["codigo"].upper()
        nickname = request.form["nickname"]

        if codigo not in partidas:
            return "La partida no existe."

        partidas[codigo]["jugadores"].append(nickname)

        return render_template(
            "jugador.html",
            codigo=codigo,
            nickname=nickname
        )

    return render_template("unirse.html")


if __name__ == "__main__":
    app.run(debug=True)