from flask import Flask, render_template, request
from models import db, elementcontent
from flask_mail import Mail, Message
from dotenv import load_dotenv
from sqlalchemy import cast, Float
import os

load_dotenv()

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), 'ipt.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
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

@app.route('/')
def home():
    elements = elementcontent.query.filter(
        elementcontent.enegativity != 'N/A',
        cast(elementcontent.enegativity, Float) > 1.5
    ).all()
    return render_template("home.html", elements=elements) if elements else render_template("404.html")

@app.route("/sendmail")
def send_mail():
    msg = Message("Hello", recipients=["ipttnoreply@gmail.com"])
    msg.body = "This is a test email sent from a Flask app using Flask-Mail. Anh yeu em"
    mail.send(msg)
    return "Mail sent!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
