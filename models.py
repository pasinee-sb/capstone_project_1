"""Models for Polling app."""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database"""
    db.app = app
    db.init_app(app)


class Auth(db.Model):
    """User Authorization"""
    __tablename__ = "auths"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    encrypted_password = db.Column(db.String)


class User(db.Model):
    """User"""

    def __repr__(self):
        u = self
        return f"<User id = {u.id} username = {u.username} auth={u.auth} >"

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False,)
    auth_id = db.Column(db.Integer, db.ForeignKey('auths.id'))

    auth = db.relationship('Auth', backref='user')
    analysis_card = db.relationship(
        'AnalysisCard', backref='user', cascade='all,delete')

    @classmethod
    def register(cls, username, email, password):
        """Register with hashed password and return user"""
        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf string)
        hashed_utf8 = hashed.decode("utf8")
        auth = Auth(encrypted_password=hashed_utf8)
        user = cls(username=username, email=email, auth=auth)

        # return instance of user w/username and hashed pwd
        return user

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists and password is correct"""

        """Return user if valid, else return false"""

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.auth.encrypted_password, pwd):
            # return user instance
            return user
        else:
            return False


class Keyword(db.Model):
    """Keyword for polling"""
    __tablename__ = "keywords"

    def __repr__(self):
        k = self
        return f"<KeyWord id ={k.keyword_id} word = {k.word}> "

    keyword_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String, nullable=False)


class AnalysisCard(db.Model):
    """Analysis card"""

    __tablename__ = "analysis_cards"

    def __repr__(self):
        c = self
        return f"<AnalysisCard id = {c.id} user_id = {c.user_id} analyis_theme={c.analysis_theme} >"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_theme = db.Column(db.String)
    # Add a unique constraint to user_id and analysis_theme
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'analysis_theme', name='_user_analysis_uc'),)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    sentiment_scores = db.relationship(
        'SentimentScore', backref='analysis_card', lazy=True)
    keywords = db.relationship('Keyword',
                               secondary='sentiment_scores',
                               backref='card', overlaps="analysis_cards,sentiment_scores")


class SentimentScore(db.Model):
    """give a keyword a sentiment score"""
    __tablename__ = "sentiment_scores"

    def __repr__(self):
        s = self
        return f"<SentimentScore id={s.id} keyword_id={s.keyword_id} score={s.score} analysis_card_id={s.analysis_card_id}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey(
        'keywords.keyword_id'), primary_key=True)
    keywords = db.relationship('Keyword', backref='score', viewonly=True)
    score = db.Column(db.Float)
    analysis_card_id = db.Column(
        db.Integer, db.ForeignKey('analysis_cards.id'), primary_key=True)
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    __table_args__ = (
        db.UniqueConstraint('created_date', 'keyword_id',
                            name='unique_analysis'),
    )
