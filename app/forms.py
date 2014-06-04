from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length, url
from wtforms.fields.html5 import URLField
from app.models import User


class LoginForm(Form):

    """This is the text string for the form"""
    openid = TextField('openid', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(Form):
    nickname = TextField('nickname', validators=[Required()])
    about_me = TextAreaField(
        'about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append(
                'This nickname is already in use. Please choose another one.')
            return False
        return True


class PostForm(Form):
    post = TextField('post', validators=[Required()])


class ProjectsForm(Form):

    """
    This is the docstring for Projects. 
    Users can add as many projects as they can by providing
    a title, a description, and links to the project (url/github).
    TODO: add ability to store image of project
    """
    title = TextField('title', validators=[Required()])
    description = TextAreaField(
        'description', validators=[Length(min=0, max=140), Required()])
    git_hub_link = URLField('git_hub_link', validators=[url(), Required()])
    demo_link = URLField('demo_link', validators=[url(), Required()])
    # Todo: add validator that checks for broken links
    
