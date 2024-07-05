from flask import make_response, render_template

from app import socketio
from app import app

random_int = 0

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('update_random_int')
def handle_update_random_int():
    global random_int
    random_int = list(range(10))
    socketio.emit('random_int_updated', {'random_int': random_int})

@app.route('/updater_test')
def updater_test():
    return make_response(render_template('test.html'))

@app.route('/random_test')
def random_test():
    handle_update_random_int()