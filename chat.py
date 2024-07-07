from flask_socketio import SocketIO
from flask import make_response, render_template, Blueprint, request, jsonify

from game_entities import Game, send_message

socketio = SocketIO()
chat_blueprint = Blueprint('test', __name__)
random_int = 0

def init_app(app):
    socketio.init_app(app)
    app.register_blueprint(chat_blueprint)

@chat_blueprint.route('/send_message', methods=['POST'])
def handle_message():
    data = request.json
    message = data.get('message')
    send_message(request.cookies.get('game_code'), request.cookies.get('player_uuid'),message)
    socketio.emit('message_received', {'message': message})
    return jsonify({'status': 'Message sent'})


@chat_blueprint.route('/chat')
def chat_test():
    game = Game(code = request.cookies.get('game_code'))
    chat = game.get_chat()
    return make_response(render_template('chat.html', chat=chat))