from flask import render_template, flash, redirect, session, url_for, request, g, make_response, jsonify, Response
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, PostForm
from models import User, ROLE_USER, ROLE_ADMIN, Post
from urllib2 import urlopen
from json import loads
from datetime import datetime
from config import POSTS_PER_PAGE

@app.route('/', methods= ['GET', 'POST'])  # index view, default when going to
@app.route('/index', methods= ['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body= form.post.data, timestamp = datetime.utcnow(), author = g.user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        return redirect(url_for('index'))
    
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False).items

    return render_template('index.html',
                           title='Home',
                           form = form,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])

    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', nickname=g.user.nickname))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found')
        return redirect(url_for('index'))

    posts = user.followed_posts().all()

    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/user/<nickname>/portfolio')
@login_required
def portfolio(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found')
        return redirect(url_for('index'))

    return render_template('portfolio.html', 
        user=user,
        portfolios=user.project)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Views for Error Handlers


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 404


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')

        return redirect(url_for('login'))

    user = User.query.filter_by(email=resp.email).first()

    if user is None:
        nickname = resp.nickname

        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)

        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()

    remember_me = False

    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)

    login_user(user, remember=remember_me)

    return redirect(url_for('user', nickname=user.nickname))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User {0} not found.'.format(nickname))
        return redirect(url_for('index'))

    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))

    u = g.user.follow(user)

    if u is None:
        flash('Cannot follow {0}'.format(nickname))
        return redirect(url_for('user', nickname=nickname))
    # user is able to add another user
    db.session.add(u)
    db.session.commit()
    flash("You're following {0}!".format(nickname))
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    # check if user exists
    if user == None:
        flash("User {0} not found.".format(nickname))
        return redirect(url_for('index'))
    # check if user is attempting to unfollow themself
    if user == g.user:
        flash("You can't unfollow yourself!")
        return redirect(url_for('index'))
    # set object u to add to db.session
    u = g.user.unfollow(user)
    # check if user is able to unfollow another user
    if u == None:
        flash("Can't unfollow {0}.".format(nickname))
        return redirect(url_for('user', nickname=nickname))
    # add unfollow and commit to db.session
    db.session.add(u)
    db.session.commit()
    flash("You have stopped following {0}".format(nickname))
    return redirect(url_for('user', nickname=nickname))
