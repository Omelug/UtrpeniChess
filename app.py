from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory, jsonify, \
    Blueprint
from flask_socketio import SocketIO
from game_entties import Game, Player
from test import test_blueprint, init_app

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

@app.route('/create_game', methods=['POST'])
def create_game():

    game = Game()
    player = Player(starter=True)
    game.add_player(player)

    response = make_response(redirect(url_for('board')))
    response.set_cookie('game_code', game.code, samesite='None', secure=True)
    response.set_cookie('player_uuid', player.player_uuid, samesite='None', secure=True)

    redirect_url = url_for('board')
    return jsonify({'redirect': redirect_url})

def load_game():
    pass
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

