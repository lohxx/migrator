import os
import concurrent.futures

import click

from rauth import OAuth2Service
import sqlalchemy.orm.exc as sq_exceptions

from migrator.services.tokens import save_tokens, get_tokens
from migrator.services.interfaces import Playlist, ServiceAuth


class SpotifyAuth(ServiceAuth):
    SERVICE_CODE = 1

    def __init__(self):
        self.session = None
        self.oauth = OAuth2Service(
            name='spotify',
            base_url='https://api.spotify.com/v1',
            client_id=os.environ['SPOTIFY_CLIENT_ID'],
            client_secret=os.environ['SPOTIFY_CLIENT_SECRET'],
            authorize_url='https://accounts.spotify.com/authorize',
            access_token_url='https://accounts.spotify.com/api/token'
        )

    def save_code_and_authenticate(self, params):
        save_tokens(self.SERVICE_CODE, params)
        self.authenticate()

    def authenticate(self):
        try:
            tokens = get_tokens(self.SERVICE_CODE)
        except sq_exceptions.NoResultFound:
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
        else:
            self.session = self._get_access_token({
                'code': tokens.code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://localhost:5000/spotify/callback'
            })
            save_tokens(
                self.SERVICE_CODE,
                self.session.access_token_response.json())


class SpotifyRequests:
    """
    Lida com as playlists do Spotify
    """

    def __init__(self):
        self.oauth = SpotifyAuth()

        # tenta conseguir a permissão do usuario
        # para ler e modificar as playlists
        self.oauth.authenticate()

    @staticmethod
    def paginate(response: dict, queryparams=None):
        self = SpotifyRequests()

        paginated_response = []
        if 'items' in response:
            paginated_response.extend(response['items'])

            while len(paginated_response) < response['total']:
                if response.get('next'):
                    response = self.oauth.session.get(
                        response.get('next'), params=queryparams).json()
                    paginated_response.extend(response['items'])
        else:
            paginated_response = response

        return paginated_response

    def get(self, endpoint: str, queryparams: str = None) -> None:
        """
        Busca informações.

        Args:
            endpoint (str): endpoint da requisição.
            queryparams (str, optional): params da url. Defaults to None.

        Raises:
            Exception: levanta exceção quando a requisição falha.

        Returns:
            [type]: retorna o objeto devolvido pelo request.
        """
        response = self.oauth.session.get(endpoint, params=queryparams)
        if response.status_code != 200:
            raise Exception(response.text)

        response = response.json()

        paginated_response = self.paginate(response)

        return paginated_response

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
        playlist_group = self.requests.get('v1/me/playlists')

        for playlist in playlist_group:
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
            [list]: lista com as infos das musicas.
        """
        click.echo('Buscando as musicas...')

        tracks = []
        playlist_tracks = self.requests.get(tracks_url)

        for track in playlist_tracks:
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

    def make_futures(self, executor, tracks):
        futures = {}

        for track in tracks:
            params = {'q': f'artist:{track["artists"][0]} track:{track["name"]} album:{track["album"]}', 'type': 'track'}
            futures[executor.submit(self.requests.get, '/v1/search/', params)] = track

        return futures

    def clone(self, playlist: dict) -> None:
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

        # Não duplicar as musicas na hora de copiar

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_track = self.make_futures(executor, tracks)

            for future in concurrent.futures.as_completed(future_to_track):
                track = future_to_track[future]

                try:
                    matches = future.result()
                except Exception as exc:
                    click.echo(exc)
                else:
                    matches_paginated = SpotifyRequests.paginate(matches.get('tracks', {}))
                    for match in matches_paginated:
                        if self.match_track(track['name'], match['name']):
                            playlist_tracks.append(match['uri'])

        if playlist_tracks:
            response = self.requests.post(
                f'v1/playlists/{playlist["id"]}/tracks',
                {'uris': playlist_tracks}
            )

            if response:
                click.echo('A playlist foi copiada com sucesso')