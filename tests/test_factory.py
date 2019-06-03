from bookstore import create_app
import json


def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_status(client):
    response = client.get('/status')
    data = response.get_json()
    assert data['message'] == 'OK'
