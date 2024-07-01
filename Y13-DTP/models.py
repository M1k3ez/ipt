from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
pass
db = SQLAlchemy(model_class=Base)

class Subshell(Base):
    __tablename__ = 'subshell'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subshells = db.Column(db.String, nullable=False, unique=True)
    maxelectrons = db.Column(db.Integer, nullable=False)
    
    elements = db.relationship('ElectronCfg', back_populates='subshell')


class ElectronCfg(Base):
    __tablename__ = 'electroncfg'
    id = db.Column(db.Integer, primary_key=True)
    element_id = db.Column(db.Integer, db.ForeignKey('ElementContent.electron'), nullable=False)
    subshell_id = db.Column(db.Integer, db.ForeignKey('subshell.id'), nullable=False)
    pqn = db.Column(db.Integer, nullable=False)
    smax = db.Column(db.Integer, nullable=True)
    pmax = db.Column(db.Integer, nullable=True)
    dmax = db.Column(db.Integer, nullable=True)
    fmax = db.Column(db.Integer, nullable=True)
    
    element = db.relationship('ElementContent', back_populates='subshells')
    subshell = db.relationship('Subshell', back_populates='elements')


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
    subshells = db.relationship('ElectronCfg', back_populates='element')


class Group(Base):
    __tablename__ = 'Group'
    id = db.Column(db.Integer, primary_key=True)
    ecid = db.Column(db.Integer, db.ForeignKey('ElementContent.electron'), nullable=False)
    name = db.Column(db.String, nullable=False)
    element_content = db.relationship('ElementContent', back_populates='group')


class Period(Base):
    __tablename__ = 'Period'
    pid = db.Column(db.Integer, primary_key=True)
    ecid = db.Column(db.Integer, db.ForeignKey('ElementContent.electron'), nullable=False)
    pname = db.Column(db.String, nullable=False)
    element_content = db.relationship('ElementContent', back_populates='period')


class Category(Base):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    ecid = db.Column(db.Integer, db.ForeignKey('ElementContent.electron'), nullable=False)
