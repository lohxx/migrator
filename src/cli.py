import pdb
import pprint
import click
import time
import os
import pickle
import threading
import http.server

from flask_script import Manager

from src.utils import PickleHandler
from src import app

from src.services.deezer import DeezerPlaylists
from src.services.spotify import SpotifyPlaylists
from src.services.youtube import YoutubeService


SERVICES = {
    'deezer': DeezerPlaylists,
    'spotify': SpotifyPlaylists,
    'youtube': YoutubeService
}

OPTIONS = SERVICES.keys()
pickle_handler = PickleHandler('tokens.pickle')



@click.group()
def cli():
    pass


def execute_copy(origin, destination, playlist_name):
    start = time.time()

    playlist = origin.get(playlist_name)
    if playlist:
        destination.clone(playlist)

    end = time.time()
    click.echo(f'Levou um total de {end-start} para executar')


@cli.command()
@click.option('--name', required=True)
@click.option('--to-service', type=click.Choice(OPTIONS), required=True)
@click.option('--from-service', type=click.Choice(OPTIONS), required=True)
def copy(from_service, to_service, name):
    pickle_handler.write({
        'deezer': {'code': None, 'access_token': None},
        'spotify': {'code': None, 'access_token': None, 'refresh_token': None}
    })

    if from_service == to_service:
        click.echo("O serviço de origem não pode ser o mesmo serviço de destino")
        return

    origin_service = SERVICES.get(from_service)()
    destination_service = SERVICES.get(to_service)()

    execute_copy(origin_service, destination_service, name)


if __name__ == '__main__':
    cli()
