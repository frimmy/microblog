from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required

class LoginForm(Form):
	"""This is the text string for the form"""
	openid = TextField('openid', validators = [Required()])
	remember_me  = BooleanField('remember_me', default = False)

	