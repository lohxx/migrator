import click

from migrator.services import spotify


@click.group()
def cli():
    pass


@cli.command()
@click.option('--from-service', type=click.Choice(['spotify', 'deezer', 'youtube']))
@click.option('--to-service', type=click.Choice(['spotify', 'deezer', 'youtube']))
@click.option('--playlist-name')
def migrate(from_service, to_service, playlist_name):
    if from_service == to_service:
        print("O serviço de origem não pode ser o mesmo serviço de destino")
        return


if __name__ == '__main__':
    cli()
