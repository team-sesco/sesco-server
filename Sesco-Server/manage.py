"""
Application Main Manage Module
"""
import click
from flask_jwt_extended import create_access_token
from config import config, APP_NAME
from app import create_sesco_app
import model


application = create_sesco_app(config)


@application.shell_context_processor
def make_shell_context():
    """Init shell context."""
    return dict(app_name=APP_NAME)


@application.cli.command()
def db_init():
    """First, run the Database init controller."""
    model.init_app(config)


@application.cli.command()
@click.argument('id')
def create_jwt(id: str):
    print(create_access_token(id))


if __name__ == "__main__":
    application.run()