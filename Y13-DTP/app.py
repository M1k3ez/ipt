from flask import Flask, render_template, request
from models import db, elementcontent
from flask_mail import Mail, Message
from dotenv import load_dotenv
from sqlalchemy import cast, Float
import os
import logging

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipt.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT') or 0)
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
db.init_app(app)

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    try:
        all_elements = elementcontent.query.all()
        logging.debug(f'Total elements in table: {len(all_elements)}')
        for element in all_elements:
            logging.debug(f'Element ID: {element.electron}, Enegativity: {element.enegativity}')
        
        elements = elementcontent.query.filter(
            elementcontent.enegativity != 'N/A',
            cast(elementcontent.enegativity, Float) > 1.5
        ).all()
        
        logging.debug(f'Query returned {len(elements)} elements.')
        for element in elements:
            logging.debug(f'Filtered Element ID: {element.electron}, Enegativity: {element.enegativity}')
        
        if elements:
            return render_template("home.html", elements=elements)
        else:
            return render_template("404.html")
    except Exception as e:
        logging.error(f'Error occurred: {e}')
        return str(e), 500

@app.route("/sendmail")
def send_mail():
    try:
        msg = Message("Hello", recipients=["thule001127@gmail.com"])
        msg.body = "This is a test email sent from a Flask app using Flask-Mail. Anh yeu em"
        mail.send(msg)
        return "Mail sent!"
    except Exception as e:
        logging.error(f'Error occurred while sending mail: {e}')
        return str(e), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
