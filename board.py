import copy
import logging

from flask import make_response, render_template, Blueprint, jsonify, request
import flask_socketio
import figures
from game_entities import Game, send_message, get_name, load, save


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

socketio = flask_socketio.SocketIO()
board_blueprint = Blueprint('board', __name__)
random_int = 0

def init_board(app):
    socketio.init_app(app)
    app.register_blueprint(board_blueprint)

#Player send message
@board_blueprint.route('/send_message', methods=['POST'])
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

@socketio.on('join_board')
def on_join(data):
    game_code = data['game_code']
    flask_socketio.join_room(game_code)


#Player leave chat room
@socketio.on('leave_chat')
def on_leave(data):
    game_code = data['game_code']
    flask_socketio.leave_room(game_code)
    name = get_name(game_code, request.cookies.get('player_uuid'))
    socketio.emit('message_received', {'name': 'SERVER', 'message': f"{name} LEFT"}, room=game_code)

#Player want game chat history
@board_blueprint.route('/chat')
def chat_history():
    game = Game(code = request.cookies.get('game_code'))
    if not game.code:
        return "", 400
    chat = load('chat',game.code)
    return make_response(render_template('chat.html', chat=chat))


def get_figure(x, y, map_jso):
    for key, figure in map_jso['status']['figures'].items():
        if figure['x'] == x and figure['y'] == y:
            return key, figure
    return None, None

def next_color(users_jso, map_jso):
    colors_turn = users_jso['colors_turn']
    current_turn = map_jso['status']['turn']
    return colors_turn[(colors_turn.index(current_turn) + 1) % len(colors_turn)]

TURN_STORAGE = {}
#TODO This maybe move to map specific classes

def turn_start(*args, **kwargs):
    TURN_STORAGE.update({"en_passant":kwargs.get('map_jso')['status']['en_passant']})
    print(TURN_STORAGE)

def turn_end(*args, **kwargs):
    if kwargs.get('moved'):
        if kwargs.get('map_jso')['status']['en_passant'] == TURN_STORAGE.get("en_passant"):
            kwargs.get('map_jso')['status']['en_passant'] = None


@board_blueprint.route('/turn', methods=['POST'])
def turn():
    data = request.json
    active_fig = data.get('id')
    turn_to = data.get('to')
    player_uuid = request.cookies.get('player_uuid')
    game = Game(code=request.cookies.get('game_code'))

    map_jso = load('map',game.code)
    actual_turn = map_jso['status']['turn']
    users_jso = load('users',game.code)

    turn_start(map_jso=map_jso)

    #his turn?
    try:
        if player_uuid != users_jso['players'][actual_turn]['uuid']:
            return jsonify({'error': 'Not your turn'})
    except KeyError:
        return jsonify({'error': f"Not your turn, player {actual_turn} is not here"})

    figure = map_jso['status']['figures'][active_fig]

    logging.info(f"Game {game.code}| figure ({figure['x']};{figure['y']}) to {turn_to}")

    #is someone changing figure?
    if map_jso['status']['changing']:
        return jsonify({'error': f"{actual_turn} is changing figure"})

    # his figure?
    if figure is None:
        return jsonify({'error': 'Empty space'})
    if actual_turn != figure['color']:
        return jsonify({'error': f"Not your ({actual_turn}) figure {figure['color']}"})

    #attack on his figure?
    conflict_id, conflict_figure = get_figure(turn_to['x'], turn_to['y'], map_jso)
    if conflict_figure is not None and actual_turn == conflict_figure['color']:
        return jsonify({'error': 'Cant attack on your figure'})

    figure_obj = figures.get_figure_o(active_fig, figure, map_jso)

    moved = figure_obj.move(to_x=turn_to['x'], to_y=turn_to['y'], target=conflict_figure,socketio=socketio)
    if not moved:
        return jsonify({'error': 'Invalid move'})


    if figures.kill(map_jso, conflict_id):
        socketio.emit('fig_action', {'killed': conflict_id})


    figure['x'] = turn_to['x']
    figure['y'] = turn_to['y']

    socketio.emit('fig_action',{"active_fig": active_fig, "to": data.get('to')}, room=game.code)
    turn_end(moved=moved,map_jso=map_jso,turn=actual_turn)

    save('map', game.code, map_jso)
    save('users', game.code, users_jso)

    # After move (like choose pawn change)
    after_move_response = figure_obj.after_move(socket=socketio, game_code=game.code)
    if after_move_response is not None:
        if after_move_response["action_type"] is "change":
            after_move_response.update({"fig_id":active_fig}) #info for change
            map_jso['status']['changing'] = True
    else: #nothing else, change turn
        map_jso['status']['turn'] = next_color(users_jso, map_jso)
        socketio.emit('fig_action', {'turn': map_jso['status']['turn']}, room=game.code)

    save('map', game.code, map_jso)

    response = {'error': None}
    if after_move_response is not None:
        response.update(after_move_response)
    return jsonify(response)



#Player want load map
@board_blueprint.route('/get_map')
def get_map():
    game_code = request.cookies.get('game_code')
    if game_code is None:
        return jsonify({'error': 'Game code not found in cookies'}), 400
    game = Game(code = game_code)
    return jsonify(load('map',game.code))


@socketio.on('figure_selected')
def handle_figure_selected(data):
    logging.debug(data)
    fig_id = data['fig_id']
    fig_type = data['fig_type']
    game_code = request.cookies.get('game_code')

    map_jso = load('map', game_code)
    users_jso = load('users', game_code)
    figure = map_jso['status']['figures'].get(fig_id)

    if figure:
        figure['fig_type'] = fig_type
        map_jso['status']['turn'] = next_color(users_jso, map_jso)
        map_jso['status']['changing'] = False
        save('map', game_code, map_jso)
        socketio.emit('fig_action', {'change_fig': fig_id, 'fig_type': fig_type}, room=game_code)
    else:
        logging.error(f"Figure with id {fig_id} not found")