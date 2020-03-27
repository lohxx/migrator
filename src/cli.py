import pdb
import pprint
import click
import asyncio
import time

from migrator import app

from migrator.services.deezer import DeezerPlaylists
from migrator.services.spotify import SpotifyPlaylists
from migrator.services.youtube import YoutubeService

"""
TODO
    1. Buscar as musicas de maneira paralela
    2. Ajustar o algoritimo de match entre as musicas
"""


SERVICES = {
    'deezer': DeezerPlaylists,
    'spotify': SpotifyPlaylists,
    'youtube': YoutubeService
}

options = SERVICES.keys()


class AuthenticationFail(Exception):
    pass


@click.group()
def cli():
    pass


def execute_copy(origin, destination, playlist_name):
    start = time.time()
    try:
        origin_service, destination_service = authenticate(origin, destination)
    except Exception as e:
        click.echo(e)
    else:
        playlist = origin_service.get(playlist_name)
        if playlist:
            destination_service.clone(playlist)

    end = time.time()
    click.echo(f'Levou um total de {end-start} para executar')


@cli.command()
def authenticate():
    """
    Tenta se autenticar nos serviços de streaming
    """
    from service.deezer import DeezerAuth 
    from services.spotify import SpotifyAuth

    try:
        DeezerAuth().authenticate()
    except Exception as e:
        click.echo(e)
    else:
        click.echo('Sua autenticação no Deezer foi bem sucedida')

    try:
        SpotifyAuth().authenticate()
    except Exception as e:
        click.echo(e)
    else:
        click.echo('Sua autenticação no Spotify foi bem sucedida')


@cli.command()
@click.option('--name', required=True)
@click.option('--to-service', type=click.Choice(options), required=True)
@click.option('--from-service', type=click.Choice(options), required=True)
def copy(from_service, to_service, name):

    if from_service == to_service:
        print("O serviço de origem não pode ser o mesmo serviço de destino")
        return

    origin_service = SERVICES.get(from_service)
    destination_service = SERVICES.get(to_service)

    execute_copy(origin_service, destination_service, name)


if __name__ == '__main__':
    cli()
