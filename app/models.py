from app import db
from hashlib import md5
import re
from app import app
from datetime import datetime

"""
SDC from the orig tutorial
7/17/2014

Don't forget!
Each time you change the database you must do:
./db_migrate.py

(TODO - explore other migration tools (Alembic for example))
Actually fuck it the built in migrate is fine for now.

9/29/2014
Idears:
admin/non-admin users
anybody can 'follow', they will see access events too (can protect access?)

Notification fun

crunch these out:

list of accesses (failed or valid)

Add sensor stuff (when we have sensors!)

Integrate w/ stormpath

Notifications

Add proper tests!

"""

ROLE_USER = 0
ROLE_ADMIN = 1

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

"""

Qs:
add relationship for access events, too?

"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
 
    first_name = db.Column(db.String(24))
    last_name = db.Column(db.String(50), index = True)
    rfid_access = db.Column(db.Boolean, default = False)
    rfid_tag = db.Column(db.String(20), index = True, unique = True)
    rfid_description = db.Column(db.String(50))           
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
 
    access_events = db.relationship('AccessEvent', backref = 'member', lazy = 'dynamic')
 
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    is_active = db.Column(db.Boolean, default = False)    

    language = db.Column(db.String(5))

    followed = db.relationship('User', 
        secondary = followers, 
        primaryjoin = (followers.c.follower_id == id), 
        secondaryjoin = (followers.c.followed_id == id), 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def is_authenticated(self):
        return True

# wait what?
#    def is_active(self):
#        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

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
        return Post.query.join(followers, (
            followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def sorted_posts(self):
        return Post.query.filter(Post.user_id == self.id).order_by(Post.timestamp.desc())

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

class Post(db.Model):   
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post %r>' % (self.body)
    
"""

Access event. Either was allowed (or not allowed) access

(how best to tie back?)

"""

class AccessEvent(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    rfid_tag = db.Column(db.String(20), index = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_date = db.Column(db.DateTime)
    access_granted = db.Column(db.Boolean, default = False)

    def __init__(self, rfid_tag, access_granted = False):
        self.rfid_tag = rfid_tag
        self.event_date = datetime.utcnow()
        self.access_granted = access_granted
        
    def __repr__(self):
        return 'Tag: %s at %s. Granted: %s' % (self.rfid_tag, self.event_date, self.access_granted)

"""

Web urls of 'Internet Things'

"""

class ServiceURL(db.Model):
    id = db.Column(db.Integer, primary_key = True) # wait. is auto?
    service_description = db.Column(db.String(100))
    service_name = db.Column(db.String(20))
    service_URL = db.Column(db.String(75))

    def __repr__(self):
        return "%s: %s" % (service_name, service_URL)
"""

Sensor event

"""

#class SensorEvent(db.Model):
#    pass

