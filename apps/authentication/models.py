# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
import sys

# from sqlalchemy import SQLAlchemyError
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import ForeignKey

from re import sub
from decimal import Decimal
import locale

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
    rut           = db.Column(db.String(20), nullable=True)

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
    client_id     = db.Column(db.Integer, ForeignKey('clients.id'))
    user_id       = db.Column(db.Integer, ForeignKey('users.id'))
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
    
    cliente = relationship('Client', backref='Invoice',
                                primaryjoin='Invoice.client_id == Client.id')
    user = relationship('Users', backref='Invoice',
                                primaryjoin='Invoice.user_id == Users.id')
    
    def __init__(
        self, 
        prefijo=None, 
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
        self.prefijo = prefijo
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
        now = datetime.now().strftime('%Y-%m-%d')
        qry = Invoice.query.with_entities(func.sum(Invoice.valor).label("daily_sales")).filter(Invoice.fecha_factura == now, Invoice.anulada == False ).first()[0]
        if (qry is None):
            qry = 0
        print(qry)
        return qry
    
    def get_monthly_total():
        now = datetime.now()
        first_of_month = now.replace(day=1).strftime('%Y-%m-%d')
        qry = Invoice.query.with_entities(func.sum(Invoice.valor).label("monthly_sales")).filter(Invoice.fecha_factura >= first_of_month, Invoice.anulada == False ).first()[0]
        if (qry is None):
            qry = 0
        print(qry)
        return qry

    def get_yearly_total():
        now = datetime.now()
        first_of_month = now.replace(day=1)
        first_of_year = first_of_month.replace(month=1)
        qry = Invoice.query.with_entities(func.sum(Invoice.valor).label("yearly_sales")).filter(Invoice.fecha_factura >= first_of_year , Invoice.anulada == False).first()[0]
        if (qry is None):
            qry = 0
        print(qry)
        return qry

    def invoices_this_year():
        now = datetime.now()
        first_of_month = now.replace(day=1)
        first_of_year = first_of_month.replace(month=1)
        qry = Invoice.query.distinct(Invoice.id).filter(Invoice.created >= first_of_year).count()
        if (qry is None):
            qry = 0
        print(qry)
        return qry

    def clients_this_year():
        now = datetime.now()
        first_of_month = now.replace(day=1)
        first_of_year = first_of_month.replace(month=1)
        qry = Invoice.query.distinct(Invoice.client_id).filter(Invoice.created >= first_of_year).count()
        if (qry is None):
            qry = 0
        print(qry)
        return qry

    def get_last_ten():
        invoices = Invoice.query.order_by(Invoice.id.desc()).limit(10).all()
        return invoices
    
    def get_last_n(n):
        invoices = Invoice.query.order_by(Invoice.id.desc()).limit(n).all()
        return invoices
    
    def get_last_invoice():
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).limit(1).first()
        last_invoice_index = last_invoice.nfactura
        return last_invoice_index
    
    def add_new(invoice):
        print("Guardando nueva invoice")
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
        new_inv = Invoice(
            prefijo            = invoice["prefijo"],
            nfactura           = invoice["nfactura"],
            client_id          = invoice["client_id"],
            fecha_factura      = invoice["fecha_factura"],
            fecha_vencimiento  = invoice["fecha_vencimiento"],
            fecha_proximo_pago = invoice["fecha_proximo_pago"],
            observaciones      = invoice["observaciones"],
            concept            = invoice["concept"],
            anulada            = invoice["anulada"],
            user_id            = invoice["user_id"],
            status_id          = invoice["status_id"],
            created            = datetime.now(),
            modified           = datetime.now(),
            descuento          = 0,
            valor              = locale.atof(invoice["valor"].strip("$"))
            
        )
        db.session.add(new_inv)
        db.session.commit()
    
    def update(invoice):
        print("Actualizando invoice")
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
        db.session.commit()
        

class Client(db.Model):
    
    __tablename__ = 'clients'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(5))
    user_id       = db.Column(db.Integer)
    reference     = db.Column(db.String(200))
    nit           = db.Column(db.String(20))
    phone         = db.Column(db.String(15))
    email         = db.Column(db.String(200))
    active        = db.Column(db.Boolean)
    created       = db.Column(db.DateTime)
    modified      = db.Column(db.DateTime)
    
    
    def __init__(
        self, prefijo=None, 
        name=None, 
        user_id=None, 
        reference=None,
        nit=None, 
        phone=None,
        email=None, 
        active=None, 
        created=None,
        modified=None):
        self.name = name
        self.user_id = user_id
        self.reference = reference
        self.nit = nit
        self.phone = phone
        self.email = email
        self.active = active
        self.created = created
        self.modified = modified

    
    
    def get_cllients_total():
        qry = Client.query.distinct(Client.name).count()
        if (qry is None):
            qry = 0
        print(qry)
        return qry

    def get_clients():
        qry = Client.query.with_entities(Client.id, Client.name).distinct(Client.name).all()
        return qry
    
class Contact(db.Model):
    
    __tablename__ = 'contacts'

    id            = db.Column(db.Integer, primary_key=True)
    client_id     = db.Column(db.Integer, ForeignKey('clients.id'))
    user_id       = db.Column(db.Integer, ForeignKey('users.id'))
    name          = db.Column(db.String(5))
    cellphone     = db.Column(db.String(20))
    address       = db.Column(db.String(200))
    email         = db.Column(db.String(100))
    created       = db.Column(db.DateTime)
    modified      = db.Column(db.DateTime)
    
    cliente = relationship('Client', backref='Contact',
                                primaryjoin='Contact.client_id == Client.id')
    usuario = relationship('Users', backref='Contact',
                                primaryjoin='Contact.user_id == Users.id')
    
    def __init__(
        self, prefijo=None, 
        client_id=None, 
        user_id=None, 
        name=None,
        cellphone=None,
        address=None,
        email=None, 
        created=None,
        modified=None):
        self.name = name
        self.user_id = user_id
        self.client_id = client_id
        self.cellphone = cellphone
        self.address = address
        self.email = email
        self.created = created
        self.modified = modified

    def get_contacts_list():
        qry = Contact.query.with_entities(Contact.id, Contact.name).distinct(Contact.name).all()
        return qry
    
    def get_contacts():
        qry = Contact.query.all()
        return qry


class Status(db.Model):
    
    __tablename__ = 'statuses'

    id            = db.Column(db.Integer, primary_key=True)
    status        = db.Column(db.String(20))
    
    def __init__(
        self, 
        status=None):
        self.status = status
    
    def get_statuses():
        qry = Status.query.all()
        return qry
