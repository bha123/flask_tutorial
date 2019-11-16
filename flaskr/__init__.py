# Here the app object will be created

import os

from flask import Flask 

#Create app instace 
def create_app(test_config=None):
	#Create app instance
	app = Flask(__name__, instance_relative_config=True)

	#load configuration for the app

	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
		)

	# load test configuration
	if test_config is None:
		app.config.from_pyfile('config.py', silent = True)
	else:
		app.config.from_mapping(test_config)

	# Check whether the app instance path is present

	try:
		os.mkdir(app.instance_path)
	except OSError:
		pass

	from . import db 
	db.init_app(app)

	from . import auth
	app.register_blueprint(auth.bp)

	from . import blog
	app.register_blueprint(blog.bp)
	app.add_url_rule('/',endpoint='index')
	
	@app.route('/hello')
	def hello():
		return 'Hello World!'

	app.add_url_rule('/','index')
	return app