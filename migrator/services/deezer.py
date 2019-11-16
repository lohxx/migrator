import os
import requests
import pdb
import re
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

        self.base_url = self.oauth.base_url

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
        if self.oauth.base_url not in endpoint:
            response = self.oauth.session.get(self.oauth.base_url+endpoint, params=q).json()
        else:
            response = self.oauth.session.get(endpoint, params=q).json()

        if response.get('error'):
            raise Exception(response['message'])

        return response

    def post(self, endpoint, data=None):
        response = self.oauth.session.post(self.oauth.base_url+endpoint, params=data)

        if response.status_code not in (200, 201):
            raise Exception(response.text)

        return response.json()


class DeezerPlaylists(Playlist):
    def __init__(self):
        self.requests = DeezerRequests()
        self.user = self.requests.get('user/me')

    def search_playlist(self, name):
        playlists = self.requests.get(f'/user/{self.user["id"]}/playlists')

        for playlists in playlists['data']:
            if playlists['title'] == name:
                return playlists
        else:
            return {}

    def get_tracks(self, tracks_url):
        tracks = []
        playlist_tracks = self.requests.get(tracks_url)

        for track in playlist_tracks.get('data', []):
            tracks.append({
                'name': track['title'].lower(),
                'album': track['album']['title'],
                'artists': [track['artist']['name']]
            })

        return tracks

    def get(self, name):
        click.echo('Procurando a playlist...')
        playlist = self.search_playlist(name)

        if playlist:
            click.echo('Playlist encotrada!')
            tracks = self.get_tracks(playlist['tracklist'])
            return {'playlist': name, 'tracks': tracks}

        click.echo('Não foi possivel achar a playlist, verifique se o nome esta correto')
        return {}

    def copy(self, playlist):
        name, tracks = playlist.values()

        playlist = self.search_playlist(name)
        if playlist:
            tracks = self._diff_tracks(self.get_tracks(playlist['tracklist']), tracks)
        else:
            playlist = self.requests.post(f'user/{self.user["id"]}/playlists', {'title': name})

        track_ids = []
        tracks_found = []
        tracks_not_found = []

        for track in tracks:
            params = {'q': f'track:"{track["name"]}" artist:"{track["artists"][0]}"&strict=on'}
            matches = self.requests.get('search/', q=params)

            for match in matches['data']:
                new_track, copy_track = self.match_track(track['name'], match['title'])
                if copy_track and new_track not in tracks_found:
                    tracks_found.append(new_track)
                    track_ids.append(str(match['id']))
                    continue
                else:
                    tracks_not_found.append(new_track)

        if track_ids:
            response = self.requests.post(f'playlist/{playlist["id"]}/tracks', data={'songs': ','.join(set(track_ids))})
            if response:
                click.echo('A playlist foi copiada com sucesso')

        for track in (set(tracks_not_found) - set(tracks_found)):
            click.echo(f'A musica: {track} não foi encontrada')
    
    def playlists(self):
        return self.requests.get(f'user/{self.user["id"]}/playlists')
