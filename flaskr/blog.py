from flask import (
	Blueprint, render_template, g, redirect, flash, request, url_for
	)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog',__name__)


@bp.route('/')
def index():
	'''
	Indexing the already present blog posts
	'''
	#get the db 
	db = get_db()

	#Get the posts 

	posts = db.execute(
		'SELECT p.id, username, author_id, title, body, created' 
		' FROM post p JOIN user u ON p.author_id=u.id'
		' ORDER BY created  DESC'
		).fetchall()
	return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods= ('GET', 'POST'))
@login_required
def create():
	"""
	Function to create a post
	"""
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		db = get_db()
		#If title is None

		if title is None:
			error = "Provide title for the Post"

		if error is not None:
			flash(error)
		else:
			db.execute(
				'INSERT INTO post  (title, body, author_id) '
				'VALUES (?,?,?) ', (title, body, g.user['id'])

				)
			db.commit()

			return redirect(url_for('blog.index'))

	return render_template('blog/create.html')		



def get_post(id, check_author=True):

	#get the post using ID

	post = get_db().execute(

		'SELECT p.id, title, body, author_id , username'
		' FROM post p JOIN user u on p.author_id = u.id'
		' WHERE p.id = ?',(id,)
		).fetchone()

	

	# if post is not present
	if post is None:
		abort(404, "Post {0} is not present".format(id))

	if check_author and post['author_id'] != g.user['id']:
		abort(403)

	return post


@bp.route('/<int:id>/update', methods=('GET','POST'))
@login_required
def update(id):
	'''
	Create post in the id
	'''
	post = get_post(id)
	if request.method=='POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		if not title:
			error = "Title is required"

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'UPDATE post SET title= ? ,body= ? WHERE id = ?',(title, body, id)

				)
			db.update()

			return redirect(url_for('blog.index'))

	return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
	get_post(id)
	db = get_db()
	db.execute(
		'DELETE FROM post WHERE id= ?',(id,)
		)
	db.commit()
	return redirect(url_for('blog.index'))



