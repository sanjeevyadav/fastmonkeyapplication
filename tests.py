#!flask/bin/python
import os
#import unittest
from datetime import datetime, timedelta

from config import basedir
from app import app, db
from app.models import Users, Post
import pytest


class TestCase():
    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'postgresql://sanjeev:sanjeev@localhost:5432/app'
        #db.create_all()

    def test_avatar(self):
        # create a user
        u = Users(username='john', email='john@example.com', password = 'john')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    def test_follow(self):
        # create a friend
        u1 = Users(username='john', email='john@example.com', password= 'john')
        u2 = Users(username='susan', email='susan@example.com', password = 'john')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) == None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) == None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().username == 'susan'
        assert u2.followers.count() == 1
        assert u2.followers.first().username == 'john'
        u = u1.unfollow(u2)
        assert u != None
        db.session.add(u)
        db.session.commit()
        assert u1.is_following(u2) == False
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        # make four users
        u1 = Users(username='test', email='test@example.com', password = 'john')
        u2 = Users(username='susa', email='susa@example.com', password = 'susan')
        u3 = Users(username='mar', email='mar@example.com', password = 'mary')
        u4 = Users(username='davi', email='davi@example.com', password = 'david')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  timestamp=utcnow + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=utcnow + timedelta(seconds=2))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=utcnow + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=utcnow + timedelta(seconds=4))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        # setup the followers
        u1.follow(u1)  # john follows himself
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u2)  # susan follows herself
        u2.follow(u3)  # susan follows mary
        u3.follow(u3)  # mary follows herself
        u3.follow(u4)  # mary follows david
        u4.follow(u4)  # david follows himself
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1 == [p4, p2, p1]
        assert f2 == [p3, p2]
        assert f3 == [p4, p3]
        assert f4 == [p4]

def test_foo(app):
    pass
