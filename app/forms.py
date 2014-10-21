from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length
from models import User

class PostForm(Form):
    post = TextField('post', validators = [Required()])

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False) 
    
class EditForm(Form):
    nickname = TextField('nickname', validators = [Required()])
    
    first_name = TextField('first_name', validators = [], default = "")
    last_name = TextField('last_name', validators = [], default = "")

    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])

    rfid_access = BooleanField('rfid_access')
    rfid_tag = TextField('rfid_tag', validators = [Length(min = 5, max = 10)])
    is_active = BooleanField('is_active')

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append('This nickname has invalid characters. Please use letters, numbers, dots and underscores only.')
            return False
        user = User.query.filter_by(nickname = self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True