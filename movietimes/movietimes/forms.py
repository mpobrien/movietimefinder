from wtforms import Form, TextField, PasswordField
from wtforms import validators

class ResetPasswordForm(Form):
    password = PasswordField('Password',
                [validators.Required(),
                 validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class ForgotPasswordForm(Form):
    email = TextField('Email')

class LoginForm(Form):
    email = TextField('Email')
    password = PasswordField('Password')

class RegisterForm(Form):
    email = TextField('Email', validators=[validators.Email(message=u'Invalid email address.')])
    password = PasswordField('Password',
                [validators.Required(),
                 validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')


