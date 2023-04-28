"""Models for Playlist app."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Playlist(db.Model):
    """Playlist."""

    def __repr__(self):
        pl = self
        return f"<PlayList id = {pl.id} name = {pl.name} description: {pl.description}>"

    __tablename__ = "playlists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    playlist_song = db.relationship('PlaylistSong', backref="playlist")
