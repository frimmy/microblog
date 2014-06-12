from app import db
from hashlib import md5

ROLE_USER = 0
ROLE_ADMIN = 1

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('user.id'))
                     )


class User(db.Model):

    """user model"""
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    # relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    # similar to posts, use relationships
    projects = db.relationship('Project', backref='author', lazy='dynamic')

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    # functions of user class for Flask-Login play
    # followed relationship defined below
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin = (followers.c.followed_id == id),
                               backref = db.backref(
                                   'followers', lazy='dynamic'),
                               lazy = 'dynamic')


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def avatar(self, size):
        return ('http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() +
                '?d=mm&s=' + str(size))

    # handle auto-creation of unique nicknames to avoid name collision
    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(
            followers,
            (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id).order_by(
            Post.timestamp.desc())


class Post(db.Model):

    """model for Posts table"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

# TODO: user projects, skills
# TODO: 
class Project(db.Model):
    
    """
    model for Projects table
    has a 1 to many relationship similar to Posts.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    description = db.Column(db.String(140))
    git_hub_link = db.Column(db.String(255))
    demo_link = db.Column(db.String(255))
    
    # relationship to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # best to use a path to the imgs 
    # ex: uploads/my_project_sample.png       
    screen_shot = db.Column(db.String(255))
    
    def __repr__(self):
        return '<Project %r>' % (self.title)

    


# class Skills(db.Model)
#   """
#   model for Skills table
#   has a one-to-many relationship similar to Posts.
#   """
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(30))

