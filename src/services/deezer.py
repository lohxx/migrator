import os
import sys
import json
import concurrent.futures

import click
import requests

from rauth import OAuth2Service
import sqlalchemy.orm.exc as sq_exceptions

from src import read_pickle, write_keys

from src.services.interfaces import Playlist, ServiceAuth


class DeezerAuth(ServiceAuth):

    def __init__(self):
        self.session = requests.Session()
        self.oauth = OAuth2Service(
            name='deezer',
            base_url='https://api.deezer.com/',
            client_id=os.environ['DEEZER_CLIENT_ID'],
            client_secret=os.environ['DEEZER_CLIENT_SECRET'],
            authorize_url='https://connect.deezer.com/oauth/auth.php',
            access_token_url='https://connect.deezer.com/oauth/access_token.php'
        )

        self.base_url = self.oauth.base_url

    def _get_access_token(self, args):
        session = requests.Session()
        response = session.get(self.oauth.access_token_url, params=args)

        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            click.echo(response.content)
            sys.exit(1)

    def save_code_and_authenticate(self, response):
        code = response.get('code', '')

        try:
            tokens = read_pickle()
            tokens['deezer']['code'] = code
            write_keys(tokens)
        except Exception:
            pass

        self.authenticate(code)

    def authenticate(self, code=None):
        tokens = read_pickle()

        if not tokens['deezer']['code']:
            self.autorization_url({
                'app_id': self.oauth.client_id,
                'perms': 'manage_library, offline_access',
                'redirect_uri': 'http://localhost:5000/deezer/callback'
            })
            return

        if not tokens['deezer']['access_token']:
            # Tenta pegar o access_token
            response = self._get_access_token({
                'output': 'json',
                'app_id': self.oauth.client_id,
                'secret': self.oauth.client_secret,
                'code': tokens['deezer']['code'],
            })

            tokens['deezer']['access_token'] = response['access_token']
            write_keys(tokens)

            return

        # associa o token com a session
        self.session.params = {
            'access_token': tokens['deezer']['access_token']}


class DeezerRequests:
    """
    Realiza requisições na api do deezer.
    """
    def __init__(self):
        self.oauth = DeezerAuth()

        # tenta conseguir a permissão do usuario
        # para ler e modificar as playlists
        self.oauth.authenticate()

    def paginate(self, response, params=None) -> list:
        """
        Junta todos os resultados paginados de um request.

        Args:
            response (dict): resposta devolvida pela api do Spotify.
            params (dict, optional): [description]. Defaults to None.

        Returns:
            list: lista com todos os resultados do request.
        """

        paginated_response = []

        if 'data' in response:
            paginated_response.extend(response['data'])
            while len(paginated_response) < response.get('total'):
                if response.get('next'):
                    response = self.oauth.session.get(
                        response.get('next'), params=params).json()
                    paginated_response.extend(response['data'])

                if not response.get('next') and response.get('prev'):
                    break
        else:
            paginated_response = response

        return paginated_response

    def get(self, endpoint: str, querystring: dict = None):
        """
        [summary]

        Args:
            endpoint (str): [description]
            querystring (dict, optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """    
        if self.oauth.base_url not in endpoint:
            endpoint = self.oauth.base_url+endpoint
        response = self.oauth.session.get(endpoint, params=querystring)
        response = response.json()

        if response.get('error'):
            click.echo(response['error']['message'])
            sys.exit(1)

        return self.paginate(response)

    def post(self, endpoint, data=None):
        response = self.oauth.session.post(
            self.oauth.base_url+endpoint, params=data)

        if response.status_code not in (200, 201):
            raise Exception(response.text)

        return response.json()


class DeezerPlaylists(Playlist):
    """
    Lida com as playlists do Deezer.
    """

    def __init__(self):
        self.requests = DeezerRequests()
        self.user = self.requests.get('user/me')

    def search_playlist(self, name: str) -> dict:
        """
        Busca uma playlist.

        Args:
            name (str): nome da playlist

        Returns:
            [type]: [description]
        """
        playlists = self.requests.get(f'/user/{self.user["id"]}/playlists')

        for playlists in playlists:
            if playlists['title'] == name:
                return playlists
        else:
            return {}

    def get_tracks(self, tracks_url: str) -> [dict]:
        """
        Busca as musicas de uma playlist.

        Args:
            tracks_url (str): url das musicas da playlist.

        Returns:
            list[dict]: lista de dicionarios com informações
            sobre as musicas da playlist.
        """

        tracks = []
        playlist_tracks = self.requests.get(tracks_url)

        for track in playlist_tracks:
            tracks.append({
                'name': track['title_short'].lower(),
                'album': track['album']['title'],
                'artists': [track['artist']['name']]
            })

        return tracks

    def get(self, name: str) -> dict:
        """
        Busca uma playlist.

        Args:
            name (str): nome da playlist

        Returns:
            dict: dict contendo informações da playlist.
        """
        click.echo('Procurando a playlist...')
        playlist = self.search_playlist(name)

        if playlist:
            click.echo('Playlist encotrada!')
            tracks = self.get_tracks(playlist['tracklist'])
            return {'playlist': name, 'tracks': tracks}

        click.echo('Não foi possivel achar a playlist, verifique se o nome esta correto')
        return {}

    def make_futures(self, executor, tracks):
        futures = {}

        for track in tracks:
            search_params = {'q': f'track:"{track["name"]}" artist:"{track["artists"][0]}" album:"{track["album"]}"&strict=on'}
            futures[executor.submit(self.requests.get, 'search/', search_params)] = track

        return futures

    def clone(self, playlist: dict) -> None:
        """
        Copia uma playlist.

        Args:
            playlist (dict): playlist que vai ser copiada.
        """

        name, tracks = playlist.values()

        # checa se já existe uma playlist com esse mesmo nome no serviço
        # para onde essa playlist vai ser copiada.
        playlist = self.search_playlist(name)

        if playlist:
            # copia apenas as musicas que ainda não existem lá
            tracks = self._diff_tracks(
                self.get_tracks(playlist['tracklist']), tracks)
        else:
            playlist = self.requests.post(
                f'user/{self.user["id"]}/playlists', {'title': name})

        tracks_cache = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=28) as executor:
            future_to_track = self.make_futures(executor, tracks)

            for future in concurrent.futures.as_completed(future_to_track):
                track = future_to_track[future]

                try:
                    matches = future.result()
                except Exception as exc:
                    click.echo(exc)
                else:
                    for match in matches:
                        print(match['title'])
                        new_track, copy_track = self.match_track(
                            track['name'], match['title'])

                        if copy_track and new_track not in tracks_cache:
                            tracks_cache[new_track] = str(match['id'])

            if tracks_cache:
                response = self.requests.post(
                    f'playlist/{playlist["id"]}/tracks', data={'songs': ','.join(tracks_cache.values())})

                if response:
                    click.echo('A playlist foi copiada com sucesso')

        # for track in tracks_not_found - tracks_found:
        #     click.echo(f'A musica: {track} não foi encontrada')
