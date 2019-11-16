import functools

from flask import(
	Blueprint, g , session, render_template, request, url_for, redirect, flash
	)

from flaskr.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
bp = Blueprint('auth', __name__, url_prefix ='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
	"""
	Register the user 
	"""
	# Checking whether the method is PUT
	if request.method == 'POST':

		# Getting the details of username and password
		# from the FORM

		username = request.form['username']
		password = request.form['password']
		# Connect to database
		db = get_db()

		# Declaring error with None
		error = None 

		if not username:
			error = 'Username not provided'
		elif not password:
			error = 'Password not provided'
		elif db.execute(
			'SELECT  id FROM user WHERE username = ?', (username,)
		).fetchone() is not None:
			error = 'User {} is already registered'.format(username)

		if error is None:
			db.execute(
				'INSERT into user (username, password) VALUES (?,?)', (
					username,
					generate_password_hash(password))
				)	
			db.commit()
			return redirect(url_for('auth.login'))

		flash(error)

	return render_template('auth/register.html')


@bp.route('/login', methods=('GET','POST'))
def login():
	'''
	login view to create session element 
	with username and password
	'''
	if request.method == 'POST':
		# Fetch the username and password requested
		username = request.form['username']
		password = request.form['password']

		# connect to db
		db = get_db()

		# set error variable
		error = None

		# fetch username and password 

		user = db.execute(
			'SELECT * FROM user WHERE username = ?', (username,)
			).fetchone()

		if user is None:
			error = 'Incorrect Username'
		elif not check_password_hash(user['password'], password):
			error = 'Incorrect Password'

		if error is None:
			session.clear()
			session['user_id'] = user['id']
			return redirect(url_for('blog.index'))

		flash(error)

	return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
	"""
	Load the logged in user with g.user
	"""
	user_id = session.get('user_id')
	db = get_db()
	if user_id is None:
		g.user = None
	else:
		g.user = get_db().execute(
			'SELECT * FROM user WHERE id = ?', (user_id,)
			).fetchone()


@bp.route('/logout')
def logout():
	'''
	logout is used to clear the session object
	'''
	session.clear()
	return redirect(url_for('blog.index'))


# Create a wrap function which will check whether a function
# a g.user is present or not if not return login.html
def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kargs)
	return wrapped_view
