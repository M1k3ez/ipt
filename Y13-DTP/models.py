from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Group(Base):
    __tablename__ = 'Group'
    id = db.Column(db.Integer, primary_key=True)
    ecid = db.Column(db.Integer, db.ForeignKey('ElementContent.electron'), nullable=False)
    name = db.Column(db.String, nullable=False)

    element_content = db.relationship('ElementContent', back_populates='group')


class ElementContent(Base):
    __tablename__ = 'ElementContent'
    electron = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    symbol = db.Column(db.String, nullable=True)
    enegativity = db.Column(db.Integer, nullable=False)
    meltingpoint = db.Column(db.Integer, nullable=False)
    boilingpoint = db.Column(db.Integer, nullable=False)
    furtherinfo = db.Column(db.String, nullable=False)
    ydiscover = db.Column(db.Integer, nullable=True)
    group = db.relationship('Group', back_populates='element_content', uselist=False)
    period = db.relationship('Period', back_populates='element_content', uselist=False)
    subshells = db.relationship('Subshell', secondary='electroncfg', back_populates='elements')


class Period(Base):
    __tablename__ = 'Period'
    pid = db.Column(db.Integer, primary_key=True)
    ecid = db.Column(db.String, db.ForeignKey('ElementContent.electron'), nullable=False)
    pname = db.Column(db.String, nullable=False)
    element_content = db.relationship('ElementContent', back_populates='period')


class Category(Base):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    ecid = db.Column(db.Integer, nullable=False)


class Subshell(Base):
    __tablename__ = 'Subshell'
    id = db.Column(db.Integer, primary_key=True)
    subshell = db.Column(db.String, nullable=False)
    max_electrons = db.Column(db.Integer, nullable=False)  
    elements = db.relationship('ElementContent', secondary='electroncfg', back_populates='subshells')


class ElectronCfg(Base):
    __tablename__ = 'electroncfg'
    id = db.Column(db.Integer, primary_key=True)
    pqn = db.Column(db.Integer)
    smax = db.Column(db.Integer)
    pmax = db.Column(db.Integer)
    dmax = db.Column(db.Integer)
    fmax = db.Column(db.Integer)
    element_id = db.Column(db.Integer, db.ForeignKey('ElementContent.electron'))
    subshell_id = db.Column(db.Integer, db.ForeignKey('Subshell.id'))
