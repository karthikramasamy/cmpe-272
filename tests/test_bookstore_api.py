import pytest
import json
from bookstore.bookstore_db import get_db


def test_get_books(client, auth, app):
    response = client.get('/api/v1/books')

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert response.status_code == 200
    assert data is not None and len(data) > 0


def test_get_book_by_isbn(client, auth, app):
    response = client.get('/api/v1/books/1524763136')

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert response.status_code == 200
    assert data['isbn'] == '1524763136'


def test_place_order(client):

    json_data = {
        "customer_id": "0123456789ab012345678901",
        "items": [{"book_id": "0123456789ab012345678903", "qty": 1}]
    }

    response = client.post('/api/v1/orders', json=json_data)

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert data['status'] == 'Created'


def test_fulfill_order(client):

    json_data = {
        "customer_id": "0123456789ab012345678901",
        "items": [{"book_id": "0123456789ab012345678903", "qty": 1}]
    }

    response = client.post('/api/v1/orders', json=json_data)

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert data['status'] == 'Created'

    order_id = data['_id']

    response = client.put('/api/v1/orders/' + order_id)

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()
    assert data['status'] == 'Fulfilled'