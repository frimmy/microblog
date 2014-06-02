import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
	dict(name='Google', url='https://www.google.com/accounts/o8/id'),
	dict(name='Yahoo', url='https://me.yahoo.com'),
	dict(name='AOL', url='http://openid.aol.com/<username>'),
	dict(name='Flickr', url='http://www.flickr.com/<username>'),
	dict(name='MyOpenID', url='https://www.myopenid.com')
]

POSTS_PER_PAGE = 3

# mail server settings
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'adrian.frimpong@gmail.com'
MAIL_PASSWORD = 'Frimmy11!'


# administrator list
ADMINS = ['adrian.frimpong@gmail.com']