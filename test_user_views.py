"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Like, FollowersFollowee

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(
                                    username="testuser1",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    )

        db.session.commit()


    def test_list_users(self):
        """Can we list users?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.get("/users")

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"testuser1", resp.data)

    def test_users_show(self):
            """Can we show user profile?"""

            # Since we need to change the session to mimic logging in,
            # we need to use the changing-session trick:

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser1.id

                # Now, that session setting is saved, so we can have
                # the rest of ours test

                resp = c.get(f"/users/{self.testuser1.id}")

                # Make sure it redirects
                self.assertEqual(resp.status_code, 200)

                self.assertIn(b"testuser1", resp.data)

    def test_show_following(self):
            """Can we show user following?"""

            # Since we need to change the session to mimic logging in,
            # we need to use the changing-session trick:

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser1.id

                # Now, that session setting is saved, so we can have
                # the rest of ours test


                # import pdb; pdb.set_trace()

                testuser2 = User.signup(
                                    username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None,
                                    )

                db.session.commit()

            

                followers = FollowersFollowee(followee_id=self.testuser1.id,follower_id=testuser2.id,)

                db.session.add(followers)

                db.session.commit()

                resp = c.get(f"/users/{testuser2.id}/following")

                

                self.assertEqual(testuser2.followers.one().username,'testuser1')

                self.assertEqual(resp.status_code, 200)

                self.assertIn(b"testuser1", resp.data)
    


    