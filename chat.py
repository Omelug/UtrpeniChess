from flask_socketio import SocketIO
from flask import make_response, render_template, Blueprint, request, jsonify

from game_entities import Game, send_message, get_name, load

socketio = SocketIO()
chat_blueprint = Blueprint('chat', __name__)
random_int = 0

def init_app(app):
    socketio.init_app(app)
    app.register_blueprint(chat_blueprint)

@chat_blueprint.route('/send_message', methods=['POST'])
def handle_message():
    data = request.json
    message = data.get('message')
    game_code = request.cookies.get('game_code')
    name = get_name(game_code, request.cookies.get('player_uuid'))
    send_message(game_code,name, message)
    socketio.emit('message_received', {'name': name, 'message': message})
    return jsonify({'status': 'Message sent'})


@chat_blueprint.route('/chat')
def chat_test():
    game = Game(code = request.cookies.get('game_code'))
    if not game.code:
        return "Game code not found in cookies", 400
    chat = load('chat',game.code)
    return make_response(render_template('chat.html', chat=chat))


@chat_blueprint.route('/turn', methods=['POST'])
def turn():
    data = request.json
    tun_from = data.get('from')
    turn_to = data.get('to')
    player_uuid = request.cookies.get('player_uuid')

    print('turn', tun_from, turn_to, player_uuid)
    return jsonify({'error': 'Not your turn'})
    #return jsonify({'error': 'Invalid move'})


@chat_blueprint.route('/get_map')
def get_map():
    game = Game(code = request.cookies.get('game_code'))
    return jsonify(load('map',game.code))