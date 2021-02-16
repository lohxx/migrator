#!/usr/bin/env python3
import os
from functools import wraps

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']

db = SQLAlchemy(app)
db.init_app(app)


def save_auth_code(service):
    if request.args.get('code'):
        service.save_code_and_authenticate(request.args)


@app.route('/deezer/callback')
def deezer_callback():
    from services.deezer import DeezerAuth
    save_auth_code(DeezerAuth())
    return 'ok'


@app.route('/spotify/callback')
def spotify_callback():
    from services.spotify import SpotifyAuth
    save_auth_code(SpotifyAuth())
    return 'ok'


if __name__ == '__main__':
    app.run(debug=True)