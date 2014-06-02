#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User
from datetime import datetime, timedelta
from app.models import User, Post, Project


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        u = User(nickname='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'

        self.assertEqual(avatar[0:len(expected)], expected)

    def test_make_unique_nickname(self):
        u = User(nickname='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()

        nickname = User.make_unique_nickname('john')
        self.assertNotEqual(nickname, 'john')

        u = User(nickname=nickname, email='susan@example.com')
        db.session.add(u)
        db.session.commit()

        nickname2 = User.make_unique_nickname('john')

        self.assertNotEqual(nickname2, 'john')
        self.assertNotEqual(nickname2, nickname)

    def test_follow(self):
        u1 = User(nickname='john', email='john@example.com')
        u2 = User(nickname='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.unfollow(u2), None)
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u1.follow(u2), None)
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEquals(u1.followed.first().nickname, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().nickname, 'john')
        u = u1.unfollow(u2)
        self.assertNotEqual(u, None)
        db.session.add(u)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # make four users
        u1 = User(nickname='john', email='john@example.com')
        u2 = User(nickname='susan', email='susan@example.com')
        u3 = User(nickname='mary', email='mary@example.com')
        u4 = User(nickname='david', email='david@example.com')
        for i in [u1, u2, u3, u4]:
            db.session.add(i)
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

        for i in [p1, p2, p3, p4]:
            db.session.add(i)
        # commit users and posts to temporary db
        db.session.commit()

        # setup followers in the db

        # followers for u1(john)
        for i in [u1, u2, u4]:  # john follows himself, susan, and david
            u1.follow(i)

        # followers for u2(susan)
        for i in [u2, u3]:  # susan follows herself, mary
            u2.follow(i)

        # followers for u3(mary)
        for i in [u3, u4]:  # mary follows herself, david
            u3.follow(i)

        # followers for u4(david)
        u4.follow(u4)  # david follows himself

        for i in [u1, u2, u3, u4]:
            db.session.add(i)  # add follows to session for commit

        db.session.commit()
        # check the followed posts of each user

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()

        self.assertEqual(len(f1), 3)
        self.assertEqual(len(f2), 2)
        self.assertEqual(len(f3), 2)
        self.assertEqual(len(f4), 1)
        self.assertEqual(f1, [p4, p2, p1])
        self.assertEqual(f2, [p3, p2])
        self.assertEqual(f3, [p4, p3])
        self.assertEqual(f4, [p4])

    def test_projects(self):
        # mock user
        u1 = User(nickname='john', email='john@example.com')
        db.session.add(u1)

        # mock portfolio object
        p1 = Project(
            title='Find Me Pizza',
            description="Yelp/Google Maps API w/ Ouath \
            2.0 to find business around with search query of \"pizza\"",
            git_hub_link="https://github.com/frimmy/findmepizza",
            demo_link="http://frimmy.github.io/findmepizza/",
            author=u1)
        
        db.session.add(p1)
        db.session.commit()

        post1 = u1.projects.first()

        self.assertEqual(post1.title, p1.title)
        self.assertEqual(post1.description, p1.description)
        self.assertEqual(post1.git_hub_link, p1.git_hub_link)
        self.assertEqual(post1.demo_link, p1.demo_link)
        self.assertEqual(post1.author, p1.author)




if __name__ == '__main__':
    unittest.main()
