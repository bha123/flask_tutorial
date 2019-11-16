import os
import tempfile

from flaskr import create_app
from flaskr.db import get_db, init_db

# pytest
import pytest

# Load the test data.sql
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
	_data_sql = f.read().decode('utf8')


# Load the
@pytest.fixture
def app():
	
	# db_fb --  temp file object
	# db_path -- temp file path

	db_fd, db_path = tempfile.mkstemp()

	# get app object

	app = create_app({
			'TESTING' : True,
			'DATABASE': db_path,
		})

	with app.app_context() :
		# initializing database
		init_db()
		# initializing the data sql
		get_db().executescript(_data_sql)

	# app generator
	yield app
	
	# close the file path
	os.close(db_fd)

	# unlink the path
	os.unlink(db_path)	


@pytest.fixture
def client(app):
	return app.test_client()


@pytest.fixture
def runner(app):
	return app.test_cli_runner()


class AuthActions(object):
	def __init__(self, client):
		self._client = client

	def login(self, username='test', password='test'):
		return self._client.post(
			'/auth/login',
			data={'username': username, 'password': password}

			)

	def logout(self):
		return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
	return AuthActions(client)


