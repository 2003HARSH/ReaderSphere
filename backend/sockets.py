from flask_socketio import emit,join_room
from flask_login import current_user
from .models import Message,FriendRequest,User,Group,GroupMessage
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
    

    @socketio.on('create_group')
    def handle_create_group(data):
        if current_user.is_authenticated:
            group_name = data.get('name')
            new_group = Group(name=group_name, created_by=current_user)
            new_group.members.append(current_user)
            db.session.add(new_group)
            db.session.commit()

            emit('group_created', {
                'id': new_group.id,
                'name': new_group.name
            }, room=str(current_user.id))

    @socketio.on('join_group')
    def handle_join_group(data):
        if current_user.is_authenticated:
            group_id = data.get('group_id')
            group = Group.query.get(group_id)
            if group and current_user not in group.members:
                group.members.append(current_user)
                db.session.commit()

            join_room(str(group_id))

            # Fetch and emit existing messages for the group
            messages = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.timestamp).all()
            messages_data = [{
                'sender': msg.sender.first_name,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            } for msg in messages]

            emit('group_messages', {'messages': messages_data}, room=str(group_id))
    
    @socketio.on('send_group_message')
    def handle_send_group_message(data):
        if current_user.is_authenticated:
            group_id = data.get('group_id')
            content = data.get('content')
            group = Group.query.get(group_id)

            if group and current_user in group.members:
                new_message = GroupMessage(
                    content=content,
                    group_id=group_id,
                    sender_id=current_user.id
                )
                db.session.add(new_message)
                db.session.commit()

                emit('new_group_message', {
                    'group_id': group_id,
                    'sender': current_user.first_name,
                    'content': content,
                    'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }, room=str(group_id))

    
    @socketio.on('add_member')
    def handle_add_member(data):
        if current_user.is_authenticated:
            group_id = data.get('group_id')
            user_id_to_add = data.get('user_id')
    
            group = Group.query.get(group_id)
            user_to_add = User.query.get(user_id_to_add)
    
            # Only the group creator can add members
            if group and user_to_add and group.created_by_id == current_user.id:
                if user_to_add not in group.members:
                    group.members.append(user_to_add)
                    db.session.commit()
    
                    # Notify the admin that the user was added
                    emit('member_added', {
                        'group_id': group.id,
                        'user_id': user_to_add.id,
                        'user_name': user_to_add.first_name
                    }, room=str(current_user.id))
    
                    # notify the newly added user
                    emit('added_to_group', {
                        'group_id': group.id,
                        'group_name': group.name,
                        'admin_name': current_user.first_name
                    }, room=str(user_to_add.id))
