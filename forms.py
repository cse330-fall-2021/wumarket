from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, DecimalField, EmailField, SelectField
# from wtforms.fields.html5 import , EmailField
from wtforms.validators import DataRequired, Email



class LoginForm(FlaskForm):
	email = EmailField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])
	submit = SubmitField()

class SignUpForm(FlaskForm):
	firstName = StringField(validators=[DataRequired()], label='firstName')
	lastName = StringField(validators=[DataRequired()], label='lastName')
	password = PasswordField(validators=[DataRequired()])
	email = EmailField(validators=[DataRequired()])
	submit = SubmitField()

class NewProductForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    price = DecimalField(validators=[DataRequired()])
    image_link = StringField(validators=[DataRequired()])
    description = TextAreaField(validators=[DataRequired()])
    submit = SubmitField(label="Add Project")
    
class ValidateForm(FlaskForm):
		email = EmailField(validators=[DataRequired()])
		token = StringField(validators=[DataRequired()])
		submit = SubmitField(label="Validate")

class editProductForm(FlaskForm):
		title = StringField(validators=[DataRequired()])
		price = DecimalField(validators=[DataRequired()])
		image_link = StringField(validators=[DataRequired()])
		description = TextAreaField(validators=[DataRequired()])
		sold = SelectField(choices=[('True', 'Yes'), ('False', 'No')], validators=[DataRequired()])
		submit = SubmitField(label="Update")  
class editProfileForm(FlaskForm):
		firstName = StringField(validators=[DataRequired()])
		lastName = StringField(validators=[DataRequired()])
		img_link = StringField(validators=[DataRequired()])
		bio = TextAreaField(validators=[DataRequired()])
		title = StringField(validators=[DataRequired()])
		submit = SubmitField(label="Update")