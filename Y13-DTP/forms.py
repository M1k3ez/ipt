from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError
import re


def email_domain_check(form, field):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$', field.data):
        raise ValidationError("Invalid email format.")
    domain = field.data.split('@')[-1]
    allowed_domains = ["gmail.com", "yahoo.com", "outlook.com"]
    if not (domain in allowed_domains or ".edu" in domain or '.uni' in domain or '.school' in domain):
        raise ValidationError("Please use school/edu/uni or a gmail.com, yahoo.com, outlook.com email.")


def validate_name(form, field):
    if not field.data.replace(' ', '').isalpha():
        raise ValidationError("Name must contain only letters and spaces.")
    if len(field.data) < 2:
        raise ValidationError("Name must be at least 2 characters long.")
    if any(char.isdigit() for char in field.data):
        raise ValidationError("Name cannot contain numbers.")


def validate_telephone(form, field):
    if not field.data.isdigit():
        raise ValidationError("Phone number must contain only digits.")
    try:
        int(field.data)
    except ValueError:
        raise ValidationError("Phone number must be a valid integer.")


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message="Name is required."),
        Length(min=2, max=24, message="Name must be between 2 and 24 characters long."),
        validate_name
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required."),
        Email(message="Invalid email format."),
        Length(max=45, message="Email must not exceed 45 characters."),
        email_domain_check
    ])
    telephone = StringField('Telephone', validators=[
        DataRequired(message="Telephone number is required."),
        Length(max=15, message="Telephone number must not exceed 15 digits."),
        validate_telephone
    ])
    subject = SelectField('Subject', choices=[
        ('Advice', "Advice"),
        ('Questions', "Questions"),
        ('Proposal', "Proposal")
    ], validators=[DataRequired(message="Please select a subject.")])
    message = TextAreaField('Message', validators=[
        DataRequired(message="Message is required."),
        Length(max=600, message="Message must not exceed 600 characters.")
    ])
    submit = SubmitField('Send Message')