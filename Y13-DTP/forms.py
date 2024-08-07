from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
import re

def email_domain_check(form, field):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$', field.data):
        raise ValidationError("Invalid email format.")
    domain = field.data.split('@')[-1]
    allowed_domains = ["gmail.com", "yahoo.com", "outlook.com"]
    if not (domain in allowed_domains or ".edu" in domain or '.uni' in domain or '.school' in domain):
        raise ValidationError("Please use school/edu/uni or a gmail.com, yahoo.com, outlook.com email.")

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(), Length(max=24),
        Regexp('^[a-zA-Z ]*$', message="Please reinput your names with letters only.")
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email(), Length(max=45), email_domain_check
    ])
    telephone = StringField('Telephone', validators=[
        DataRequired(), Length(max=15),
        Regexp('^[0-9]*$', message="Phone numbers must be numbers.")
    ])
    subject = SelectField('Subject', choices=[
        ('Advice', "Advice"),
        ('Questions', "Questions"),
        ('Proposal', "Proposal")
    ], validators=[DataRequired()])
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(max=600)
    ])
    submit = SubmitField('Send Message')
