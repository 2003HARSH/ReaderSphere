from flask_socketio import send
from flask_login import current_user
from .models import Message
from .extensions import db, socketio
from datetime import datetime

def configure_socketio(socketio):
    @socketio.on('message')
    def handle_message(msg):
        print(msg)
        if current_user.is_authenticated:
            new_message = Message(
                content=msg,
                sender_id=current_user.id,
                receiver_id=current_user.id,
                timestamp=datetime.now()
            )
            db.session.add(new_message)
            db.session.commit()

            # Broadcast the message to all clients
            send({
                'firstname': current_user.first_name,
                'message': msg,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }, broadcast=True)


