"""Keyword models tests."""

# run these tests like:
#  \
#    python -m unittest test_keyword_model.py


from app import app
import os
from unittest import TestCase
from flask import session

from models import db, User, Auth, Keyword, AnalysisCard, SentimentScore
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


class KeywordModelTestCase(TestCase):
    """Test Keyword, AnalysisCard and SentimentScore models."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        self.uid = 94566
        u = User.register("testing", "testing@test.com", "password")
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_keyword_model(self):
        """Does basic keyword model work?"""
        w = Keyword(word="obama")
        db.session.add(w)
        db.session.commit()

        expected = f"<KeyWord id ={w.keyword_id} word = {w.word}> "
        actual = repr(w)

        self.assertEqual(expected, actual)
        self.assertIsInstance(w, Keyword)
        self.assertEqual(w.word, "obama")

    def test_keyword_model2(self):
        """Does keyword get added to the session['keywords] correctly?"""
        with app.test_client() as client:
            resp = client.get('/add_keyword?word=obama')
            self.assertEqual(resp.status_code, 302)
            self.assertIn('keywords', session)
            self.assertEqual(session['keywords'], ['obama'])

    def test_keyword_view(self):
        """Does keyword get rendered on the page?"""
        with app.test_client() as client:
            resp = client.get('/add_keyword?word=obama', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('obama', str(resp.data))

    def test_analysis_card(self):
        """ checking whether AnalysisCard is  created successfully with the expected values"""
        card = AnalysisCard(user_id=self.u, analysis_theme="us")
        db.session.add(card)
        db.session.commit()

        self.assertIsInstance(card, AnalysisCard)
        self.assertEqual(card.analysis_theme, 'us')
        self.assertEqual(card.user_id, self.u)

    def test_sentiment_score_creation(self):
        """Score is created when prompted with keyword and analysis card"""
        word = Keyword(word="obama")
        card = AnalysisCard(analysis_theme="test", user_id=self.u)
        db.session.add_all([word, card])
        db.session.commit()
        s = SentimentScore(keyword_id=word.keyword_id,
                           score=1.55, analysis_card_id=card.id)

        db.session.add(s)
        db.session.commit()
        self.assertIsInstance(s, SentimentScore)

        self.assertEqual(s.keyword_id, word.keyword_id)
        self.assertEqual(s.analysis_card_id, card.id)
        self.assertEqual(s.score, 1.55)

    def test__analyze_route_with_results(self):
        """
        Test that the /analyze route returns a response with the expected keywords and the word "Result"
        when given a list of keywords in the request.
        """
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['keywords'] = ['love', 'hate']
            resp = client.get('/analyze?keywords[]=love&keywords[]=hate')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Result',  resp.data)
            self.assertIn(b'love', resp.data)
            self.assertIn(b'hate', resp.data)
