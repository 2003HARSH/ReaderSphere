from .extensions import db
from flask_login import UserMixin
import datetime
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy import Float

# Many-to-Many relationship for accepted friendships
friends_association = db.Table('friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password = db.Column(db.String(200))
    dob = db.Column(db.Date)
    profile_pic = db.Column(db.String(200))
    bio = db.Column(db.Text)

    # Many-to-Many: confirmed friends
    friends = db.relationship(
        'User',
        secondary=friends_association,
        primaryjoin=id == friends_association.c.user_id,
        secondaryjoin=id == friends_association.c.friend_id,
        backref='friend_of'
    )

    def is_friend(self, other_user):
        return other_user in self.friends


class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_friend_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_friend_requests')

    def is_pending(self):
        return self.status == 'pending'

    def is_accepted(self):
        return self.status == 'accepted'

class Message(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    receiver_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    content=db.Column(db.String(1000),nullable=False)
    timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow)
    seen=db.Column(db.Boolean,default=False)


group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', backref='created_groups')
    members = db.relationship('User', secondary=group_members, backref='groups')

class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    group = db.relationship('Group', backref='messages')
    sender = db.relationship('User')

class BookRating(db.Model):
    """
    Represents a single rating given by a user to a book.
    """
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(50), nullable=False, index=True) # Google Books Volume ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # Rating from 1 to 5
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationship to get the user who made the rating
    user = db.relationship('User', backref='ratings')

    # Ensures a user can only rate a specific book once
    __table_args__ = (db.UniqueConstraint('book_id', 'user_id', name='_book_user_uc'),)



class BookGenreMap(db.Model):
    __tablename__ = 'book_genre_map'

    book_id = db.Column(db.String(50), primary_key=True)  # Google Books Volume ID
    raw_genre = db.Column(db.String(255), nullable=False)
    normalized_genre = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<BookGenreMap(book_id='{self.book_id}', normalized='{self.normalized_genre}')>"

class UserGenreVector(db.Model):
    __tablename__ = 'user_genre_vector'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    romance = db.Column(Float, default=0.0)
    science_fiction = db.Column(Float, default=0.0)
    fantasy = db.Column(Float, default=0.0)
    mystery = db.Column(Float, default=0.0)
    historical = db.Column(Float, default=0.0)
    biography = db.Column(Float, default=0.0)
    non_fiction = db.Column(Float, default=0.0)
    thriller = db.Column(Float, default=0.0)
    young_adult = db.Column(Float, default=0.0)
    self_help = db.Column(Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', backref='genre_vector', uselist=False)

    def as_vector(self):
        return [
            self.romance, self.science_fiction, self.fantasy,
            self.mystery, self.historical, self.biography,
            self.non_fiction, self.thriller, self.young_adult, self.self_help
        ]

class FriendSuggestion(db.Model):
    __tablename__ = 'friend_suggestions'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    suggested_friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    similarity_score = db.Column(Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref='suggested_friends')
    suggested_friend = db.relationship('User', foreign_keys=[suggested_friend_id])

    def __repr__(self):
        return f"<FriendSuggestion({self.user_id} → {self.suggested_friend_id}, sim={self.similarity_score:.4f})>"
