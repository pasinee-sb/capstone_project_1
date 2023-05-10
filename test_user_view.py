"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_view.py


from app import app, CURR_USER_KEY, do_login, g
import os
from unittest import TestCase
from flask import session, request

from models import db, connect_db, User, AnalysisCard, Auth, SentimentScore, Keyword
from sqlalchemy import exc


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///reddi-senti-test"


# Now we can import app


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

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                      email="test@test.com",
                                      password="testuser")
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.register("abc", "test1@test.com", "password")
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.register("efg", "test2@test.com", "password")
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.register("hij", "test3@test.com", "password")
        self.u4 = User.register("testing", "test4@test.com", "password")

        db.session.add_all([self.testuser, self.u1, self.u2, self.u3, self.u4])

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_home_view(self):
        with self.client as c:
            resp = c.get("/")

            self.assertIn("What is sentiment analysis", str(resp.data))
            self.assertIn("Try it!", str(resp.data))

    def test_demo_view(self):
        with self.client as c:
            resp = c.get("/demo")

            self.assertIn("Analyze Machine", str(resp.data))
            self.assertIn("Add Keyword", str(resp.data))
            self.assertNotIn("Check keywords to analyze", str(resp.data))

    def test_logged_user_view(self):
        with self.client as c:
            # simulate logging in the user and what the user sees on the first page
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add Keyword", str(resp.data))
            self.assertIn("Dashboard", str(resp.data))
            self.assertIn("Log out", str(resp.data))

    def test_logged_user_view2(self):
        with self.client as c:
            # simulate logging in the user and what the user sees on the first page
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/dashboard")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("Dashboard", str(resp.data))
