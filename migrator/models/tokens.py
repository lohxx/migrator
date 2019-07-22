import sqlite3
from migrator import db

DEEZER = 1
SPOTIFY = 2
YOUTUBE = 3


def save_tokens(response):
    user_tokens = Tokens.query.first()

    if user_tokens:
        user_tokens.save(response)
        return
    
    user_tokens = Tokens(
        refresh_token=response['refresh_token'],
        access_token=response['access_token'],
        service=service,
        code=response['code']
    )


class Tokens(db.Model):
    code = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String)
    access_token = db.Column(db.String)
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.Integer, nullable=False)

    def save(self, response):
        self.access_token = response.get('access_token')
        self.refresh_token = response.get('refresh_token')
        db.session.add(self)
        db.session.commit()

