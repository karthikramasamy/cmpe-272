import pytest
from bookstore.bookstore_db import get_db


def test_get_books(client, auth, app):
    auth.login()
    assert client.get('/api/v1/books').status_code == 200
