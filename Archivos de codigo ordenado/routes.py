from flask import Flask, request, jsonify
from services import MongoService, WhatsAppService
from config import Config

app = Flask(__name__)
mongo_service = MongoService()

@app.route('/')
def home():
    return "Servidor Flask en funcionamiento."

@app.route('/test_mongodb', methods=['GET'])
def test_mongodb_connection():
    try:
        mongo_service.db.command('ping')
        return jsonify({'status': 'success', 'message': 'Conexión exitosa'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token == Config.VERIFY_TOKEN:
            return str(challenge), 200
        return "Verificación fallida", 403
    elif request.method == 'POST':
        data = request.json
        return jsonify({'status': 'success', 'data': data}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=Config.PORT)
