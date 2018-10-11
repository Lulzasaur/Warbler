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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        self.client = app.test_client()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(u.messages.count(), 0)
        self.assertEqual(u.followers.count(), 0)

    def test_repr(self):
        """Does this function show user?"""

        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        #user should have the following message
        self.assertEqual(repr(u),'<User #1: testuser, test@test.com>')
        
    def test_is_followed_by(self):
        """Does this function show user?"""

        u1 = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )

        u2 = User(
            id=2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2",
        )

        

        follow = FollowersFollowee(
            followee_id=1,
            follower_id=2
        )

    
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.add(follow)
        db.session.commit()

        #user should have the following message
        self.assertEqual(u2.is_followed_by(u1),True)
        self.assertEqual(u2.followers.first(),u1)

    def test_is_following(self):
        u1 = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )

        u2 = User(
            id=2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2",
        )

        

        follow = FollowersFollowee(
            followee_id=1,
            follower_id=2
        )

    
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.add(follow)
        db.session.commit()

        self.assertEqual(u1.is_following(u2),True)
        self.assertEqual(u1.following.first(),u2)

        # Should this be fixed in model.py? Doesn't make sense to me.
    
    def test_number_of_likes(self):
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

        self.assertEqual(u1.number_of_likes, 1)


    def test_signup(self):
        u1 = User.signup('testuser', 'test@test.com', 'HASHED_PASSWORD', '')

        db.session.commit()

        self.assertEqual(User.query.filter(User.username=='testuser').first(), u1)
        self.assertEqual(User.query.filter(User.username=='testuser').first().username, 'testuser')
        self.assertEqual(User.query.filter(User.username=='testuser').first().email, 'test@test.com')



    def test_authenticate(self):

        u1 = User.signup('testuser', 'test@test.com', 'HASHED_PASSWORD', '')

        db.session.add(u1)
        db.session.commit()


        self.assertEqual(User.authenticate('testuser', 'HASHED_PASSWORD'), u1)
        self.assertEqual(User.authenticate('testuser', "HASWORD"), False)

        