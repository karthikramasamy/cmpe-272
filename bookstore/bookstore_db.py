from pymongo import MongoClient
from os import environ as env
import click
import datetime
from flask import current_app, g
from flask.cli import with_appcontext

MONGO_URL = env.get('MONGO_URL')
if not MONGO_URL or MONGO_URL is '':
    MONGO_URL = "mongodb://localhost:27017"

def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db_client' not in g:
        g.db_client = MongoClient(MONGO_URL)
    if 'db' not in g:
        g.db = g.db_client.bookstore
    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db_client = g.pop('db_client', None)

    if db_client is not None:
        db_client.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    # Cleanup database
    clean_up = False

    if clean_up:
        db["books"].delete_many({})
        db["inventory"].delete_many({})
        db["customers"].delete_many({})
        db["orders"].delete_many({})

    # Insert sample data for books
    db.books.insert_many(
        [{
            "_id": "0123456789ab012345678901",
            "title": "Becoming",
            "author": ["Michelle Obama"],
            "language": "English",
            "isbn": "1524763136",
            "price": 10.5,
            "published_date": "2018-11-13",
            "publisher": "Crown Publishing Group"
        }, {
            "_id": "0123456789ab012345678902",
            "title": "Redemption",
            "author": ["David Baldacci"],
            "language": "English",
            "isbn": "1538761459",
            "price": 15.5,
            "published_date": "2019-10-08",
            "publisher": "Grand Central Publishing"
        }, {
            "_id": "0123456789ab012345678903",
            "title": "Milkman: A Novel",
            "author": ["Anna Burns"],
            "language": "English",
            "isbn": "1644450003",
            "price": 25.5,
            "published_date": "2018-12-04",
            "publisher": "Graywolf Press"
        }]
    )

    # Insert sample data for inventory
    db.inventory.insert_many(
        [{
            "book_id": "0123456789ab012345678901",
            "qty": 2,
            "last_modified": datetime.datetime.utcnow()
        }, {
            "book_id": "0123456789ab012345678902",
            "qty": 1,
            "last_modified": datetime.datetime.utcnow()
        }, {
            "book_id": "0123456789ab012345678903",
            "qty": 5,
            "last_modified": datetime.datetime.utcnow()
        }]
    )

    # Insert sample data for customers
    db.customers.insert_many(
        [{
            "_id": "0123456789ab012345678901",
            "name": "Karthik",
            "address": "San Jose, CA",
            "phone": "408-000-001",
            "last_modified": datetime.datetime.utcnow()
        }, {
            "_id": "0123456789ab012345678902",
            "name": "Muthu",
            "address": "San Jose, CA",
            "phone": "408-000-002",
            "last_modified": datetime.datetime.utcnow()
        }, {
            "_id": "0123456789ab012345678903",
            "name": "Anis",
            "address": "San Jose, CA",
            "phone": "408-000-003",
            "last_modified": datetime.datetime.utcnow()
        }]
    )
    return db


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
