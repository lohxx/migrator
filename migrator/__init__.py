#!/usr/bin/env python3
import os

from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy

#from views import spotify, deezer

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']

db = SQLAlchemy(app)
db.init_app(app)

#app.register_blueprint(deezer.deezer_api)
#app.register_blueprint(spotify.main)

def register_blueprints():
    from migrator.services.spotify import spotify_web

    app.register_blueprint(spotify_web)


@app.route('/deezer/callback')
def deezer_callback():
    from migrator.services.tokens import save_tokens
    if request.args.get('code'):
        save_tokens(2, request.args)

    return 'token salvo'


@app.route('/spotify/callback')
def spotify_callback():
    from migrator.services.tokens import save_tokens
    if request.args.get('code'):
        save_tokens(1, request.args)

    return "token salvo"


# @app.route('/spotify/playlists', methods=['GET'])
# def spotify_playlists():
#     from migrator.services.spotify import SpotifyPlaylists
#     spotify = SpotifyPlaylists()
#     playlists = spotify.playlists()
#     return playlists[0]


# @app.route('/deezer/playlists', methods=['GET'])
# def deezer_playlists():
#     from migrator.services.deezer import DeezerPlaylists
#     deezer = DeezerPlaylists()
#     return deezer.playlists()

# @app.route('/spotify/playlist/tracks', methods=['GET'])
# def spotify_playlist_songs():
#     pass


def init_db():
    """ Inicializa o banco de dados """
    from migrator.services.tokens import TokensManager
    db.create_all()


if __name__ == '__main__':
    register_blueprints()
    app.run(debug=True)