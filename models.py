"""Models for Polling app."""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database"""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    def __repr__(self):
        u = self
        return f"<PlayList id = {u.id} username = {u.username} password={u.password} >"

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    analysis_card = db.relationship(
        'AnalysisCard', backref='user', cascade='all,delete')

    @classmethod
    def register(cls, username, password):
        """Register with hashed password and return user"""
        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf string)
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists and password is correct"""

        """Return user if valid, else return false"""

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, pwd):
            # return user instance
            return user
        else:
            return False


class Keyword(db.Model):
    """Keyword for polling"""
    __tablename__ = "keywords"

    def __repr__(self):
        k = self
        return f"<KeyWord id ={k.keyword_id} word = {k.word}>"

    keyword_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String, nullable=False)
    sentiment_analyses = db.relationship(
        'SentimentAnalysis', backref='keyword', lazy=True)

    def serialize(self):
        """Returns a dict representation of Keyword"""
        return {
            'id': self.keyword_id,
            'word': self.word
        }


class SentimentAnalysis(db.Model):
    """give a keyword a sentiment score"""
    __tablename__ = "sentiment_analyses"

    def __repr__(self):
        s = self
        return f"<SentimentAnalysis id={s.id} keyword_id={s.keyword_id} score={s.score}>"

    id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey(
        'keywords.keyword_id'))
    score = db.Column(db.Integer)


class AnalysisCard(db.Model):
    """Analysis card"""

    __tablename__ = "analysis_cards"

    def __repr__(self):
        c = self
        return f"<AnalysisCard id = {c.id} user_id = {c.user_id} >"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    analysis_card_keywords = db.relationship(
        'AnalysisCardKeyword', backref='analysis_card', lazy=True)


class AnalysisCardKeyword(db.Model):
    __tablename__ = "analysis_card_keywords"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_card_id = db.Column(db.Integer, db.ForeignKey(
        'analysis_cards.id'))
    keyword_id = db.Column(db.Integer, db.ForeignKey(
        'keywords.keyword_id'))
    sentiment_analysis_id = db.Column(db.Integer, db.ForeignKey(
        'sentiment_analyses.id'))
    sentiment_analysis = db.relationship(
        'SentimentAnalysis', backref='analysis_card_keywords', lazy=True)
