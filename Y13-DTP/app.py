from flask import Flask, render_template, flash, request
from models import db, elementcontent
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

app = Flask(__name__)
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipt.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
db.init_app(app)


@app.route('/')
def home():
    try:
        elements = elementcontent.query.filter(
            elementcontent.enegativity != 'N/A',
            elementcontent.enegativity > '1.5'
        ).all()
        print(elements)
        if elements:
            return render_template("home.html", elements=elements)
        else:
            return render_template("404.html")
    except Exception as e:
        return str(e), 500


@app.route("/send-mail/")
def send_mail():
    msg = Message("Hello", recipients=["ipttnoreply@gmail.com"])
    msg.body = "This is a test email sent from a Flask app using Flask-Mail."
    mail.send(msg)
    return "Mail sent!"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
