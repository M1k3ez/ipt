# importing necessary libraries
from flask import Flask, render_template, request, flash, redirect, jsonify, abort
from flask_cors import CORS
import sqlite3
import re


app = Flask(__name__)
app.secret_key = 'S_KEY'
CORS(app)  # Enable CORS for all routes
# Specifically enable CORS for routes with "/api/*" path
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5000"}})


# Function to handle database queries
def db_query(query, params=None, fetchone=False):
    conn = sqlite3.connect("glifewiki.db")
    cur = conn.cursor()
    # Executing query with parameters if provided
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    # Commit changes if query is for data manipulation (insert/update/delete)
    if query.strip().lower().startswith(('insert', 'update', 'delete')):
        conn.commit()
    # Fetching single result if fetchone is True, otherwise fetching all results
    if fetchone:
        result = cur.fetchone()
    else:
        result = cur.fetchall()
    conn.close()
    return result


# Route for homepage
@app.route("/")
def homepage():
    return render_template('home.html')


# Route to display all rule categories
@app.route("/all_rules_category")
def all_rules_category():
    results = db_query("SELECT id, name FROM category")
    return render_template('all_rules_category.html', results=results)


# Route to display all rules based on category name
@app.route('/all_rules_category/all_rules/<category_name>')
def all_rules(category_name):
    # Check if category name is valid
    if category_name not in ["connection", "gameplay", "behaviour"]:
        abort(404)
    results = db_query(
        "SELECT id, name, date, basicdescription, photo FROM rules WHERE id IN \
        (SELECT rid FROM rulescategory WHERE cid = \
        (SELECT id FROM category WHERE name = ?))", (category_name,))
    return render_template('all_rules.html', results=results, category_name=category_name)


# API route to provide details for a specific rule within a category
@app.route('/api/rules_details/<string:category_name>/<string:rule_name>', methods=['GET'])
def api_rule_details(category_name, rule_name):
    # Check if category name exists in the database
    ctgr = db_query("SELECT name FROM category WHERE name = ?", (category_name,), fetchone=True)
    if ctgr is None:
        return jsonify({"error": "Category not found"}), 404
    results = db_query(
        """SELECT name, content, sanction, recidivism FROM rcontent WHERE id IN \
        (SELECT ctid FROM rulescontent WHERE rid = \
        (SELECT id FROM rules WHERE name = ? AND id IN \
        (SELECT rid FROM rulescategory WHERE cid = \
        (SELECT id FROM category WHERE name = ?))))""", (rule_name, category_name))
    if not results:
        return jsonify({"error": "Rule not found in this category"}), 404
    rule_details = {
        "category": ctgr[0],
        "rule_name": results[0][0],
        "content": results[0][1],
        "sanction": {
            "first_time": results[0][2],
            "second_time": results[0][3]
        }
    }
    return jsonify(rule_details)


# Route to convert in-game coins
@app.route("/converter")
def gcoins():
    gc = request.args.get('gc')
    if gc is None:
        return render_template('converter.html')
    try:
        gc = int(gc)
    except ValueError:
        abort(404)
    if gc % 100 != 0:
        abort(404)
    results = db_query("SELECT ingamemoney FROM converter WHERE gcoins = ?", (gc,), fetchone=True)
    if results:
        ingamemoney = results[0]
        return render_template('converter.html', gc=gc, ingamemoney=ingamemoney)
    return render_template('converter.html')


# Route to display the about page
@app.route("/about")
def about():
    return render_template("about.html")


# Route to display season information
@app.route("/season_info")
def seasoninfo():
    return render_template("seasoninfo.html")


# Route to display all gun categories
@app.route("/all_guns_type")
def all_guns_category():
    results = db_query("SELECT id, name FROM gtype")
    return render_template('all_guns_type.html', results=results)


# Route to display all guns based on type
@app.route('/all_guns_type/<type_name>/all_guns')
def all_guns(type_name):
    # Check if gun type is valid (boundary relevant)
    if type_name not in ["Rifles", "Sniper", "Heavy Weapon", "Shotgun"]:
        abort(404)
    results = db_query(
        "SELECT id, name, description, ammo, rarity, picture FROM ginfo WHERE id IN \
        (SELECT ifid FROM gtypeinfo WHERE gtid = \
        (SELECT id FROM gtype WHERE name = ?))", (type_name,))
    return render_template('all_guns.html', results=results, type_name=type_name)


# Route to display details of a specific gun within a gun type
@app.route('/all_guns_type/<type_name>/all_guns/<gun_name>')
def guns(type_name, gun_name):
    tname = db_query("SELECT name FROM gtype WHERE name =?", (type_name,))
    tname = tname[0][0] if tname and len(tname) > 0 else None
    results = db_query(
        "SELECT name, description, ammo, rarity, picture FROM ginfo WHERE name = ? AND id IN \
        (SELECT ifid FROM gtypeinfo WHERE gtid = \
        (SELECT id FROM gtype WHERE name = ?))", (gun_name, type_name))
    return render_template('guns.html', results=results, type_name=type_name, gun_name=gun_name, tname=tname)


# Route to handle contact form submission and display
@app.route("/contact", methods=['POST', 'GET'])
def contact():
    should_redirect = False
    if request.method == 'POST':
        ingameid = request.form.get('igid')
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Validations for the form inputs
        if len(ingameid) == 0:
            flash('Please input your ingame id', 'flash_error')
        elif len(name) == 0:
            flash('Please input your name', 'flash_error')
        elif len(email) == 0:
            flash('Please input your email', 'flash_error')
        elif not re.match(r"[^@]+@(gmail\.com|yahoo\.com|outlook.com)$", email):
            flash('Please use Yahoo, Outlook or Gmail email domain', 'flash_warning')
        elif len(message) == 0:
            flash('Please input your message', 'flash_warning')
        else:
            # if all validation checks pass, insert the info into the database
            db_query(
                'INSERT INTO formsubmission \
                (ingameid, name, email, message) VALUES \
                (?, ?, ?, ?)', (ingameid, name, email, message))
            flash('Thanks for your submission, we will reply to you ASAP', 'flash_success')
            should_redirect = True
    return render_template('contact.html', should_redirect=should_redirect)


# Route to display all messages received through the contact form
@app.route("/contact/all_message")
def all_message():
    results = db_query("SELECT * FROM formsubmission")
    return render_template('all_message.html', results=results)


# Route to delete a specific message based on ID
@app.route('/delete_message/<int:id>', methods=['POST'])
def delete_message(id):
    if request.method != 'POST':
        abort(405)
    db_query('DELETE FROM formsubmission WHERE id = ?', (id,))
    flash('Message has already been deleted', 'flash-delete-message')
    return redirect('/contact/all_message')


# Route to display a specific message based on ID
@app.route('/contact/message/<int:id>')
def message(id):
    message = db_query('SELECT * FROM formsubmission WHERE id =?', (id,), fetchone=True)
    if message is None:
        abort(404)
    # Update message status to read
    if message[5] == 0:
        db_query('UPDATE formsubmission SET status = 1 WHERE id = ?', (id,))
    return render_template('message.html', message=message)


if __name__ == '__main__':
    app.run(debug=True)
