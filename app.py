import os.path

from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory, jsonify
from flask_socketio import SocketIO

from chat import init_app
from game_entities import Game, get_uuid


app = Flask(__name__)
socketio = SocketIO(app)
init_app(app)


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



def player_connect(game, create_data):
    #TODO unconnect and delete if emty game
    response = make_response(jsonify({'redirect': url_for('board')}))
    response.set_cookie('game_code', game.code, samesite='None', secure=True)

    uuid = request.cookies.get('player_uuid')
    if uuid is None:
        uuid = get_uuid()
        response.set_cookie('player_uuid', uuid, samesite='None', secure=True)

    added = game.connect_player(
        uuid, name=create_data.get('player_name'),
    )

    if added:
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
    create_data = request.json
    conn_gam_code = create_data.get('game_code')

    if not conn_gam_code or not os.path.exists(f"./games/{conn_gam_code}/"):
        return make_response(jsonify({'error': "Invalid code"}))
    game = Game(conn_gam_code)
    return player_connect(game, create_data)

@app.route('/board')
def board():
    game_code = request.cookies.get('game_code')
    player_uuid = request.cookies.get('player_uuid')
    response = make_response(
        render_template('board.html', player_uuid=player_uuid, game_code=game_code)
    )
    return response



if __name__ == '__main__':
    app.run()

