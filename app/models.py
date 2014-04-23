from app import db
from datetime import datetime
import re
from hashlib import md5

ROLE_USER = 0
ROLE_ADMIN = 1

followers = db.Table('followers',
                     db.Column(
                         'follower_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column(
                         'followed_id', db.Integer, db.ForeignKey('users.id'))
                     )


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(10))
    email = db.Column('email', db.String(50), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Users',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin = (followers.c.followed_id == id),
                               backref = db.backref(
                                   'followers', lazy='dynamic'),
                               lazy = 'dynamic')

    @staticmethod
    def make_unique_username(username):
        if Users.query.filter_by(username=username).first() == None:
            return username
        version = 2
        while True:
            new_username = username + str(version)
            if Users.query.filter_by(username=new_username).first() == None:
                break
            version += 1
        return new_username

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()

    @staticmethod
    def make_valid_username(username):
        return re.sub('[^a-zA-Z0-9_\.]', '', username)

    @staticmethod
    def make_valid_password(password):
        return re.sub('[^a-zA-Z0-9_\.]', '', password)

    @staticmethod
    def make_valid_email(email):
        return re.sub('[^a-zA-Z0-9_\.]', '', email)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def __repr__(self):
        return '<User %r>' % (self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
