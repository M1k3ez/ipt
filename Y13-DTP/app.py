from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from models import db, elementcontent
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from dotenv import load_dotenv
from sqlalchemy import cast, Float
import os

load_dotenv()

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), 'ipt.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Needed for CSRF protection in forms
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT') or 0)
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
db.init_app(app)


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Telephone', validators=[DataRequired(), Length(min=6, max=20)])
    subject = SelectField('Subject', choices=[
        ('start_project', "Advice"),
        ('ask_question', "Questions"),
        ('make_proposal', "Proposal")],
        validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')


@app.route('/')
def home():
    elements = elementcontent.query.filter(
        elementcontent.enegativity != 'N/A',
        cast(elementcontent.enegativity, Float) > 1.5
    ).all()
    return render_template("home.html", elements=elements) if elements else render_template("404.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            msg = Message(form.subject.data,
                          sender=app.config['MAIL_DEFAULT_SENDER'],
                          recipients=["ipttnoreply@gmail.com"])
            msg.add_header('Reply-To', form.email.data)
            msg.body = f"Name: {form.name.data}\nEmail: {form.email.data}\nPhone: {form.telephone.data}\nMessage: {form.message.data}"
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'Failed to send message: {str(e)}', 'error')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
