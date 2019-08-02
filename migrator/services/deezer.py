import os

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
            access_token_url='https://connect.deezer.com/oauth/access_token.php'
        )

    def _get_access_token(self):
        pass

    def autorization_url(self):
        request_args = {
            'app_id': os.environ['DEEZER_APP_ID'],
            'perms': 'manage_library',
            'redirect_uri': 'http://localhost:5000/deezer/callback'
        }

        try:
            tokens = get_tokens(self.SERVICE_CODE)
            request_args.update({'app_id': tokens.code})
        except sq_exceptions.NoResultFound as e:
            pass


class DeezerPlaylists(Playlist):
    def __init__(self):
        self.oauth = DeezerAuth()

    def get_tracks(self):
        return super().get_tracks()

    def get(self):
        return super().get()

