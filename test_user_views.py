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
        Like.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(
                                    username="testuser1",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url='https://images.pexels.com/photos/67636/rose-blue-flower-rose-blooms-67636.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260',
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

            

                followers = FollowersFollowee(followee_id=testuser2.id,follower_id=self.testuser1.id,)

                db.session.add(followers)

                db.session.commit()

                resp = c.get(f"/users/{testuser2.id}/following")

                self.assertEqual(testuser2.following.one().username,'testuser1')

                self.assertEqual(resp.status_code, 200)

                self.assertIn(b'rose-blue-flower-rose-blooms-67636', resp.data)

    def test_users_followers(self):
            """Can we show user followers?"""

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

                resp = c.get(f"/users/{testuser2.id}/followers")

                self.assertEqual(testuser2.followers.one().username,'testuser1')

                self.assertEqual(resp.status_code, 200)

                self.assertIn(b"testuser2", resp.data)


    def test_add_follow(self):
            """Can we add follow and redirect?"""

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

                resp = c.post(f"/users/follow/{testuser2.id}")

                self.assertEqual(testuser2.followers.one().username,'testuser1')

                self.assertEqual(resp.status_code, 302)
        
    def test_stop_following(self):
        """Can we stop following?"""

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

            testuser2.followers.append(self.testuser1)

            # followers = FollowersFollowee(followee_id=self.testuser1.id,follower_id=testuser2.id,)

            # db.session.add(followers)

            db.session.commit()

            resp = c.post(f"/users/stop-following/{testuser2.id}")

            self.assertEqual(len(testuser2.followers.all()),0)

            self.assertEqual(resp.status_code, 302)

    def test_show_liked_messages(self):
        """Can we show liked messages?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            u2 = User(
                        id=1,
                        email="test123@test.com",
                        username="test123user",
                        password="HASHED_PASSWORD",
                    )

            db.session.add(u2)
            db.session.commit()

            m1 = Message(
                        id=1,
                        text='blahblahblah',
                        user_id=u2.id,
                    )

            l1 = Like(
                        user_id=self.testuser1.id,
                        message_id=1
                    )
                        
            db.session.add(m1)
            db.session.commit()
            db.session.add(l1)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser1.id}/likes")

            self.assertEqual(self.testuser1.number_of_likes,1)

            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"blahblahblah", resp.data)

    def test_show_profile(self):
        """Can we show user profile?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
        
        resp = c.get(f"/users/profile")
                                    
        self.assertIn(b"test@test.com", resp.data)
        self.assertIn(b"rose-blue-flower-rose-blooms", resp.data)

    def test_show_profile(self):
        """Can we show user profile?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
        
        resp = c.post(f"/users/profile",data={'username':'otterman',"email": "otteremail@otters.com",'password':'testuser'},follow_redirects=True)

        self.assertEqual(resp.status_code, 200)                    

        self.assertIn(b"otterman", resp.data)
        self.assertIn(b"rose-blue-flower-rose-blooms", resp.data)
        

    

    


    