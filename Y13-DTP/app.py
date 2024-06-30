import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
from models import db, ElementContent, Group, Period, Category
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Configure logging
handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

db_path = os.path.join(os.path.dirname(__file__), 'ipt.sqlite3')
app.config.update(
    SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='your-secret-key',
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT') or 0),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS') == 'True',
    MAIL_USE_SSL=os.getenv('MAIL_USE_SSL') == 'True',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER'),
    MAIL_DEBUG=False
)

mail = Mail(app)
db.init_app(app)

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Length(max=24),
        Regexp('^[a-zA-Z ]*$', message="Name must contain only letters and spaces.")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=45)
    ])
    telephone = StringField('Telephone', validators=[
        DataRequired(),
        Length(max=15),
        Regexp('^[0-9]*$', message="Phone number must contain only numbers.")
    ])
    subject = SelectField('Subject', choices=[
        ('Advice', "Advice"),
        ('Questions', "Questions"),
        ('Proposal', "Proposal")
    ], validators=[DataRequired()])
    message = TextAreaField('Message', validators=[
        DataRequired(),
        Length(max=600)
    ])
    submit = SubmitField('Send Message')

@app.route('/')
def home():
    try:
        elements = db.session.query(
            ElementContent.electron,
            ElementContent.name,
            ElementContent.symbol,
            ElementContent.meltingpoint,
            ElementContent.boilingpoint,
            ElementContent.furtherinfo,
            ElementContent.ydiscover,
            Group.id.label('group'),
            Period.pid.label('period')
        ).join(Group, ElementContent.electron == Group.ecid)\
         .join(Period, ElementContent.electron == Period.ecid).all()
        elements = [
            {
                "electron": element.electron,
                "name": element.name,
                "symbol": element.symbol,
                "meltingpoint": element.meltingpoint,
                "boilingpoint": element.boilingpoint,
                "furtherinfo": element.furtherinfo,
                "ydiscover": element.ydiscover,
                "group": element.group,
                "period": element.period
            }
            for element in elements
        ]
        return render_template("home.html", elements=elements)
    except Exception as e:
        app.logger.error('Error loading home page', exc_info=e)
        return render_template('404.html'), 500

@app.route('/element/<int:electron>', methods=['GET'])
def get_element(electron):
    app.logger.info(f'Received request for element with electron number: {electron}')
    try:
        element = ElementContent.query.filter_by(electron=electron).first()
        if element:
            app.logger.info(f'Element found: {element}')
            return jsonify({
                "electron": element.electron,
                "name": element.name,
                "symbol": element.symbol,
                "enegativity": element.enegativity,
                "meltingpoint": element.meltingpoint,
                "boilingpoint": element.boilingpoint,
                "details": element.furtherinfo,
                "ydiscover": element.ydiscover
            })
        else:
            app.logger.warning(f'Element with electron number {electron} not found')
            return jsonify({"error": "Element not found"}), 404
    except Exception as e:
        app.logger.error(f'Error fetching details for element {electron}', exc_info=e)
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            msg = Message(
                subject=form.subject.data,
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=["ipttnoreply@gmail.com"]
            )
            msg.reply_to = form.email.data
            msg.body = f"Name: {form.name.data}\nEmail: {form.email.data}\nPhone: {form.telephone.data}\nMessage: {form.message.data}"
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            app.logger.error('Error sending email', exc_info=e)
            flash('Failed to send your message. Please try again later.', 'danger')
    return render_template('contact.html', form=form)

@app.route('/404')
def handlingerror():
    return render_template('404.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
