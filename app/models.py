from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
	"""user model"""
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(120), index = True, unique = True)
	role = db.Column(db.Integer, default = ROLE_USER)
	
	# relationships
	posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')

	# functions of user class for Flask-Login play
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def __repr__(self):
		return '<User %r>'% (self.nickname)

class Post(db.Model):
	"model for Posts table"
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	# relationships
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


	def __repr__(self):
		return '<Post %r>' % (self.body)