from flask import Flask, jsonify

app = Flask("Xeguridad_Bot_Fask")

@app.route('/')
def home():
    return "Servidor Flask en funcionamiento."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
