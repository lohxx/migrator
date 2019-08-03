import os
import requests
import webbrowser

from rauth import OAuth2Service
import sqlalchemy.orm.exc as sq_exceptions


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
        try:
            return response.json()
        except Exception as e:
            self.autorization_url({
                'app_id': os.environ['DEEZER_CLIENT_ID'],
                'perms': 'manage_library',
                'redirect_uri': 'http://localhost:5000/deezer/callback'
            })

            return session.get(self.oauth.access_token_url, params=args).json()

    @property
    def session(self):
        data = {
            'app_id': os.environ['DEEZER_CLIENT_ID'],
            'secret': os.environ['DEEZER_CLIENT_SECRET'],
            'output': 'json',
        }

        try:
            tokens = get_tokens(self.SERVICE_CODE)
            data.update({'code': tokens.code})
        except sq_exceptions.NoResultFound as e:
            self.autorization_url({
                'app_id': os.environ['DEEZER_CLIENT_ID'],
                'perms': 'manage_library',
                'redirect_uri': 'http://localhost:5000/deezer/callback'
            })
            tokens = get_tokens(self.SERVICE_CODE)
            data.update({'code': tokens.code})

        tokens = self._get_access_token(data)
        save_tokens(self.SERVICE_CODE, tokens.json())

        # gerar uma session que usa o token...
        return session


class DeezerPlaylists(Playlist):
    def __init__(self):
        self.oauth = DeezerAuth()

    def get_tracks(self):
        return super().get_tracks()

    def get(self, name):
        playlists = self.request('playlists')

