#!/usr/bin/env python3
import os
import functools
import pickle

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']

db = SQLAlchemy(app)
db.init_app(app)


def read_pickle():
    obj = {}
    with open('tokens.pickle', 'rb') as f:
        obj = pickle.load(f)

    return obj


def write_keys(key, new_values):
    with open('tokens.pickle', 'wb') as f:
        pickle.dump(new_values, f, pickle.HIGHEST_PROTOCOL)


@app.route('/deezer/callback')
def deezer_callback():
    from src.services.deezer import DeezerAuth

    if request.args.get('code'):
        DeezerAuth().save_code_and_authenticate(request.args)

    return 'token salvo'


@app.route('/spotify/callback')
def spotify_callback():
    from src.services.spotify import SpotifyAuth

    if request.args.get('code'):
        SpotifyAuth().save_code_and_authenticate(request.args)

    return "token salvo"


if __name__ == '__main__':
    app.run(debug=True)