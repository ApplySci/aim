from flask import Flask, render_template
from flask_socketio import SocketIO

application = Flask(__name__)
socketio = SocketIO(application)

@application.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('hello')
def handle_hello(data):
    print(f'Received hello from client: {data}')
    socketio.emit('response', {'message': 'Hello from server!'})

if __name__ == '__main__':
    socketio.run(application, debug=True)
