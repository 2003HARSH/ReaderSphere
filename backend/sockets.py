from flask_socketio import emit,join_room
from flask_login import current_user
from .models import Message
from .extensions import db, socketio
from datetime import datetime

def configure_socketio(socketio):   
    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            # Join the user to a room based on their user_id 
            # ie,user_id == room_id
            join_room(str(current_user.id))
            print(f'User {current_user.id} connected and joined room {current_user.id}')

    @socketio.on('private_message')
    def handle_private_message(data):
        if current_user.is_authenticated:
            message = data.get('message')
            receiver_id = data.get('receiver_id')

            # Save the message to the database
            new_message = Message(
                content=message,
                sender_id=current_user.id,
                receiver_id=receiver_id,
                timestamp=datetime.now()
            )
            db.session.add(new_message)
            db.session.commit()

            # Send the message to the receiver's room
            emit('private_message', {
                'sender_id': current_user.id,
                'sender_name': current_user.first_name,
                'message': message,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }, room=str(receiver_id))  # Send to the receiver's room

            # Also send the message back to the sender's room
            emit('private_message', {
                'sender_id': current_user.id,
                'sender_name': current_user.first_name,
                'message': message,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }, room=str(current_user.id))  # Send back to the sender's room


