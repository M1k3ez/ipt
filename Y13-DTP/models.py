from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class elementcontent(db.Model):
    __tablename__ = 'elementcontent'
    electron = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    symbol = db.Column(db.String(50), nullable=False, unique=True)
    enegativity = db.Column(db.String(50), nullable=False)
    meltingpoint = db.Column(db.String(50), nullable=False)
    boilingpoint = db.Column(db.String(50), nullable=False)
    furtherinfo = db.Column(db.String(50), nullable=False)
    ydiscover = db.Column(db.String(50), nullable=False)
