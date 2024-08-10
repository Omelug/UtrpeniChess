import copy

from flask import make_response, render_template, Blueprint, jsonify, request
import flask_socketio
import figures
from game_entities import Game, send_message, get_name, load, save

socketio = flask_socketio.SocketIO()
chat_blueprint = Blueprint('chat', __name__)
random_int = 0

def init_chat(app):
    socketio.init_app(app)
    app.register_blueprint(chat_blueprint)

#Player send message
@chat_blueprint.route('/send_message', methods=['POST'])
def handle_message():
    data = request.json
    message = data.get('message')
    game_code = request.cookies.get('game_code')
    name = get_name(game_code, request.cookies.get('player_uuid'))
    send_message(game_code,name, message)
    socketio.emit('message_received', {'name': name, 'message': message}, room=game_code)
    return jsonify({'status': 'Message sent'})

#Player join chat room
@socketio.on('join_chat')
def on_join(data):
    game_code = data['game_code']
    flask_socketio.join_room(game_code)
    name = get_name(game_code, request.cookies.get('player_uuid'))
    socketio.emit('message_received', {'name': 'SERVER', 'message': f"{name} JOINED"}, room=game_code)

#Player leave chat room
@socketio.on('leave_chat')
def on_leave(data):
    game_code = data['game_code']
    flask_socketio.leave_room(game_code)
    name = get_name(game_code, request.cookies.get('player_uuid'))
    socketio.emit('message_received', {'name': 'SERVER', 'message': f"{name} LEFT"}, room=game_code)

#Player want game chat history
@chat_blueprint.route('/chat')
def chat_history():
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
            return figure, key
    return None, None

# Player want move!
@chat_blueprint.route('/turn', methods=['POST'])
def turn():
    data = request.json
    active_fig = data.get('id')
    turn_to = data.get('to')
    player_uuid = request.cookies.get('player_uuid')
    game = Game(code=request.cookies.get('game_code'))

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

    print(f"Game {game.code}| figure ({figure['x']};{figure['y']}) to {turn_to}")

    #TODO check if player is chnagina pawn

    # his figure?
    if figure is None:
        return jsonify({'error': 'Empty space'})
    if actual_turn != figure['color']:
        return jsonify({'error': f"Not your ({actual_turn}) figure {figure['color']}"})

    #attack on his figure?
    conflict_figure, key = get_figure(turn_to['x'], turn_to['y'], map_jso)
    if conflict_figure is not None and actual_turn == conflict_figure['color']:
        return jsonify({'error': 'Cant attack on your figure'})

    figure_class = figures.get_fig_class(figure['fig_type'])
    figure_obj = figure_class(active_fig, figure, map_jso)

    killed = copy.deepcopy(conflict_figure)
    moved = figure_obj.move(to_x=turn_to['x'], to_y=turn_to['y'], target=conflict_figure)
    if not moved:
        return jsonify({'error': 'Invalid move'})


    if figures.kill(map_jso, key):
        socketio.emit('fig_action', {'killed': killed})


    figure['x'] = turn_to['x']
    figure['y'] = turn_to['y']

    # info for change player turn
    colors_turn = users_jso['colors_turn']
    current_index = colors_turn.index(actual_turn)
    next_index = (current_index + 1) % len(colors_turn)

    socketio.emit('fig_action',{"active_fig": active_fig, "to": data.get('to')}, room=game.code)

    save('map', game.code, map_jso)
    save('users', game.code, users_jso)

    # After move (like choose pawn change)
    after_move_response = figure_obj.after_move()
    if after_move_response is not None:
        if after_move_response["action_type"] is "change":
            after_move_response.update({"fig_id":active_fig}) #info for change
    else: #nothing else, change turn
        map_jso['status']['turn'] = colors_turn[next_index]
        socketio.emit('fig_action', {'turn': colors_turn[next_index]}, room=game.code)

    save('map', game.code, map_jso)


    response = {'error': None}
    if after_move_response is not None:
        response.update(after_move_response)
    print(response)
    return jsonify(response)


#Player want load map
@chat_blueprint.route('/get_map')
def get_map():
    game = Game(code = request.cookies.get('game_code'))
    return jsonify(load('map',game.code))