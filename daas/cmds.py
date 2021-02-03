import base64

from flask import current_app
from flask.cli import with_appcontext
import click

from .exts import db

@click.command("db-init")
@with_appcontext
def db_init():
    db.create_all(app=current_app)
    
    click.echo("Initialized SQLite database")
