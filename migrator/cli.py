import pdb
import pprint
import click


from migrator.services.deezer import DeezerPlaylists
from migrator.services.spotify import SpotifyPlaylists
from migrator.services.youtube import YoutubeService


SERVICES = {
    'deezer': DeezerPlaylists,
    'spotify': SpotifyPlaylists,
    'youtube': YoutubeService
}

options = SERVICES.keys()


@click.group()
def cli():
    pass


def execute_copy(origin, destination, playlist_name):
    origin_service = origin()
    playlist = origin_service.get(playlist_name)
    pprint.pprint(playlist)


@cli.command()
@click.option('--playlist-name', required=True)
@click.option('--to-service', type=click.Choice(options), required=True)
@click.option('--from-service', type=click.Choice(options), required=True)
def copy(from_service, to_service, playlist_name):

    if from_service == to_service:
        print("O serviço de origem não pode ser o mesmo serviço de destino")
        return

    origin_service = SERVICES.get(from_service)
    destination_service = SERVICES.get(to_service)

    execute_copy(origin_service, destination_service, playlist_name)


if __name__ == '__main__':
    cli()
