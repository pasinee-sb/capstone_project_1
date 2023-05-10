"""User model tests."""

# run these tests like:
#  \
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Auth
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


class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Auth.query.delete()

        self.client = app.test_client()

    def test_user_authen_success(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        u = User.register(
            "testuser",
            "test@test.com",
            "HASHED_PASSWORD"
        )
        db.session.add(u)

        db.session.commit()

        user = User.authenticate(u.username, "HASHED_PASSWORD")

        self.assertEqual(user, u)

    def test_user_authen_fail(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        u = User.register(
            "",
            "test@test.com",
            "HASHED_PASSWORD"
        )
        db.session.add(u)

        db.session.commit()

        user = User.authenticate(u.username, "HASHED_PASSWORD")

        self.assertNotEqual(user, False)

    def test_user_authen_fail2(self):
        """Does User.register raise a ValueError when an empty password is entered?"""
        with self.assertRaises(ValueError):
            User.register(
                "testuser",
                "test@test.com",
                ""
            )

    def test_user_repr(self):
        """Does the repr method work as expected?"""
        u = User.register(
            "",
            "test@test.com",
            "HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        u = User(
            email="test@test.com",
            username="testuser",
            auth_id=1
        )
        expected = f"<User id = {u.id} username = {u.username} auth={u.auth} >"
        actual = repr(u)
        self.assertEqual(actual, expected)

    def test_auth(self):
        """Is auth_id created after registering user?"""

        u = User.register(
            "testuser",
            "test@test.com",
            "HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        auth1 = Auth.query.filter_by(id=u.auth_id).first()

        self.assertEqual(auth1.id, u.auth_id)

        # Does deleting a user delete their auth_id from the auths table?

        db.session.delete(u)
        db.session.commit()

        auth2 = Auth.query.filter_by(id=u.auth_id).first()
        self.assertIsNone(auth2)
