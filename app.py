from flask import Flask, render_template, request, redirect, url_for, make_response

from game_entties import Game, Player, get_uuid

app = Flask(__name__)

games={}
@app.route('/')
def index():
    return redirect(url_for('index'))
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/create_game', method='POST')
def create_game():
    game = Game()
    response = make_response(render_template('index.html'))
    response.set_cookie('game_code', game.code)
    player = Player(starter=True)
    response.set_cookie('player_id', player.player_uuid)
    game.add_player(player)
    return response


if __name__ == '__main__':
    app.run()
