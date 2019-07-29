import os

from rauth import OAuth2Service

from migrator.services.interfaces import Playlist, ServiceAuth


class DeezerAuth(ServiceAuth):
    def __init__(self):
        self.oauth = OAuth2Service(
            name='deezer',
            base_url='https://api.deezer.com/',
            client_id=os.environ['DEEZER_CLIENT_ID'],
            client_secret=os.environ['DEEZER_CLIENT_SECRET'],
            authorize_url='https://connect.deezer.com/oauth/auth.php',
            access_token_url='https://connect.deezer.com/oauth/access_token.php'
        )

    def get_access_token(self):
        return super().get_access_token()

    def autorization_url(self):
        return super().autorization_url()


class DeezerPlaylists(Playlist):
    def __init__(self):
        self.oauth = DeezerAuth()

    def get_tracks(self):
        return super().get_tracks()

    def get(self):
        return super().get()

