from flask_socketio import emit,join_room
from flask_login import current_user
from .models import Message,FriendRequest,User
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

            new_message = Message(
                content=message,
                sender_id=current_user.id,
                receiver_id=receiver_id,
                timestamp=datetime.now()
            )
            db.session.add(new_message)
            db.session.commit()

            emit('private_message', {
                'sender_id': current_user.id,
                'sender_name': current_user.first_name,
                'message': message,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }, room=str(receiver_id))  # Send to the receiver's room

            emit('private_message', {
                'sender_id': current_user.id,
                'sender_name': current_user.first_name,
                'message': message,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }, room=str(current_user.id))  

    @socketio.on('send_friend_request')
    def handle_send_friend_request(data):
        if current_user.is_authenticated:
            receiver_id = data.get('receiver_id')
            sender_id = current_user.id

            if sender_id == receiver_id:
                return

            # Check if a friend request already exists
            existing = FriendRequest.query.filter_by(
                sender_id=sender_id, receiver_id=receiver_id, status='pending'
            ).first()
            if not existing:
                new_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id)
                db.session.add(new_request)
                db.session.commit()

                emit('receive_friend_request', {
                    'request_id': new_request.id,
                    'sender_id': sender_id,
                    'sender_name': current_user.first_name,
                    'timestamp': new_request.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }, room=str(receiver_id))


    @socketio.on('respond_friend_request')
    def handle_respond_friend_request(data):
        request_id = data.get('request_id')
        action = data.get('action')  # 'accept' or 'reject'

        friend_request = FriendRequest.query.get(request_id)
        if friend_request and friend_request.receiver_id == current_user.id:
            friend_request.status = action
            db.session.commit()

            if action == 'accept':
                # Add to each other's friends list
                sender = User.query.get(friend_request.sender_id)
                current_user.friends.append(sender)
                sender.friends.append(current_user)
                db.session.commit()

            emit('friend_request_response', {
                'receiver_id': current_user.id,
                'receiver_name': current_user.first_name,
                'status': action
            }, room=str(friend_request.sender_id))
