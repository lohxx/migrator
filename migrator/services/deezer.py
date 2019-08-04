import os
import requests
import webbrowser

from rauth import OAuth2Service
import sqlalchemy.orm.exc as sq_exceptions

import click

from migrator import app
from migrator.services.tokens import save_tokens, get_tokens
from migrator.services.interfaces import Playlist, ServiceAuth


class DeezerAuth(ServiceAuth):
    SERVICE_CODE = 2

    def __init__(self):
        self.oauth = OAuth2Service(
            name='deezer',
            base_url='https://api.deezer.com/',
            client_id=os.environ['DEEZER_CLIENT_ID'],
            client_secret=os.environ['DEEZER_CLIENT_SECRET'],
            authorize_url='https://connect.deezer.com/oauth/auth.php',
            access_token_url='https://connect.deezer.com/oauth/access_token.php?'
        )

    def _get_access_token(self, args):
        session = requests.Session()
        response = session.get(self.oauth.access_token_url, params=args)
        return response.json()

    @property
    def session(self):
        try:
            tokens = get_tokens(self.SERVICE_CODE)
        except sq_exceptions.NoResultFound as e:
            self.autorization_url({
                'app_id': os.environ['DEEZER_CLIENT_ID'],
                'perms': 'manage_library, offline_access',
                'redirect_uri': 'http://localhost:5000/deezer/callback'
            })
            tokens = get_tokens(self.SERVICE_CODE)
            data.update({'code': tokens.code})
            response = self._get_access_token(data)
            save_tokens(self.SERVICE_CODE, response)

        session = requests.Session()
        session.params = {'access_token': tokens.access_token}

        return session


class DeezerPlaylists(Playlist):
    def __init__(self):
        self.oauth = DeezerAuth()
        self.user = self.request('https://api.deezer.com/user/me')

    def request(self, endpoint, page=0, limit=30):
        response = self.oauth.session.get(endpoint)
        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    def get_tracks(self, tracks_url):
        tracks = []
        playlist_tracks = self.request(tracks_url)

        for track in playlist_tracks['data']:
            tracks.append({
                'name': track['title'],
                'artists': [track['artist']['name']]
            })

        return tracks

    def get(self, name):
        click.echo('Procurando a playlist...')
        playlists = self.request(f'http://api.deezer.com/user/{self.user["id"]}/playlists')

        for playlist in playlists['data']:
            if playlist['title'] == name:
                click.echo('Playlist encotrada!')
                tracks = self.get_tracks(playlist['tracklist'])
                return {'playlist': name, 'tracks': tracks}
        else:
            click.echo('Não foi possivel achar a playlist, verifique se o nome esta correto')

    def copy(self, playlist):
        click.echo('Copiando a playlist!')
        name, tracks = playlist.values()