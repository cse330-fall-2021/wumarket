from flask_socketio import emit, join_room, leave_room
from main import socketio

@socketio.on('newMessage', namespace='/chat')
def newMessage(message):
