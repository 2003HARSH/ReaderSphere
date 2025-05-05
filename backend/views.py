from flask import Blueprint,render_template,request,jsonify,redirect,url_for
from flask_login import login_required,current_user
from .models import User,Message,FriendRequest
import requests
from bs4 import BeautifulSoup

views=Blueprint('views',__name__)

@views.route('/')
def index():
    if current_user:
        return redirect(url_for('views.my_profile'))
    return(redirect(url_for('auth.login')))

@views.route('<username>')
@login_required
def profile(username):
    if username != current_user.username:
        user=User.query.filter_by(username=username).first()
        is_friend = False
        if current_user in user.friends:
            is_friend = True
        return render_template('profile.html',user=user,is_friend=is_friend,edit=False) 
    else:
        return redirect(url_for('views.my_profile'))
    
@views.route('/my_profile')
@login_required
def my_profile():
    people=User.query.filter(User.id!=current_user.id).all()
    pending_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()
    non_friends = User.query.filter(User.id != current_user.id).filter(~User.id.in_([friend.id for friend in current_user.friends])).all()
    return render_template('profile.html', user=current_user, people=non_friends, edit=True, pending_requests=pending_requests)

@views.route('/api/my_profile', methods=['GET'])
@login_required
def api_my_profile():
    # Serialize current user
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'dob': current_user.dob.isoformat() if current_user.dob else None,
        'bio': current_user.bio,
        'profile_pic': current_user.profile_pic,
    }

    # Serialize non-friends
    non_friends = User.query.filter(
        User.id != current_user.id,
        ~User.id.in_([friend.id for friend in current_user.friends])
    ).all()
    non_friends_data = [
        {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_pic': user.profile_pic,
        } for user in non_friends
    ]

    # Serialize pending friend requests
    pending_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()
    pending_data = [
        {
            'id': fr.id,
            'sender_id': fr.sender.id,
            'sender_username': fr.sender.username,
            'sender_profile_pic': fr.sender.profile_pic,
            'timestamp': fr.timestamp.isoformat()
        } for fr in pending_requests
    ]

    return jsonify({
        'user': user_data, #json
        'non_friends': non_friends_data, #list of json
        'pending_requests': pending_data #list of json
    })

@views.route('/messages')
@login_required
def messages():
    return render_template('messages.html', user=current_user)

@views.route('/get_users')
@login_required
def get_users():
    # Fetch all users except the current user
    users = current_user.friends

    # Convert users to a list of dictionaries
    users_data = [{
        'id': user.id,
        'username':user.username,
        'first_name': user.first_name,
        'profile_pic':user.profile_pic
    } for user in users]

    return jsonify(users_data)

@views.route('/get_messages/<int:receiver_id>')
@login_required
def get_messages(receiver_id):
    # Fetch messages between the current user and the selected user
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    # Convert messages to a list of dictionaries
    messages_data = [{
        'sender_id': message.sender_id,
        'sender_name': User.query.filter_by(id=message.sender_id).first().first_name,
        'message': message.content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for message in messages]

    return jsonify(messages_data)


@views.route('/groups')
@login_required
def groups():
    my_groups = current_user.groups
    return render_template('groups.html', user=current_user,groups=my_groups)

@views.route('/books')
@login_required
def books():
    return render_template('books.html',user=current_user)

@views.route('/book/<title>')
@login_required
def book(title):
    url = f"https://www.googleapis.com/books/v1/volumes/{title}"
    res = requests.get(url)
    data = res.json()

    info = data.get('volumeInfo', {})
    Title= info.get("title")
    Authors=info.get("authors")
    Publisher=info.get("publisher")
    Category=info.get("categories")
    pageCount=info.get("pageCount")
    Description=info.get("description")
    Description=BeautifulSoup(Description, "html.parser").get_text()
    Thumbnail=info.get("imageLinks", {}).get("thumbnail")
    return render_template("book_detail.html",user=current_user,
                           Title=Title,
                           Authors=Authors,
                           Publisher=Publisher,
                           Category=Category,
                           pageCount=pageCount,
                           Description=Description,
                           Thumbnail=Thumbnail)

@views.route('/book/search/<query>')
@login_required
def book_search(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    res = requests.get(url)
    data = res.json()

    for book in data['items'][:1]:
        info = book['volumeInfo']
        Title= info.get("title")
        Authors=info.get("authors")
        Publisher=info.get("publisher")
        Category=info.get("categories")
        pageCount=info.get("pageCount")
        Description=info.get("description")
        Description=BeautifulSoup(Description, "html.parser").get_text()
        Thumbnail=info.get("imageLinks", {}).get("thumbnail")
    return render_template("book_detail.html",user=current_user,
                           Title=Title,
                           Authors=Authors,
                           Publisher=Publisher,
                           Category=Category,
                           pageCount=pageCount,
                           Description=Description,
                           Thumbnail=Thumbnail)