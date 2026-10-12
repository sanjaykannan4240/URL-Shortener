import os
import tempfile

import pytest

from app import app as flask_app


@pytest.fixture()
def client():
    handle, path = tempfile.mkstemp(suffix='.db')
    os.close(handle)
    flask_app.config.update(TESTING=True)
    import app as app_module
    old_database = app_module.DATABASE
    app_module.DATABASE = path
    app_module.init_db()
    with flask_app.test_client() as test_client:
        yield test_client
    app_module.DATABASE = old_database
    os.unlink(path)


def test_create_and_redirect(client):
    response = client.post('/api/shorten', json={'url': 'https://example.com/docs'})
    assert response.status_code == 201
    data = response.get_json()
    assert len(data['short_code']) == 7
    redirect_response = client.get('/' + data['short_code'])
    assert redirect_response.status_code == 302
    assert redirect_response.location == 'https://example.com/docs'


def test_custom_code_and_duplicate(client):
    response = client.post('/api/shorten', json={'url': 'https://example.com', 'custom_code': 'launch'})
    assert response.status_code == 201
    duplicate = client.post('/api/shorten', json={'url': 'https://example.org', 'custom_code': 'launch'})
    assert duplicate.status_code == 409


def test_invalid_url(client):
    response = client.post('/api/shorten', json={'url': 'not-a-url'})
    assert response.status_code == 400


def test_list_urls(client):
    client.post('/api/shorten', json={'url': 'https://example.com'})
    response = client.get('/api/urls')
    assert response.status_code == 200
    assert len(response.get_json()['urls']) == 1
