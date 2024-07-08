from flask_socketio import SocketIO
from flask import make_response, render_template, Blueprint, request, jsonify

from game_entities import Game, send_message, get_name, load, save

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


def get_figure(map_jso, x, y):
    figures = map_jso['status']['figures']
    for figure in figures:
        if figure['x'] == x and figure['y'] == y:
            return figure
    return None

@chat_blueprint.route('/turn', methods=['POST'])
def turn():
    data = request.json
    tun_from = data.get('from')
    turn_to = data.get('to')
    player_uuid = request.cookies.get('player_uuid')
    game = Game(code=request.cookies.get('game_code'))

    #his turn?
    map_jso = load('map',game.code)
    actual_turn = map_jso['status']['turn']
    users_jso = load('users',game.code)

    #his turn?
    if player_uuid != users_jso['players'][actual_turn]['uuid']:
        return jsonify({'error': 'Not your turn'})

    #his figure?
    figure = get_figure(map_jso, tun_from['x'], tun_from['y'])
    if figure is None:
        return jsonify({'error': 'Empty space'})
    if actual_turn != figure['color']:
        return jsonify({'error': 'Not your figure'})

    #attack on his figure?
    conflict_figure = get_figure(map_jso, tun_from['x'], tun_from['y'])
    if actual_turn == conflict_figure['color']:
        return jsonify({'error': 'Cant attack on your figure'})

    #figure_obj = Figure(figure)
    #if not figure_obj.valid():
    #    return jsonify({'error': 'Invalid move'})
    #TODO figure_obj.conflict(conflict_figure)

    colors_turn = users_jso['colors_turn']
    current_index = colors_turn.index(actual_turn)
    next_index = (current_index + 1) % len(colors_turn)

    save('map',game.code, actual_turn)
    save('users', game.code, users_jso)
    #TODO sent changed
    socketio.emit('turn', {"success": True,'turn': colors_turn[next_index]})
    return jsonify({'error': 'ok'})


@chat_blueprint.route('/get_map')
def get_map():
    game = Game(code = request.cookies.get('game_code'))
    return jsonify(load('map',game.code))