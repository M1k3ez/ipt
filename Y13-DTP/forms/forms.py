# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError

def email_domain_check(form, field):
    allowed_domains = ["gmail.com", "yahoo.com", "outlook.com"]
    domain = field.data.split('@')[-1]
    if domain not in allowed_domains:
        raise ValidationError("Please use gmail.com, yahoo.com, or outlook.com email domain.")

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
        Regexp('^[0-9]*$', message="Phone numbers must be numers")
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
