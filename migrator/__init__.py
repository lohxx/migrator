#!/usr/bin/env python3
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']

db = SQLAlchemy(app)
db.init_app(app)


@app.route('/deezer/callback')
def deezer_callback():
    from migrator.services.deezer import DeezerAuth

    if request.args.get('code'):
        DeezerAuth().save_code_and_authenticate(request.args)

    return 'token salvo'


@app.route('/spotify/callback')
def spotify_callback():
    from migrator.services.spotify import SpotifyAuth

    if request.args.get('code'):
        SpotifyAuth().save_code_and_authenticate(request.args)

    return "token salvo"


def init_db():
    """ Inicializa o banco de dados """
    from migrator.services.tokens import TokensManager
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)