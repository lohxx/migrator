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
    access_token_url='https://accounts.spotify.com/api/toke',
    base_url='https://api.spotify.com/v1/'
)

scopes = [
    'playlist-modify-public',
    'playlist-read-collaborative',
    'playlist-read-private',
    'playlist-modify-private'
]


@cli.command()
def auth():
    data = {'code': os.environ['SPOTIFY_CODE']}
    response = spotify.get_access_token(data=data, decoder=json.loads)


@cli.command()
def authorization_url():
    authorize_url = spotify.get_authorize_url(**{
        'response_type': 'code',
        'redirect_uri': 'http://localhost:5000/callback',
        'scope': 'playlist-read-collaborative'
    })

    print('Por favor, autorize a api')
    webbrowser.open_new_tab(authorize_url)


if __name__ == '__main__':
    cli()