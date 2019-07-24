import click

from migrator.services.spotify import SpotifyService


SERVICES = {
    'spotify': SpotifyService,
    'deezer': None,
    'youtube': None
}

options = ['spotify', 'deezer', 'youtube']


@click.group()
def cli():
    pass


def execute_copy(origin, destination, playlist_name):
    # checar se já existe os dados para autenticação antes de solicitar o browser
    origin_service = origin()
    origin_service.get_playlist(playlist_name)


@cli.command()
@click.option('--playlist-name', required=True)
@click.option('--to-service', type=click.Choice(options), required=True)
@click.option('--from-service', type=click.Choice(options), required=True)
def copy(from_service, to_service, playlist_name):

    if from_service == to_service:
        print("O serviço de origem não pode ser o mesmo serviço de destino")
        return

    # TODO
        # 1. Selecionar o service conforme a escolha do usuario
        # 2. Criar uma interface padrão

    origin_service = SERVICES.get(from_service)
    destination_service = SERVICES.get(to_service)

    execute_copy(origin_service, destination_service, playlist_name)


if __name__ == '__main__':
    cli()
