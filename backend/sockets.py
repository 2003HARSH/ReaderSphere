from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from .models import Message, FriendRequest, User, Group, GroupMessage,FriendSuggestion
from .extensions import db, socketio
from datetime import datetime

def configure_socketio(socketio):   
    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            # Join the user to a room based on their user_id 
            # so they can receive direct notifications
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

            # Send to the receiver's room
            emit('private_message', {
                'sender_id': current_user.id,
                'sender_name': current_user.first_name,
                'message': message,
                'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }, room=str(receiver_id))

            # Send back to the sender's room for UI update
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
        action = data.get('action')
        friend_request = FriendRequest.query.get(request_id)
        
        if friend_request and friend_request.receiver_id == current_user.id and friend_request.status == 'pending':
            friend_request.status = action
            
            if action == 'accept':
                sender = User.query.get(friend_request.sender_id)
                
                # Explicitly adding the friendship from both sides.
                current_user.friends.append(sender)
                sender.friends.append(current_user)

                FriendSuggestion.query.filter_by(user_id=current_user.id, suggested_friend_id=sender.id).delete()
                FriendSuggestion.query.filter_by(user_id=sender.id, suggested_friend_id=current_user.id).delete()
                
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
            member_ids = data.get('members', []) # Get member IDs from frontend

            new_group = Group(name=group_name, created_by=current_user)
            
            # Add the creator to the group
            new_group.members.append(current_user)

            # Find and add the selected friends to the group
            if member_ids:
                members_to_add = User.query.filter(User.id.in_(member_ids)).all()
                for member in members_to_add:
                    if member not in new_group.members:
                        new_group.members.append(member)

            db.session.add(new_group)
            db.session.commit()

            # Notify ALL members of the new group so their UI updates
            for member in new_group.members:
                emit('group_created', {
                    'id': new_group.id,
                    'name': new_group.name
                }, room=str(member.id))

    @socketio.on('join_group')
    def handle_join_group(data):
        if current_user.is_authenticated:
            group_id = data.get('group_id')
            group = Group.query.get(group_id)

            # A user can only join a group chat if they are a member
            if group and current_user in group.members:
                join_room(str(group_id))

                messages = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.timestamp).all()
                messages_data = [{
                    'sender': msg.sender.first_name,
                    'content': msg.content,
                    'sender_id': msg.sender_id,
                    'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                } for msg in messages]

                # Emit message history only to the user who just joined
                emit('group_messages', {'messages': messages_data})


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

                # Broadcast the new message to everyone in the group chat room
                emit('new_group_message', {
                    'group_id': group_id,
                    'sender': current_user.first_name,
                    'sender_id': current_user.id,
                    'content': content,
                    'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }, room=str(group_id))
                
    @socketio.on('delete_group')
    def handle_delete_group(data):
        if current_user.is_authenticated:
            group_id = data.get('group_id')
            group = Group.query.get(group_id)

            # Check if the group exists and if the current user is the creator
            if group and group.created_by_id == current_user.id:
                # Store member ids before deletion to notify them
                member_ids = [member.id for member in group.members]

                # Delete associated group messages first
                GroupMessage.query.filter_by(group_id=group_id).delete()
                
                # Now delete the group itself (relationships are handled by SQLAlchemy)
                db.session.delete(group)
                db.session.commit()

                # Notify all former members that the group was deleted
                for member_id in member_ids:
                    emit('group_deleted', {'group_id': group_id}, room=str(member_id))

    @socketio.on('unfriend')
    def handle_unfriend(data):
        if current_user.is_authenticated:
            friend_id = data.get('friend_id')
            friend_to_remove = User.query.get(friend_id)

            if friend_to_remove and friend_to_remove in current_user.friends:
                current_user.friends.remove(friend_to_remove)
                friend_to_remove.friends.remove(current_user)
                db.session.commit()

                emit('friendship_ended', {
                    'unfriended_user_id': friend_to_remove.id,
                    'unfriended_by_user_id': current_user.id
                }, room=str(current_user.id))
                
                emit('friendship_ended', {
                    'unfriended_user_id': friend_to_remove.id,
                    'unfriended_by_user_id': current_user.id
                }, room=str(friend_to_remove.id))