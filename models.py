"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class FollowersFollowee(db.Model):
    """Connection of a follower <-> followee."""

    __tablename__ = 'follows'

    followee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png"
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    messages = db.relationship('Message', backref='user', lazy='dynamic')

    followers = db.relationship(#was followers
        "User",
        secondary="follows",
        primaryjoin=(FollowersFollowee.follower_id == id),
        secondaryjoin=(FollowersFollowee.followee_id == id),
        backref=db.backref('following', lazy='dynamic'),#was following
        lazy='dynamic')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        return bool(self.followers.filter_by(id=other_user.id).first())

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        return bool(self.following.filter_by(id=other_user.id).first())
    
    @property
    def number_of_likes(self):
        """How many likes?"""
        total_liked = len(Like
                        .query
                        .filter(Like.user_id == self.id)
                        .all())
        
        return total_liked

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        #no commit?
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    # message.likers returns users that liked the message.
    # user.liked_messages returns messages that the user liked
    likers = db.relationship(
        "User",
        secondary="likes", 
        backref=db.backref('liked_messages', lazy='dynamic'),
        lazy='dynamic')

    def liked_by_user(self, user):
        """Is this message liked by the user?"""
        
        return user.id in [like.user_id for like in self.likes]

    def toggle_like(self,user):
        """Function for toggling like on a warble"""

        if self.liked_by_user(user):
            
            unliked = [like for like in user.likes if like.message_id == int(self.id)][0]
            db.session.delete(unliked)

        else:

            liked = Like(user_id=user.id,message_id=self.id)
            db.session.add(liked)
        

class Like(db.Model):
    """Individual like for a message"""

    __tablename__ = 'likes'

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    message_id = db.Column(db.Integer, db.ForeignKey('messages.id', ondelete="cascade"),
        primary_key=True)

    # Create two relationships here - Message, User

    liker = db.relationship('User', backref='likes')

    liked_message = db.relationship('Message', backref='likes')

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
