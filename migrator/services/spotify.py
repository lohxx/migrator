import itertools
import json
import os
import pdb
import webbrowser

import click
import requests

from flask import request
from rauth import OAuth2Service
import sqlalchemy.orm.exc as sq_exceptions

from migrator import app
from migrator.services.tokens import save_tokens, get_tokens
from migrator.services.interfaces import Playlist, ServiceAuth


class SpotifyAuth(ServiceAuth):
    SERVICE_CODE = 1

    def __init__(self):
        self.oauth = OAuth2Service(
            name='spotify',
            base_url='https://api.spotify.com/v1',
            client_id=os.environ['SPOTIFY_CLIENT_ID'],
            client_secret=os.environ['SPOTIFY_CLIENT_SECRET'],
            authorize_url='https://accounts.spotify.com/authorize',
            access_token_url='https://accounts.spotify.com/api/token'
        )

    @property
    def session(self):
        session = None
        data = {
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:5000/spotify/callback'
        }

        try:
            tokens = get_tokens(self.SERVICE_CODE)
            data.update({'code': tokens.code})
        except sq_exceptions.NoResultFound as e:
            self.autorization_url({
                'response_type': 'code',
                'redirect_uri': 'http://localhost:5000/spotify/callback',
                'scope': ', '.join([
                    'playlist-modify-public',
                    'playlist-read-collaborative',
                    'playlist-read-private',
                    'playlist-modify-private'
                ])
            })
            tokens = get_tokens(self.SERVICE_CODE)
            data.update({'code': tokens.code})

        session = self._get_access_token(data)
        save_tokens(self.SERVICE_CODE, session.access_token_response.json())

        return session


class SpotifyRequests:
    def __init__(self):
        self.oauth = SpotifyAuth()

    def get(self, endpoint, q=None):
        response = self.oauth.session.get(endpoint, params=q)
        if response.status_code != 200:
            raise Exception(response.text)

        response = response.json()
        while response.get('next'):
            yield response
            response = self.oauth.session.get(response['next']).json()

        # itens sem paginação
        yield response

    def post(self, endpoint, data):
        response = self.oauth.session.post(endpoint, json=data)

        if response.status_code not in (200, 201):
            raise Exception(response.text)

        return response.json()


class SpotifyPlaylists(Playlist):
    def __init__(self):
        self.requests = SpotifyRequests()

    def get_tracks(self, tracks_url):
        click.echo('Buscando as musicas...')

        tracks = []
        response = next(self.requests.get(tracks_url))

        for track in response['items']:
            tracks.append({
                'name': track['track']['name'],
                'album': track['track']['album']['name'],
                'artists': list(
                    map(
                        lambda artists: artists['name'],
                        track['track']['artists']
                    )
                )
            })

        return tracks

    def get(self, name):
        click.echo('Procurando a playlist...')

        for playlist in self.requests.get('v1/me/playlists'):
            for pl in playlist['items']:
                if pl['name'] == name:
                    click.echo('Playlist encotrada!')
                    tracks = self.get_tracks(pl['tracks']['href'])
                    return {'playlist': name, 'tracks': tracks}
        else:
            click.echo('Não foi possivel achar a playlist, verifique se o nome esta correto')

    def copy(self, playlist):
        name, tracks = playlist.values()

        playlist = self.get(name)

        if not playlist:
            playlist = self.requests.post(
                '/v1/me/playlists',
                {
                    "name": name,
                    "description": "New playlist description",
                    "public": True
                }
            )

        playlist_tracks = []
        for track in tracks:
            params = {'q': f'{track["artists"][0]} {track["name"]} album:{track["album"]}', 'type': 'track'}
            matches = next(self.requests.get(f'/v1/search/', q=params)).get('tracks', {})

            for match in matches.get('items'):
                artists = list(filter(lambda i: i['name'] in track['artists'], match['artists']))
                if artists and track['name'] in match['name'] and match['album']['name'] == track['album']:
                    playlist_tracks.append(match['uri'])

        if playlist_tracks:
            # nao adicionar as musicas que já existem na playlist
            response = self.requests.post(f'v1/playlists/{playlist["id"]}/tracks', {'uris': playlist_tracks})
            if response:
                click.echo('A playlist foi copiada com sucesso')
