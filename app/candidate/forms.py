from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email


class CandidateForm(FlaskForm):
  username = StringField('username', validators=[DataRequired()])
  email = StringField('email', validators=[DataRequired(), Email()])
  phone = StringField('phone', validators=[DataRequired()])
  address = StringField('address', validators=[DataRequired()])
  fullname = StringField('fullname', validators=[DataRequired()])
  password = PasswordField('password', validators=[DataRequired()])
  repassword = PasswordField('retype password', validators=[DataRequired()])
  submit = SubmitField('SAVE')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')