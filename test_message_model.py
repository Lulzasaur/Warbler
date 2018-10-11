"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, FollowersFollowee, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        self.client = app.test_client()

    def test_liked_by_user(self):
        u1 = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )

        m1 = Message(
            id=1,
            text='blahblahblah',
            user_id=1,
        )

        l1 = Like(
            user_id=1,
            message_id=1
        )

        db.session.add(u1)
        db.session.add(m1)
        db.session.commit()
        db.session.add(l1)
        db.session.commit()

        self.assertEqual(m1.liked_by_user(u1), True)

    def test_attrs(self):
        u1 = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )

        m1 = Message(
            id=1,
            text='blahblahblah',
            user_id=1,
        )

        db.session.add(u1)
        db.session.add(m1)
        db.session.commit()

        self.assertEqual(m1.text, 'blahblahblah')

    def test_toggle_like(self):
        u1 = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )

        m1 = Message(
            id=1,
            text='blahblahblah',
            user_id=1,
        )

        db.session.add(u1)
        db.session.add(m1)
        db.session.commit()

        m1.toggle_like(u1)
        db.session.commit()

        self.assertEqual(m1.likes, u1.likes)
        self.assertEqual(len(m1.likes), 1)

        m1.toggle_like(u1)
        db.session.commit()

        self.assertEqual(len(m1.likes), 0)

   
        
