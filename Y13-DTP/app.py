from flask import Flask, render_template, flash, request
from models import db, elementcontent
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import logging
import smtplib

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipt.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT') or 0)
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize Flask-Mail
mail = Mail(app)

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

db.init_app(app)

@app.route('/')
def home():
    try:
        elements = elementcontent.query.filter(
            elementcontent.enegativity != 'N/A',
            elementcontent.enegativity > '1.5'
        ).all()
        if elements:
            return render_template("home.html", elements=elements)
        else:
            return render_template("404.html")
    except Exception as e:
        return str(e), 500

@app.route("/sendmail")
def send_mail():
    try:
        # Log the current mail configuration
        logging.debug(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
        logging.debug(f"MAIL_PORT: {app.config['MAIL_PORT']}")
        logging.debug(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
        logging.debug(f"MAIL_USE_SSL: {app.config['MAIL_USE_SSL']}")
        logging.debug(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
        logging.debug(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")

        msg = Message("Hello", recipients=["ipttnoreply@gmail.com"])
        msg.body = "This is a test email sent from a Flask app using Flask-Mail."
        
        # SMTP Debugging
        smtp = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        smtp.set_debuglevel(1)
        smtp.ehlo()
        if app.config['MAIL_USE_TLS']:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        smtp.sendmail(app.config['MAIL_DEFAULT_SENDER'], ["ipttnoreply@gmail.com"], msg.as_string())
        smtp.quit()

        mail.send(msg)
        return "Mail sent!"
    except smtplib.SMTPException as e:
        logging.error("SMTP error occurred: ", exc_info=e)
        return str(e), 500
    except Exception as e:
        logging.error("Error sending mail:", exc_info=e)
        return str(e), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
