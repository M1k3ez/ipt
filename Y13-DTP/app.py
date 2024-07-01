import os
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
from models import db, ElementContent, Group, Period, Category, Subshell, ElectronCfg
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database configuration
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


def calculate_electron_configuration(atomic_number):
    subshells = db.session.query(Subshell).order_by(Subshell.id).all()
    configuration = []
    electrons_remaining = atomic_number

    for subshell in subshells:
        if electrons_remaining <= 0:
            break
        electrons_in_subshell = min(electrons_remaining, subshell.maxelectrons)
        configuration.append({
            'subshell_id': subshell.id,
            'electrons': electrons_in_subshell,
            'pqn': subshell.id,  # Assuming `pqn` is the primary key or related to subshell.id
            's': electrons_in_subshell if subshell.subshells.startswith('s') else None,
            'p': electrons_in_subshell if subshell.subshells.startswith('p') else None,
            'd': electrons_in_subshell if subshell.subshells.startswith('d') else None,
            'f': electrons_in_subshell if subshell.subshells.startswith('f') else None
        })
        electrons_remaining -= electrons_in_subshell

    return configuration


def calculate_electron_configuration(atomic_number):
    subshells = db.session.query(Subshell).order_by(Subshell.id).all()
    configuration = []
    electrons_remaining = atomic_number

    for subshell in subshells:
        if electrons_remaining <= 0:
            break
        electrons_in_subshell = min(electrons_remaining, subshell.maxelectrons)
        pqn = int(subshell.subshells[0])  # Assuming subshells are in the format "1s", "2p", etc.
        s = electrons_in_subshell if subshell.subshells.endswith('s') else None
        p = electrons_in_subshell if subshell.subshells.endswith('p') else None
        d = electrons_in_subshell if subshell.subshells.endswith('d') else None
        f = electrons_in_subshell if subshell.subshells.endswith('f') else None
        
        configuration.append({
            'pqn': pqn,
            's': s,
            'p': p,
            'd': d,
            'f': f,
            'element_id': atomic_number,
            'subshell_id': subshell.id
        })
        
        electrons_remaining -= electrons_in_subshell

    # Ensure only the final result for each subshell is included
    final_configuration = {}
    for config in configuration:
        subshell_id = config['subshell_id']
        if subshell_id in final_configuration:
            final_configuration[subshell_id]['s'] = (final_configuration[subshell_id]['s'] or 0) + (config['s'] or 0)
            final_configuration[subshell_id]['p'] = (final_configuration[subshell_id]['p'] or 0) + (config['p'] or 0)
            final_configuration[subshell_id]['d'] = (final_configuration[subshell_id]['d'] or 0) + (config['d'] or 0)
            final_configuration[subshell_id]['f'] = (final_configuration[subshell_id]['f'] or 0) + (config['f'] or 0)
        else:
            final_configuration[subshell_id] = config

    config_string = ""
    for config in final_configuration.values():
        if config['s']:
            config_string += f"{config['pqn']}s<sup>{config['s']}</sup> "
        if config['p']:
            config_string += f"{config['pqn']}p<sup>{config['p']}</sup> "
        if config['d']:
            config_string += f"{config['pqn']}d<sup>{config['d']}</sup> "
        if config['f']:
            config_string += f"{config['pqn']}f<sup>{config['f']}</sup> "

    return config_string.strip()


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
        print(f"Error: {e}")
        return render_template('404.html'), 500


@app.route('/<int:electron>', methods=['GET'])
def get_element(electron):
    try:
        element = db.session.query(ElementContent).filter_by(electron=electron).first()
        if element:
            return jsonify({
                "electron": element.electron,
                "name": element.name,
                "symbol": element.symbol,
                "enegativity": element.enegativity,
                "meltingpoint": element.meltingpoint,
                "boilingpoint": element.boilingpoint,
                "details": element.furtherinfo,
                "ydiscover": element.ydiscover,
            })
        else:
            return jsonify({"error": "Element not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
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
        except Exception:
            flash('Failed to send your message. Please try again later.', 'danger')
    return render_template('contact.html', form=form)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/show_configuration/<int:atomic_number>', methods=['GET'])
def show_configuration(atomic_number):
    try:
        element = db.session.query(ElementContent).filter_by(electron=atomic_number).first()
        if element:
            configuration = calculate_electron_configuration(atomic_number)
            return render_template('show_configuration.html', element=element, configuration=configuration)
        else:
            return jsonify({"error": "Element not found"}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
