import json
import os
import pdb
import webbrowser

import click

from rauth import OAuth2Service

@click.group()
def cli():
    pass

spotify = OAuth2Service(
    name='spotify',
    client_id=os.environ['SPOTIFY_CLIENT_ID'],
    client_secret=os.environ['SPOTIFY_CLIENT_SECRET'],
    authorize_url='https://accounts.spotify.com/authorize',
    access_token_url='https://accounts.spotify.com/api/token',
    base_url='https://api.spotify.com/v1/'
)


# TODO:
    # 1. Adicionar tabela para salvar o access_token, refresh_token e o code
    # 2. Criar flags para identificar o deezer, spotify e o youtube

@cli.command()
def auth():
    data = {
        'code': os.environ['SPOTIFY_CODE'],
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:5000/callback'
    }
 
    session = spotify.get_auth_session(data=data, decoder=json.loads)

    response = session.access_token_response.json()
    os.environ['SPOTIFY_REFRESH_TOKEN'] = response.get('refresh_token') 
    os.environ['SPOTIFY_ACCESS_TOKEN'] = response.get('access_token')


@cli.command()
def authorization_url():
    scopes = [
        'playlist-modify-public',
        'playlist-read-collaborative',
        'playlist-read-private',
        'playlist-modify-private'
    ]
    authorize_url = spotify.get_authorize_url(**{
        'response_type': 'code',
        'redirect_uri': 'http://localhost:5000/callback',
        'scope': ', '.join(scopes)
    })

    print('Por favor, autorize a api')
    webbrowser.open_new_tab(authorize_url)


if __name__ == '__main__':
    cli()