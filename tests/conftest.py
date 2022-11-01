import sys
from pathlib import Path
sys.path.append('.')

import pytest
from app import app as flask_app
class AuthActions(object):

    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        self._client.post(
            '/account/register/',
            json={'username': username, 'password': password}
        )
        return self._client.post(
            '/account/login/',
            json={'username': username, 'password': password}
        )
    def logout(self):
        return self._client.get('/account/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True,
    })
    return flask_app

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
