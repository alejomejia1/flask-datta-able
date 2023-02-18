# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin, current_user
import sys

# from sqlalchemy import SQLAlchemyError
from sqlalchemy.orm import relationship, column_property, Session
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import aggregated
from sqlalchemy import ForeignKey, select

from re import sub
from decimal import Decimal
import locale

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

from datetime import datetime

class Invoice(db.Model):
    
    __tablename__ = 'invoices'

    id            = db.Column(db.Integer, primary_key=True)
    prefijo       = db.Column(db.String(5))
    nfactura      = db.Column(db.Integer, unique=True)
    client_id     = db.Column(db.Integer, ForeignKey('clients.id'))
    user_id       = db.Column(db.Integer, ForeignKey('users.id'))
    project_id    = db.Column(db.Integer, ForeignKey('projects.id'))
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
    project = relationship('Project', backref='Invoice',
                                primaryjoin='Invoice.project_id == Project.id')
    
    
        
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
    name          = db.Column(db.String(200))
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

    
    def add_new(client):
        print("Guardando nuevo cliente")
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
        new_cli = Client(
            name               = client["name"],
            user_id            = client["user_id"],
            reference          = client["reference"],
            nit                = client["nit"],
            phone              = client["phone"],
            email              = client["email"],
            created            = datetime.now(),
            modified           = datetime.now(),            
        )
        db.session.add(new_cli)
        db.session.commit()
    
    def get_cllients_total():
        qry = Client.query.distinct(Client.name).count()
        if (qry is None):
            qry = 0
        print(qry)
        return qry

    def get_clients():
        qry = Client.query.with_entities(Client.id, Client.name).distinct(Client.name).all()
        return qry

    def get_clients_list():
        qry = Client.query.with_entities(Client.id, Client.reference).distinct(Client.name).all()
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
    user    = relationship('Users', backref='Contact',
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

    def add_new(contact):
        print("Guardando nuevo contacto")
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
        new_con = Contact(
            name               = contact["name"],
            user_id            = contact["user_id"],
            client_id          = contact["client_id"],
            cellphone          = contact["cellphone"],
            email              = contact["email"],
            address            = contact["address"],
            created            = datetime.now(),
            modified           = datetime.now(),            
        )
        db.session.add(new_con)
        db.session.commit()


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


class Project(db.Model):
    
    __tablename__ = 'projects'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(255))
    description   = db.Column(db.Text, nullable=True)
    user_id       = db.Column(db.Integer, ForeignKey('users.id'))
    client_id     = db.Column(db.Integer, ForeignKey('clients.id'))
    start_date    = db.Column(db.Date);
    end_date      = db.Column(db.Date, nullable=True)
    active        = db.Column(db.Boolean)
    created       = db.Column(db.DateTime)
    modified      = db.Column(db.DateTime)
    
    cliente = relationship('Client', backref='Project',
                                primaryjoin='Project.client_id == Client.id')
    user    = relationship('Users', backref='Project',
                                primaryjoin='Project.user_id == Users.id')
    
    ninvoices = column_property(
        select(func.count(Invoice.id)).where(Invoice.project_id == id).scalar_subquery()
    )
    
    total_invoices = column_property(
        select(func.sum(Invoice.valor)).where(Invoice.project_id == id).scalar_subquery()
    )
    
    invoices = relationship('Invoice', 
                            primaryjoin='Invoice.project_id == Project.id', viewonly = True)
    
    def get_projects():
        qry = Project.query.filter(Project.user_id == current_user.id).all()
        return qry