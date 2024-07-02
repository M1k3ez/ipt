import os
from flask import Flask, render_template, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
from models import db, ElementContent, Group, Period, Category, Subshell, ElectronCfg
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
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
# Initialize Flask-Mail
mail = Mail(app)

# Initialize the database with the Flask app
db.init_app(app)


# Define the contact form using Flask-WTF
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


# Function to calculate electron configuration
def calculate_electron_configuration(atomic_number):
    subshells = db.session.query(Subshell).order_by(Subshell.id).all()
    # Query all subshells
    configuration = []  # Initialize configuration list
    electrons_remaining = atomic_number
    # Set remaining electrons to atomic number
    for subshell in subshells:
        if electrons_remaining <= 0:
            break  # Exit loop if no electrons remaining
        electrons_in_subshell = min(electrons_remaining, subshell.maxelectrons)
        # Electrons in current subshell
        pqn = int(subshell.subshells[0])  # Principal quantum number
        subshell_type = subshell.subshells[1]  # Subshell type
        config = {
            'pqn': pqn,
            'subshell_id': subshell.id,
            'element_id': atomic_number,
            subshell_type: electrons_in_subshell
        }
        configuration.append(config)  # Append configuration
        electrons_remaining -= electrons_in_subshell  # Subtract electrons
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


# Function to store electron configuration in the database
def store_electron_configuration(element_id, configuration):
    db.session.query(ElectronCfg).filter_by(element_id=element_id).delete()
    # Delete existing configuration
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
        db.session.add(electron_cfg)  # Add new configuration
    db.session.commit()  # Commit changes


# Function to determine the state of an element at 273 Kelvin (0 celcius)
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
    elements = db.session.query(
        ElementContent.electron,
        ElementContent.name,
        ElementContent.symbol,
        ElementContent.meltingpoint,
        ElementContent.boilingpoint,
        ElementContent.furtherinfo,
        ElementContent.ydiscover,
        Group.id.label('group'),
        Period.pid.label('period'),
        Category.id.label('category_id')
    ).join(Group, ElementContent.electron == Group.ecid)\
     .join(Period, ElementContent.electron == Period.ecid)\
     .join(Category, ElementContent.electron == Category.ecid).all()
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
            "category_id": element.category_id,
            "state": determine_state_at_zero(element)
        }
        for element in elements
    ]
    return render_template("home.html", elements=elements)


# Route to get details of an element by atomic number
@app.route('/<int:electron>', methods=['GET'])
def get_element(electron):
    if electron < 1 or electron > 118:  # Boundary check
        return render_template('404.html'), 404
    element = db.session.query(ElementContent).filter_by(electron=electron).first()
    if not element:
        return jsonify({"error": "Element not found"}), 404
    category = db.session.query(Category).filter_by(ecid=electron).first()
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
        "group": element.group.name if element.group else None,
        "period": element.period.pname if element.period else None,
        "configuration": config_string,
        "category": category.name if category else None,
        "categorydescription": category.description if category else None,
    })


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():  # Check if form is valid
        msg = Message(
            subject=form.subject.data,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=["ipttnoreply@gmail.com"]
        )
        msg.reply_to = form.email.data
        msg.body = f"Name: {form.name.data}\nEmail: {form.email.data}\n\
            Phone: {form.telephone.data}\nMessage: {form.message.data}"
        mail.send(msg)  # Send email
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('404.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
