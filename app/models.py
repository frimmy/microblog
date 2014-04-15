from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
	"""user model"""
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(120), index = True, unique = True)
	role = db.Column(db.Integer, default = ROLE_USER) 

	def __repr__(self):
		return '<User {}>'.format(self.nickname)