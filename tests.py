#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User


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

if __name__ == '__main__':
    unittest.main()
