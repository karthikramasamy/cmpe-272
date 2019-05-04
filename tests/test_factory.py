from bookstore import create_app
import json


def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_home(client):
    response = client.get('/')
    data = json.loads(response.data)
    assert data['message'] == b'Welcome to the BookStore API'


def test_status(client):
    response = client.get('/status')
    data = json.loads(response.data)
    assert data['message'] == b'OK'
