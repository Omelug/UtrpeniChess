import os.path
from flask_cors import CORS
from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory, jsonify
from flask_socketio import SocketIO, join_room, leave_room

from board import init_board
from game_entities import Game, get_uuid


app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins
socketio = SocketIO(app,cors_allowed_origins="*")
init_board(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/javascript/<path:filename>')
def custom_static(filename):
    return send_from_directory('javascript', filename)

@app.route('/')
def home():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    return render_template('index.html')

#Player join to board
@socketio.on('join')
def on_join(data):
    join_room(data['game_code'])

#TODO this is useless now
#Player leave board
@socketio.on('leave')
def on_leave(data):
    leave_room(data['game_code'])


def player_connect(game, create_data):
    response = make_response(jsonify({'redirect': url_for('board')}))
    response.set_cookie('game_code', game.code, samesite='None',secure=False)

    uuid = request.cookies.get('player_uuid')
    if uuid is None:
        uuid = get_uuid()
        response.set_cookie('player_uuid', uuid, samesite='None', secure=False)

    added, color, jso_users = game.connect_player(
        uuid, name=create_data.get('player_name'),
    )

    if added:
        response.set_cookie('view', str(jso_users['view'][color]), samesite='None', secure=False)
        return response
    return make_response(jsonify({'error': "Game is probably full"}))

@app.route('/create_game', methods=['POST'])
def create_game():
    create_data = request.json
    game = Game()
    game.create_new(create_data)
    return player_connect(game, create_data)


@app.route('/connect_to_game', methods=['POST'])
def connect_to_game():
    connect_data = request.json
    conn_gam_code = connect_data.get('game_code')

    if not conn_gam_code or not os.path.exists(f"./games/{conn_gam_code}/"):
        return make_response(jsonify({'error': "Invalid code"}))
    game = Game(conn_gam_code)
    return player_connect(game, connect_data)

@app.route('/board')
def board():
    game_code = request.cookies.get('game_code')
    player_uuid = request.cookies.get('player_uuid')
    response = make_response(
        render_template('board.html', player_uuid=player_uuid, game_code=game_code)
    )
    return response

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)


