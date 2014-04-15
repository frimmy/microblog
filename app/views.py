from app import app
from flask import render_template, flash, redirect
from forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
	user = {'nickname': 'Miguel'} # fake user
	posts = [ # fake array of posts
		{
			'author': { 'nickname': 'John'},
			'body': 'Beautiful day in Portland!',
			'comments':
				[
					{
						'username': 'daylegaylord',
						'comment':'This movie was badass!'
					},
					{
					'username':'badassking1010',
					'comment':'This movie was terrible!'
					}
				]
		},
		{
			'author': {'nickname': 'Susan'},
			'body': 'The Avengers movie was so cool!',
			'comments':
				[
					{
						'username': 'daylegaylord',
						'comment':'This movie was badass!'
					},
					{
					'username':'badassking1010',
					'comment':'This movie was terrible!'
					}
				]
		}
	]
	return render_template('index.html',
		user=user,
		title='Home',
		posts=posts)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for OpenId="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
		return redirect('/index')
	return render_template('login.html',
		title= 'Sign In',
		form = form,
		providers = app.config['OPENID_PROVIDERS'])