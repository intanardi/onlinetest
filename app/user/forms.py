from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from ..models import User, Role
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class UserForm(FlaskForm):
  username = StringField('username', validators=[DataRequired()])
  email = StringField('email', validators=[DataRequired(), Email()])
  roles = SelectField('Category', choices = [('1', 'superadmin'), ('2', 'admin'), ('3', 'candidate')])
  password = PasswordField('password', validators=[DataRequired()])
  repassword = PasswordField('retype password', validators=[DataRequired(), EqualTo(password)])
  submit = SubmitField('Save')

class LoginForm(FlaskForm):
  username = StringField('username', validators=[DataRequired()])
  password = PasswordField('password', validators=[DataRequired()])
  submit = SubmitField('Login')
