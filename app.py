from flask import Flask

app = Flask(__name__)


@app.route("/")
def inicio():
    return """
    <h1>🎵 SONG BATTLE</h1>
    <p>Juego interactivo para adivinar canciones</p>
    """


if __name__ == "__main__":
    app.run(debug=True)
