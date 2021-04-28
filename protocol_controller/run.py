import click
import logging

from interfaces.sas_interface import SASProtocolController


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def run():
    server = SASProtocolController('sas_interface', 'sas/v1')
    server.add_sas_endpoints()
    server.run()


if __name__ == '__main__':
    run()
