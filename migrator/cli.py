import click

from migrator.services import spotify


SERVICES = {
    'spotify': spotify,
    'deezer': None,
    'youtube': None
}


@click.group()
def cli():
    pass


def execute_copy(origin, destination):
    pass


@cli.command()
@click.option('--from-service', type=click.Choice(['spotify', 'deezer', 'youtube']))
@click.option('--to-service', type=click.Choice(['spotify', 'deezer', 'youtube']))
@click.option('--playlist-name')
def copy(from_service, to_service, playlist_name):

    if from_service == to_service:
        print("O serviço de origem não pode ser o mesmo serviço de destino")
        return

    # TODO
        # 1. Selecionar o service conforme a escolha do usuario
        # 2. Criar uma interface padrão

    origin_service = SERVICES.get(from_service)
    destination_service = SERVICES.get(to_service)


if __name__ == '__main__':
    cli()
