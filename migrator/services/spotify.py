import json
import os
import pdb
import webbrowser

import click

from rauth import OAuth2Service

from migrator import app
from migrator.services.auth import ServiceAuth


@click.group()
def cli():
    pass


class SpotifyService(ServiceAuth):
    def __init__(self):
        self.oauth = OAuth2Service(
            name='spotify',
            client_id=os.environ['SPOTIFY_CLIENT_ID'],
            client_secret=os.environ['SPOTIFY_CLIENT_SECRET'],
            authorize_url='https://accounts.spotify.com/authorize',
            access_token_url='https://accounts.spotify.com/api/token',
            base_url='https://api.spotify.com/v1/'
        )

        self.playlist_service = None

    def autorization_url(self):
        scopes = [
            'playlist-modify-public',
            'playlist-read-collaborative',
            'playlist-read-private',
            'playlist-modify-private'
        ]
        authorize_url = self.oauth.get_authorize_url(**{
            'response_type': 'code',
            'redirect_uri': 'http://localhost:5000/callback',
            'scope': ', '.join(scopes)
        })

        app.logger.info(authorize_url)
        webbrowser.open(authorize_url)

        return self

    def get_access_token(self):
        data = {
            'code': os.environ['SPOTIFY_CODE'],
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:5000/callback'
        }

        session = self.oauth.get_auth_session(data=data, decoder=json.loads)

        response = session.access_token_response.json()

# TODO:
    # 1. Adicionar tabela para salvar o access_token, refresh_token e o code
    # 2. Criar flags para identificar o deezer, spotify e o youtube


if __name__ == '__main__':
    cli()
