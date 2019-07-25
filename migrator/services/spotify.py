import itertools
import json
import os
import pdb
import webbrowser

import click

from rauth import OAuth2Service


from migrator import app
from migrator.services.auth import ServiceAuth


class SpotifyService(ServiceAuth):
    def __init__(self):
        try:
            self.oauth = OAuth2Service(
                name='spotify',
                base_url='https://api.spotify.com/v1',
                client_id=os.environ['SPOTIFY_CLIENT_ID'],
                client_secret=os.environ['SPOTIFY_CLIENT_SECRET'],
                authorize_url='https://accounts.spotify.com/authorize',
                access_token_url='https://accounts.spotify.com/api/token'
            )
        except KeyError as e:
            app.logger.exception(e)

    def autorization_url(self):
        scopes = [
            'playlist-modify-public',
            'playlist-read-collaborative',
            'playlist-read-private',
            'playlist-modify-private'
        ]
        authorize_url = self.oauth.get_authorize_url(**{
            'response_type': 'code',
            'redirect_uri': 'http://localhost:5000/callback',
            'scope': ', '.join(scopes)
         })

        app.logger.info(authorize_url)
        webbrowser.open(authorize_url)

        return self

    def paginate(self):
        pass

    @property
    def session(self):
        # achar uma maneira de sempre checar se o token expirou antes de fazer um request
        data = {
            'code': os.environ['SPOTIFY_CODE'],
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:5000/callback'
        }

        try:
            session = self.oauth.get_auth_session(data=data, decoder=json.loads)
        except Exception as e:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': os.environ['refresh_token']
            }
            session = self.oauth.get_auth_session(data=data, decoder=json.loads)
            click.echo(session.access_token_response.json())

        response = session.access_token_response.json()
        return session

    def request(self, endpoint, page=0, limit=30):
        response = self.session.get(endpoint)

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    def get_playlist_tracks(self, tracks_url):
        click.echo('Buscando as musicas...')

        tracks = []
        response = self.request(f"v1/{'/'.join(tracks_url.split('/')[-3:])}")

        for track in response['items']:
            tracks.append({
                'name': track['track']['name'],
                'artists': list(
                    map(
                        lambda artists: artists['name'],
                        track['track']['artists']
                    )
                )
            })

        return tracks

    def get_playlist(self, name):
        click.echo('Procurando a playlist...')
        playlists = self.request('v1/me/playlists')

        for playlist in playlists['items']:
            if playlist['name'] == name:
                click.echo('Playlist encotrada!')
                tracks = self.get_playlist_tracks(playlist['tracks']['href'])

                return {'playlist': name, 'tracks': tracks}
        else:
            click.echo('Não foi possivel achar a playlist, verifique se o nome esta correto')


# TODO:
    # 1. Adicionar tabela para salvar o access_token, refresh_token e o code
    # 2. Criar flags para identificar o deezer, spotify e o youtube
    # 3. Colocar o sqlite para funcionar
    # 4. Separara a autenticação das buscas?
