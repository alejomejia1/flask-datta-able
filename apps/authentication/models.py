# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

# from sqlalchemy import SQLAlchemyError
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

from datetime import datetime

class Users(db.Model, UserMixin):

    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(64), unique=True)
    password      = db.Column(db.String(255))
    name          = db.Column(db.String(50), nullable=True)
    group_id      = db.Column(db.Integer, nullable=True)
    role_id       = db.Column(db.Integer, nullable=True)

    # oauth_github  = db.Column(db.String(100), nullable=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

    @classmethod
    def find_by_email(cls, email: str) -> "Users":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username: str) -> "Users":
        return cls.query.filter_by(username=username).first()
    
    
    @classmethod
    def find_by_id(cls, _id: int) -> "Users":
        return cls.query.filter_by(id=_id).first()
   
    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
          
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
    
    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(Users)


class Invoice(db.Model):
    
    __tablename__ = 'invoices'

    id            = db.Column(db.Integer, primary_key=True)
    prefijo       = db.Column(db.String(5))
    nfactura      = db.Column(db.Integer, unique=True)
    client_id     = db.Column(db.Integer)
    user_id       = db.Column(db.Integer)
    fecha_factura = db.Column(db.DateTime)
    fecha_vencimiento = db.Column(db.DateTime)
    fecha_proximo_pago = db.Column(db.DateTime)
    valor         = db.Column(db.Float)
    descuento     = db.Column(db.Float)
    observaciones = db.Column(db.Text)
    anulada       = db.Column(db.Boolean)
    created       = db.Column(db.DateTime)
    modified      = db.Column(db.DateTime)
    status_id     = db.Column(db.Integer)
    concept       = db.Column(db.Text)
    
    
    def __init__(
        self, prefijo=None, 
        nfactura=None, 
        client_id=None, 
        user_id=None,
        fecha_factura=None, 
        fecha_vencimiento=None,
        fecha_proximo_pago=None, 
        valor=None, 
        descuento=None,
        observaciones=None,
        anulada=None,
        created=None,
        modified=None,
        status_id=None,
        concept=None):
        self.nfactura = nfactura
        self.client_id = client_id
        self.user_id = user_id
        self.fecha_factura = fecha_factura
        self.fecha_vencimiento = fecha_vencimiento
        self.fecha_proximo_pago = fecha_proximo_pago
        self.valor = valor
        self.descuento = descuento
        self.observaciones = observaciones
        self.anulada = anulada
        self.created = created
        self.modified = modified
        self.status_id = status_id
        self.concept = concept
    
    
    def get_daily_total():
        now = datetime.now()
        qry = Invoice.query.with_entities(func.sum(Invoice.valor).label("daily_sales")).filter(Invoice.fecha_factura == now )
        return qry
    
    def get_monthly_total():
        now = datetime.today()
        first_of_month = now.replace(day=1)
        qry = Invoice.query.with_entities(func.sum(Invoice.valor).label("monthly_sales")).filter(Invoice.fecha_factura >= first_of_month ).first()[0]
        print(qry)
        return qry
