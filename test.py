from flask_socketio import SocketIO
from flask import make_response, render_template, Blueprint, request, jsonify

from game_entties import get_game

socketio = SocketIO()
test_blueprint = Blueprint('test', __name__)
random_int = 0

def init_app(app):
    socketio.init_app(app)
    app.register_blueprint(test_blueprint)

@socketio.on('update_random_int')
def handle_update_random_int():
    global random_int
    random_int = list(range(10))
    socketio.emit('chat_updated', {'random_int': random_int})

@test_blueprint.route('/send_message', methods=['POST'])
def handle_message():
    data = request.json
    message = data.get('message')

    socketio.emit('message_received', {'message': message})
    return jsonify({'status': 'Message sent'})

@test_blueprint.route('/chat')
def chat_test():
    game = get_game(game_code = request.cookies.get('game_code'))
    chat = game.get_chat()
    return make_response(render_template('chat.html', chat=chat))

@test_blueprint.route('/random_test')
def random_test():
    handle_update_random_int()
    return "Updated"