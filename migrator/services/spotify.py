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
        callback_url = '/callback/spotify'

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

    def get(self, endpoint: str, q:str=None):
        """
        Busca informações.
        
        Args:
            endpoint (str): endpoint da requisição.
            q (str, optional): params da url. Defaults to None.
        
        Raises:
            Exception: levanta exceção quando a requisição falha.
        
        Yields:
            [type]: retorna o objeto devolvido pelo request.
        """        
        response = self.oauth.session.get(endpoint, params=q)
        if response.status_code != 200:
            raise Exception(response.text)

        response = response.json()
        while response.get('next'):
            yield response
            response = self.oauth.session.get(response['next']).json()

        # itens sem paginação
        yield response

    def post(self, endpoint: str, data: dict) -> dict:
        """
        Envia informações para o serviço de streaming.
        
        Args:
            endpoint (str): endpoint da requisição.
            data (dict): dados que serão enviados.
        
        Raises:
            Exception: levanta exceção quando a requisição falha.
        
        Returns:
            dict: resposta da requisição.
        """        
        response = self.oauth.session.post(endpoint, json=data)

        if response.status_code not in (200, 201):
            raise Exception(response.text)

        return response.json()


class SpotifyPlaylists(Playlist):
    def __init__(self):
        self.requests = SpotifyRequests()

    def search_playlist(self, name: str) -> dict:
        """
        Busca a playlist no serviço de streaming.
        
        Args:
            name (str): nome da playlist.
        
        Returns:
            dict: infos da playlist.
        """        
        for playlist_group in self.requests.get('v1/me/playlists'):
            for playlist in playlist_group['items']:
                if playlist['name'] == name:
                    return playlist
        else:
            return {}

    def get_tracks(self, tracks_url: str) -> [dict]:
        """
        Busca as musicas de uma playlist.
        
        Args:
            tracks_url (str): url das musicas da playlist.
        
        Returns:
            [dict]: lista com as infos das musicas.
        """        
        click.echo('Buscando as musicas...')

        tracks = []
        response = next(self.requests.get(tracks_url))

        for track in response['items']:
            tracks.append({
                'name': track['track']['name'].lower(),
                'album': track['track']['album']['name'],
                'artists': list(
                    map(
                        lambda artists: artists['name'],
                        track['track']['artists']
                    )
                )
            })

        return tracks

    def get(self, name: str) -> dict:
        """
        Busca a playlist.

        Arguments:
            name {str} -- nome da playlist.
        
        Returns:
            dict -- dicionario com as infos da playlist.
        """        
        click.echo('Procurando a playlist...')

        playlist = self.search_playlist(name)

        if playlist:
            click.echo('Playlist encotrada!')
            tracks = self.get_tracks(playlist['tracks']['href'])
            return {'playlist': name, 'tracks': tracks}

        click.echo('Não foi possivel achar a playlist, verifique se o nome esta correto')
        return {}

    def copy(self, playlist: dict):
        """
        Copia a playlist de um serviço de streaming.
        
        Args:
            playlist (dict): infos da playlist que vai ser copiada.
        """        
        name, tracks = playlist.values()
        playlist = self.search_playlist(name)

        if playlist:
            tracks = self._diff_tracks(self.get_tracks(playlist['tracks']['href']), tracks)
        else:
            playlist = self.requests.post('/v1/me/playlists', {"name": name, "public": True})

        playlist_tracks = []
        for track in tracks:
            params = {'q': f'artist:{track["artists"][0]} track:{track["name"]} album:{track["album"]}', 'type': 'track'}
            matches = next(self.requests.get(f'/v1/search/', q=params)).get('tracks', {})

            for match in matches.get('items'):
                if self.match_track(track['name'], match['name']):
                    playlist_tracks.append(match['uri'])

        if playlist_tracks:
            response = self.requests.post(f'v1/playlists/{playlist["id"]}/tracks', {'uris': playlist_tracks})
            if response:
                click.echo('A playlist foi copiada com sucesso')

    def playlists(self) -> []:
        """
        Busca todas as playlists de um usuario.
        
        Returns:
            list: playlists
        """        
        return list(self.requests.get('/v1/me/playlists'))