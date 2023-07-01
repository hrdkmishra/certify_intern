from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length


class SignupForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name")
    password = PasswordField(
        "Password", validators=[InputRequired(), DataRequired(), Length(min=8, max=30)]
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ProfileEditForm(FlaskForm):
    company_name = StringField("Company Name", validators=[DataRequired()])
    company_address = StringField("Company Address", validators=[DataRequired()])
    company_city = StringField("Company City", validators=[DataRequired()])
    company_state = StringField("Company State", validators=[DataRequired()])
    company_zipcode = StringField("Company Zip", validators=[DataRequired()])
    company_phone = StringField("Company Phone", validators=[DataRequired()])
    company_email = StringField("Company Email", validators=[DataRequired()])
    company_website = StringField("Company Website", validators=[DataRequired()])

    submit = SubmitField("Update Profile")


class InternForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    designation = StringField("Designation", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    submit = SubmitField("Add Intern")
