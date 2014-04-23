from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required
from app.models import Users


class LoginForm(Form):
    username = TextField('username', validators=[Required()])
    password = TextField('password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(Form):
    username = TextField('username', validators=[Required()])
    password = TextField('password', validators=[Required()])
    email = TextField('email', validators=[Required()])

    def __init__(self, original_username, original_password, original_email, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_username = original_username
        self.original_password = original_password
        self.original_email = original_email

    def validate(self):
        if not Form.validate(self):
            return False
        if self.username.data == self.original_username:
            return True
        if self.username.data != Users.make_valid_username(self.username.data):
            self.username.errors.append(gettext(
                'This username has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        user = Users.query.filter_by(username=self.username.data).first()
        if self.password.data != Users.make_valid_password(self.password.data):
            self.username.errors.append(gettext(
                'This password has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        password = Users.query.filter_by(password=self.password.data).first()
        if self.email.data != Users.make_valid_email(self.email.data):
            self.username.errors.append(gettext(
                'This email has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        email = Users.query.filter_by(email=self.email.data).first()
        if user != None:
            self.username.errors.append(
                gettext('This username is already in use. Please choose another one.'))
            return False
        return True
