from flask_sqlalchemy import SQLAlchemy

import click
from flask import current_app, g
from flask.cli import with_appcontext

db = SQLAlchemy()


def get_db():
    if 'db' not in g:
        g.db = SQLAlchemy()

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as schema:
        db.executescript(schema.read().decode('utf8'))

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def test():
    curs = get_db().cursor()
    curs.execute('INSERT INTO user (username, password_hash) VALUES ("Tony", "134")')
    curs.execute("SELECT * FROM user")
    print(curs.fetchone()[1])
