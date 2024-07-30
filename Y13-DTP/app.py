import os
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_mail import Mail, Message
from models import db, ElementContent, Group, Period, Category
from config import Config
from forms import ContactForm
from functions import calculate_electron_configuration, determine_state_at_zero, store_electron_configuration

# Initialize Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(Config)

# Initialize Flask-Mail
mail = Mail(app)

# Initialize the database with the Flask app
db.init_app(app)

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
            "state": determine_state_at_zero(element, Config.NORM_TEMP)
        }
        for element in elements
    ]
    return render_template("home.html", elements=elements, config=Config)


@app.route('/<int:electron>', methods=['GET'])
def get_element(electron):
    element = db.session.query(ElementContent).filter_by(electron=electron).first_or_404()
    category = db.session.query(Category).filter_by(ecid=electron).first_or_404()
    configuration, config_string = calculate_electron_configuration(electron)
    store_electron_configuration(element.electron, configuration)
    return jsonify({
        "electron": element.electron,
        "name": element.name,
        "symbol": element.symbol,
        "atomicmass": element.atomicmass,
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
    if request.method == 'POST':
        if form.validate_on_submit():
            msg = Message(
                subject=form.subject.data,
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=["ipttnoreply@gmail.com"]
            )
            msg.reply_to = form.email.data
            msg.body = f"Name: {form.name.data}\nEmail: {form.email.data}\nPhone: {form.telephone.data}\nMessage: {form.message.data}"
            mail.send(msg)
            if request.is_json:
                return jsonify({'message': 'Your message has been sent successfully!', 'category': 'success'})
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        else:
            if request.is_json:
                errors = [{'field': field, 'message': error} for field, errors in form.errors.items() for error in errors]
                return jsonify({'errors': errors, 'category': 'danger'})
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return render_template('contact.html', form=form, config=Config)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', config=Config)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', config=Config), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('404.html', config=Config), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
