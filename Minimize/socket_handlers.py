from flask_socketio import emit, join_room
from flask_login import current_user
from datetime import datetime
from Minimize.extensions import socketio, db
from Minimize.models import Message

@socketio.on('join')
def on_join(data):
    room = f"group_{data['group_id']}"
    join_room(room)

@socketio.on('send_message')
def handle_send_message(data):
    group_id = data['group_id']
    msg = data['msg']

    message = Message(content=msg, user_id=current_user.id, group_id=group_id)
    db.session.add(message)
    db.session.commit()

    emit('receive_message', {
        'msg': msg,
        'username': current_user.username,
        'timestamp': datetime.utcnow().strftime('%H:%M')
    }, to=f"group_{group_id}")
