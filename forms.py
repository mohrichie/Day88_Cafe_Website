from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField


# Create a Registration Form
class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    login = SubmitField("Login")


class AddCafeForm(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    map_url = StringField("Location URL", validators=[DataRequired(), URL()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    location = StringField("City", validators=[DataRequired()])
    seats = StringField("Number Of Seats", validators=[DataRequired()])
    has_toilet = SelectField('Select 1 If Venue Has Toilet', choices=['0', '1'])
    has_wifi = SelectField('Select 1 If Venue Has WiFi', choices=['0', '1'])
    has_sockets = SelectField('Select 1 If Venue Has Sockets', choices=['0', '1'])
    can_take_calls = SelectField('Select 1 If Someone Can Take Calls', choices=['0', '1'])
    coffee_price = StringField("Coffee Price in £", validators=[DataRequired()])
    submit = SubmitField("ADD VENUE")
