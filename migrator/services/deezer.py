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


class DeezerRequests:
    def __init__(self):
        self.oauth = DeezerAuth()

    def get(self, endpoint, q=None):
        response = self.oauth.session.get('http://api.deezer.com/'+endpoint, params=q)

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    def post(self, endpoint, data=None):
        response = self.oauth.session.post('http://api.deezer.com/'+endpoint, params=data)

        if response.status_code not in (200, 201):
            raise Exception(response.text)

        return response.json()


class DeezerPlaylists(Playlist):
    def __init__(self):
        self.requests = DeezerRequests()
        self.user = self.requests.get('user/me')

    def get_tracks(self, tracks_url):
        tracks = []
        playlist_tracks = self.requests.get(tracks_url)

        for track in playlist_tracks['data']:
            tracks.append({
                'name': track['title'],
                'album': track['album']['title'],
                'artists': [track['artist']['name']]
            })

        return tracks

    def get(self, name):
        click.echo('Procurando a playlist...')
        playlists = self.requests.get(f'/user/{self.user["id"]}/playlists')

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
        playlist_id = self.requests.post(f'user/{self.user["id"]}/playlists', {'title': name})['id']

        cache = []
        track_ids = []
        for track in tracks:
            params = {'q': f'album:"{track["album"]}" track:"{track["name"]}" artist:"{track["artists"][0]}"'}
            matches = self.requests.get('search/', q=params)
            for match in matches['data']:
                track_already_added = f'{match["title"]} - {match["artist"]["name"]}'
                if track['name'] == match['title'] and match['artist']['name'] in track['artists'] and track_already_added not in cache:
                    cache.append(track_already_added)
                    click.echo(f'{track["name"]} - {track["artists"][0]} encontrado!')
                    track_ids.append(str(match['id']))
                    continue
                else:
                    click.echo(f'{track["name"]} - {track["artists"][0]} não foi encontrado')
        if track_ids:
            import pdb; pdb.set_trace()
            self.requests.post(f'playlist/{playlist_id}/tracks', data={'songs': ','.join(set(track_ids))})
