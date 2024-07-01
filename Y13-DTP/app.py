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
        pqn = int(subshell.subshells[0])
        subshell_type = subshell.subshells[1]
        config = {
            'pqn': pqn,
            'subshell_id': subshell.id,
            'element_id': atomic_number,
            subshell_type: electrons_in_subshell
        }
        configuration.append(config)
        electrons_remaining -= electrons_in_subshell
    final_configuration = {}
    for config in configuration:
        subshell_id = config['subshell_id']
        if subshell_id in final_configuration:
            for key in ['s', 'p', 'd', 'f']:
                if key in config:
                    if key in final_configuration[subshell_id]:
                        final_configuration[subshell_id][key] += config[key]
                    else:
                        final_configuration[subshell_id][key] = config[key]
        else:
            final_configuration[subshell_id] = config
    config_string = ""
    for config in final_configuration.values():
        for subshell in ['s', 'p', 'd', 'f']:
            if subshell in config and config[subshell] > 0:
                config_string += f"{config['pqn']}{subshell}<sup>{config[subshell]}</sup> "

    return final_configuration, config_string.strip()


def store_electron_configuration(element_id, configuration):
    db.session.query(ElectronCfg).filter_by(element_id=element_id).delete()
    for subshell_id, config in configuration.items():
        electron_cfg = ElectronCfg(
            element_id=element_id,
            subshell_id=config['subshell_id'],
            pqn=config['pqn'],
            s=config.get('s', None),
            p=config.get('p', None),
            d=config.get('d', None),
            f=config.get('f', None)
        )
        db.session.add(electron_cfg)
    db.session.commit()


def determine_state_at_zero(element):
    try:
        meltingpoint = int(element.meltingpoint) if element.meltingpoint != 'N/A' else None
        boilingpoint = int(element.boilingpoint) if element.boilingpoint != 'N/A' else None
    except ValueError:
        return "unknown"
    if meltingpoint is None:
        return "unknown"
    elif boilingpoint is None:
        return "solid" if meltingpoint > 273 else "liquid"
    elif meltingpoint > 273:
        return "solid"
    elif meltingpoint <= 273 and boilingpoint > 273:
        return "liquid"
    else:
        return "gas"



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
                "period": element.period,
                "state": determine_state_at_zero(element)
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
        category = db.session.query(Category).filter_by(ecid=electron).first()
        if element:
            configuration, config_string = calculate_electron_configuration(electron)
            store_electron_configuration(element.electron, configuration)
            return jsonify({
                "electron": element.electron,
                "name": element.name,
                "symbol": element.symbol,
                "enegativity": element.enegativity,
                "meltingpoint": element.meltingpoint,
                "boilingpoint": element.boilingpoint,
                "details": element.furtherinfo,
                "ydiscover": element.ydiscover,
                "configuration": config_string,
                "category": category.name if category else None,
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
