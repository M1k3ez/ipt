from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, elementcontent

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipt.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/')
def home():
    try:
        elements = elementcontent.query.filter( elementcontent.enegativity != 'N/A',\
                                                elementcontent.enegativity > '1.5').all()
        if not elements:
            return "No elements found."
        element_list = [f"{e.electron} {e.name} ({e.symbol}):  eNeg: {e.enegativity}, " for e in elements]
        return '<br>'.join(element_list)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
