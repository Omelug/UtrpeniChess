import copy

from flask_socketio import SocketIO
from flask import make_response, render_template, Blueprint, request, jsonify

import figures
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


def get_figure(x, y, map_jso):
    fig_keys= map_jso['status']['figures'].keys()
    for key in fig_keys:
        figure = map_jso['status']['figures'][key]
        if figure['x'] == x and figure['y'] == y:
            return figure
    return None

@chat_blueprint.route('/turn', methods=['POST'])
def turn():
    data = request.json
    active_fig = data.get('id')
    turn_to = data.get('to')
    player_uuid = request.cookies.get('player_uuid')
    game = Game(code=request.cookies.get('game_code'))

    print(f"Turn {active_fig} to {turn_to}")

    #TODO to x,y on board?

    #his turn?
    map_jso = load('map',game.code)
    actual_turn = map_jso['status']['turn']
    users_jso = load('users',game.code)

    #his turn?
    try:
        if player_uuid != users_jso['players'][actual_turn]['uuid']:
            return jsonify({'error': 'Not your turn'})
    except KeyError:
        return jsonify({'error': f"Not your turn, player {actual_turn} is not here"})


    figure = map_jso['status']['figures'][active_fig]

    # his figure?
    if figure is None:
        return jsonify({'error': 'Empty space'})
    if actual_turn != figure['color']:
        return jsonify({'error': f"Not your ({actual_turn}) figure {figure['color']}"})

    #attack on his figure?
    conflict_figure = get_figure(turn_to['x'], turn_to['y'], map_jso)
    if conflict_figure is not None and actual_turn == conflict_figure['color']:
        return jsonify({'error': 'Cant attack on your figure'})

    figure_class = figures.FIGURE_CLASSES[figure['fig_type']]
    figure_obj = figure_class(active_fig, figure, map_jso)

    killed_copy = copy.deepcopy(conflict_figure)
    moved = figure_obj.move(to_x=turn_to['x'], to_y=turn_to['y'], target=conflict_figure)
    if not moved:
        return jsonify({'error': 'Invalid move'})

    response_json = {}
    if figures.kill(map_jso, conflict_figure):
        response_json.update({'killed': killed_copy})

    colors_turn = users_jso['colors_turn']
    current_index = colors_turn.index(actual_turn)
    next_index = (current_index + 1) % len(colors_turn)
    map_jso['status']['turn'] = colors_turn[next_index]

    figure['x'] = turn_to['x']
    figure['y'] = turn_to['y']

    save('map',game.code, map_jso)
    save('users', game.code, users_jso)

    response_json.update({"active_fig": active_fig, "to": data.get('to'), 'turn': colors_turn[next_index]})
    socketio.emit('turn_move', response_json)
    return jsonify({'error': None})


@chat_blueprint.route('/get_map')
def get_map():
    game = Game(code = request.cookies.get('game_code'))
    return jsonify(load('map',game.code))