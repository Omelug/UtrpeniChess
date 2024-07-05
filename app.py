from flask import Flask, render_template, request, redirect, url_for, make_response

from game_entties import Game, Player, get_uuid

app = Flask(__name__)

games={}
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
    color = game.add_player(player)

    response = make_response(render_template('board.html', color=color, game_code=game.code))
    response.set_cookie('game_code', game.code)
    response.set_cookie('player_id', player.player_uuid)

    return response



if __name__ == '__main__':
    app.run()
