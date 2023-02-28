from flask import jsonify
from flask_rbac import RoleMixin, UserMixin, RBAC as rbac


from sqlalchemy import Table, Column, Integer, String, Text,  Date, DateTime, Boolean, SmallInteger, BigInteger, ForeignKey, and_, or_, distinct, select, func, UniqueConstraint
from sqlalchemy.orm import relationship, relation, column_property, class_mapper
from sqlalchemy.sql.expression import collate
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.sqltypes import Float
from sqlalchemy_filters import apply_filters
from sqlalchemy.ext.hybrid import hybrid_property

from apps import db
from dataclasses import dataclass
import hashlib

from faker import Faker as fk
import uuid
import random

from datetime import datetime, timedelta
from apps.authentication.models import Users

import random


import gc

import json

from werkzeug.security import generate_password_hash, check_password_hash

from unidecode import unidecode


def unaccent_ln(context):
    return unidecode(context.current_parameters['last_name'])

def unaccent_fn(context):
    return unidecode(context.current_parameters['first_name'])
class Serializer(object):
    
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
    
@dataclass
class User(db.Model, UserMixin):
    """Clase para manejar los usuarios del panel de administracion 

    Args:
        id ([int]): [Llave principal auto incremental] 
        password ([str]): [Password encriptado del usuario]

    Returns:
        [type]: [description]
    """
    __tablename__ = 'user'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    ssno = Column(String(13))
    docType_id = Column(String(2), ForeignKey('Acceso.docType.id'))
    numero_doc = Column(String(20))
    password = Column(String(100)) 
    nombre = Column(String(100))
    email = Column(String(100))
    token = Column(String(100))
    
    UniqueConstraint('username')    

    # roles = relationship('Role', secondary =user_roles,  back_populates='users')
    # roles = db.relationship(
    #     'Role',
    #     secondary=users_roles,
    #     backref=db.backref('roles', lazy='dynamic')
    # )

    def __init__(self, id=None, password=None, nombre=None, email=None, token=None, first_name=None, last_name=None, ssno=None, username=None, docType_id=None):
        self.password = password
        self.nombre = nombre
        self.email = email
        self.token = token
        self.username = token
        self.last_name = last_name
        self.ssno = ssno
        self.first_name = first_name
        self.docType_id = docType_id

        
    @staticmethod
    def get_by_id(id):
        return User.query.filter_by(id=id).first()

    def __repr__(self):
        return f'<User {self.id!r}>'
    
    def has_roles(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def get_user(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
    
    def get_all_by_name(firstname, lastname):
        if(firstname is not None and lastname is not None):
            users = User.query.filter(User.first_name.like(f'%{firstname}%')).filter(User.last_name.like(f'%{firstname}%'))
        if(firstname is not None and lastname is None):
            users = User.query.filter(User.first_name.like(f'%{firstname}%')).all()
        if(firstname is None and lastname is not None):
            users = User.query.filter(User.last_name.like(f'%{lastname}%'))    
        return users


    def set_password(self, password):
        hash_object = hashlib.sha1(bytes(password, 'utf-8'))
        hashed_client_secret = hash_object.hexdigest()
        self.password = hashed_client_secret 
        # self.password = generate_password_hash(password)

    def check_password(self, password):
        hash_object = hashlib.sha1(bytes(password, 'utf-8'))
        hashed_client_secret = hash_object.hexdigest()
        if self.password == hashed_client_secret:
            return True
        else:
            return False
        # return check_password_hash(self.password, password)

    def create(n):
        fkr = fk('es_CO')
        user = []
        print("Creando %s usuarios" % n)
        for i in range(n):
            lastName = fkr.last_name()
            firstName = fkr.first_name()
            fullname = firstName + ' ' + lastName
            username = "%s%s" % (firstName, lastName)
            username = unidecode(username.lower())
            email = username + '@gmail.com'
            token = uuid.uuid4()
            
            print("username %s" % username)
            
            new_user = User(
                password = 'add682f27131b98c268073f4a16ee18a89968747',
                nombre = fullname,
                email = email,
                token = token,
                username = username,
                first_name = firstName,
                last_name = lastName,
                ssno = '',
                docType_id = "CC"
            )
            
            print("Adding user: %s" % new_user)
            db.session.add(new_user)
            db.session.commit()
    
    def add_role(self, role):
        self.roles.append(role)

    def add_roles(self, roles):
        for role in roles:
            self.add_role(role)

    def get_roles(self):
        for role in self.roles:
            yield role
            

    
@dataclass
class PlantaPersonal(db.Model):
    """Tabla para almacenar la informacion entregada por Ecopetrol de la planta de personal para comparacion en el momento de registro

    Attributes:
        Npers : int
            Llave principal de la tabla de Planta de personal, auto incremental
        Nombres : str
            Nombres y apellidos del funcionario
        numero_doc : str
            Numero documento de identificacion del funcionario
        ssno : str
            Numero de registro Ecopetrol de identificacion del funcionario
        N1 : str
            Primer nivel de pertenencia al organigrama de Ecopetrol
        N2 : str
            Segundo nivel de pertenencia al organigrama de Ecopetrol
        N3 : str
            Tercer nivel de pertenencia al organigrama de Ecopetrol
        N4 : str
            Cuarto nivel de pertenencia al organigrama de Ecopetrol
        N5 : str
            Quinto nivel de pertenencia al organigrama de Ecopetrol
        NUO : str
            Pertenencia al Negocio en la estructura de Ecopetrol (NO SE ESTA USANDO)
        regional : str
            Regional a la que pertenece el funcionario
        ciudad : str
            Ciudad de registro del funcionario
        posicion : str
            Cargo del funcionario (NO SE ESTA USANDO)
        email : str
            Correo electronico del funcionario

    """
    __tablename__ = 'plantaPersonal'
    __table_args__ = {"schema": "Acceso"}
    NPers = Column(Integer, primary_key=True)
    Nombres = Column(String(50))
    numero_doc = Column(String(50))
    ssno = Column(String(50), unique=True)
    N1 = Column(String(50))
    N2 = Column(String(50))
    N3 = Column(String(50))
    N4 = Column(String(50))
    N5 = Column(String(50))
    NUO = Column(String(50))
    regional = Column(String(50))
    ciudad = Column(String(50))
    posicion = Column(String(50))
    email = Column(String(50))
    
    # registrados = relationship('Employee', backref='plantaPersonal',
    #                             primaryjoin='PlantaPersonal.numero_doc == Employee.numero_doc')


    def __init__(self, NPers=None, Nombres=None, numero_doc=None, ssno=None,email=None ):
        self.NPers = NPers
        self.Nombres = Nombres
        self.numero_doc = numero_doc
        self.ssno = ssno
        self.email = email


    @staticmethod
    def get_by_doc(numero_doc):
        """Obtiene todos el primer registro usando como filtros el documento de identificacion del usuario

        Args:
            structure ([str]): [Documento de identificacion del usuario ]

        Returns:
            [SQLAlchemy Object]: [Objeto con el primer registro de un usuario que coincidan con un documento de identificacion]
        """
        return PlantaPersonal.query.filter_by(numero_doc=numero_doc).first()
    
    @staticmethod
    def get_registrados():
        """Obtiene todos los registros de PlantaPersonal que tengan registro

        Args:
            

        Returns:
            [SQLAlchemy Object]: [Objeto con los registros de usuarios que estan registrados]
        """
        return PlantaPersonal.query.join(Employee, Employee.numero_doc == PlantaPersonal.numero_doc).all()
    
    @staticmethod
    def create(n):
        fkr = fk('es_CO')
        user = []
        types = ['E', 'C', 'V' ]
        
        print("Creando %s usuarios" % n)
        for i in range(n):
            lastName = fkr.last_name()
            firstName = fkr.first_name()
            fullname = firstName + ' ' + lastName
            username = "%s%s" % (firstName, lastName)
            username = unidecode(username.lower())
            email = username + '@gmail.com'
            numero_doc = '10' + fkr.ean(length=8)
            ssno = fkr.random_element(elements=('E', 'C', 'V')) + numero_doc[0:11]
            
            new_pp = PlantaPersonal(
                Nombres = fullname,
                email = email,
                numero_doc = numero_doc,
                ssno = ssno,
            )
            
            print("Adding user: %s" % new_pp)
            db.session.add(new_pp)
            db.session.commit()

    def __repr__(self):
        return f'<PlantaPersonal {self.numero_doc!r}>'

@dataclass
class PlantaContratistas(db.Model):
    """Tabla para almacenar la informacion entregada por Ecopetrol de la planta de personal para comparacion en el momento de registro

    Attributes:
        first_name : str
            Nombres del contratista
        last_name : str
            Apellidos del contratista
        numero_doc : str
            Numero de identificacion del Contratista
        department : str
            Departamento de ejecucion del contrato
        city : str  
            Ciudad de ejecucion del contrato
        status : str
            Estado del contrato (NO USADO)
        mandato : str
            Datos del mandato de ejecucion (NO USADO)

    """
    __tablename__ = 'plantaContratistas1'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    last_name = Column(String(50))
    first_name = Column(String(50))
    numero_doc = Column(String(50))
    department = Column(String(50))
    city = Column(String(50))
    status = Column(String(50))
    mandato = Column(String(50))
    


    def __init__(self, last_name=None, first_name=None, numero_doc=None, department=None, city=None, status=None, mandato=None):
        self.first_name = first_name
        self.last_name = last_name
        self.numero_doc = numero_doc
        self.department = department
        self.city = city
        self.status = status
        self.mandato = mandato
        

    @staticmethod
    def get_by_doc(numero_doc):
        """Obtiene todos el primer registro usando como filtros el documento de identificacion del contratista

        Args:
            structure ([str]): [Documento de identificacion del contratista ]

        Returns:
            [SQLAlchemy Object]: [Objeto con el primer registro de un contratista que coincidan con un documento de identificacion]
        """
        return PlantaContratistas.query.filter_by(numero_doc=numero_doc).first()

    @staticmethod
    def get_registrados():
        """Obtiene todos los registros de PlantaPersonal que tengan registro

        Args:
            

        Returns:
            [SQLAlchemy Object]: [Objeto con los registros de usuarios que estan registrados]
        """
        return PlantaContratistas.query.join(Employee, Employee.numero_doc == PlantaContratistas.numero_doc).all()

    def __repr__(self):
        return f'<PlantaContratistas {self.numero_doc!r}>'

@dataclass
class Employee(db.Model):
    """ Tabla para registro de Empleados, Contratistas y Visitantes. De esta tabla se utilizan los datos para relacionar el envio de imagenes a los dispositiovs, solo se pasa un usuario a esta tabla si ha podido verificarse que pertenece a la organizacion, es contratista de la misma o ha sido invitado
    
    En esta tabla se almacenan los registros biometricos antes de pasar a la tabla 
    empoyees, una vez han sido verificados con las tablas de empleados o con una 
    consulta a Lenel
    
    id : int
        Llave principal auto incremental
    last_name : str
        Apellidos
    first_name : str
        Nombres
    ssno : str
        Numero de registro Ecopetrol 
    id_status : int
        Llave foranea para status de la persona (Activo, inactivo, etc)
    status : str
        Cadena de texto indicando el status de la persona en Lenel(Activo, inactivo, etc )
    docType_id : str
        Tipo de documento
    numero_doc : str
        Numero documento de identificacion 
    isAuthorized : boolean
        Campo donde se almacena un bit de control en true si la persona ya hizo la doble validacion de identidad
    
    """
    __tablename__ = 'employee'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer)
    id_lenel = Column(String(50))
    last_name = Column(String(50)) 
    first_name = Column(String(50))
    ssno = Column(String(50))
    id_status = Column(String(50))
    status = Column(String(50))
    docType_id = Column(String(5))
    numero_doc = Column(String(50), primary_key=True)
    isAuthorized = Column(Boolean)
    company_id = Column(Integer)
    image_url = Column(String(250))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    site_id = Column(SmallInteger)
    region_id = Column(SmallInteger)
    metadatos = Column(String(250))
    badge_id = Column(String(50))
    origin_id = Column(SmallInteger)
    tipo_employee = Column(String(20))
    typeEmployee_id = Column(Boolean)
    union_doc = Column(String(50))
    prioridad = Column(Integer)
    negocio = Column(String(10))
    email = Column(String(100))
    visitante = Column(Boolean)
    created = Column(DateTime)
    updated = Column(DateTime)
    

    # sites = relationship('EmployeeSite', backref='Employee',
    #                             primaryjoin='EmployeeSite.numero_doc == Employee.numero_doc')
    


    def __init__(self,last_name=None, first_name=None, ssno=None, id_status=None, status=None, docType_id=None, numero_doc=None, isAuthorized=None, company_id=None, image_url=None,star_time=None,end_time=None,site_id=None, region_id=None,metadatos=None,badge_id=None,origin_id=None,tipo_employee=None,tipo_employee_id=None,union_doc=None,prioridad=None,negocio=None,email=None, visitante=None,created=None,updated=None):
        self.last_name = last_name
        self.first_name = first_name
        self.ssno = ssno
        self.id_status = status
        self.status = status
        self.numero_doc = numero_doc
        self.isAuthorized = isAuthorized
        self.company_id = company_id
        self.docType_id = docType_id
        self.image_url = None
        self.start_time = star_time
        self.end_time = end_time
        self.site_id = site_id
        self.region_id = region_id
        self.metadatos = metadatos
        self.badge_id = badge_id
        self.origin_id = origin_id
        self.tipo_employee = tipo_employee
        self.tipo_employee_id = tipo_employee_id
        self.union_doc = union_doc
        self.prioridad = prioridad
        self.negocio = negocio
        self.email = email
        self.visitante = visitante
        self.created = created
        self.updated = updated

    @staticmethod
    def get_by_doc(numero_doc):
        """Obtiene todos registros usando como filtros el documento de identificacion del usuario

        Args:
            numero_doc ([str]): [Documento de identificacion ]
    
        Returns:
            [SQLAlchemy Object]: [Objeto con todos registros que coincidan con un documento de identificacion]
            
        """
        return Employee.query.filter_by(numero_doc=numero_doc).first()
    
    
    @staticmethod
    def get_events_doc(numero_doc, direction):
        """Obtiene todos registros de entrada o salida

        Args:
            numero_doc ([str]): [Documento de identificacion ]
            direction (bool): [Direccion]
    
        Returns:
            [SQLAlchemy Object]: [Objeto con todos registros que coincidan con un documento de identificacion]
            
        """
        return Employee.query.filter_by(numero_doc=numero_doc).join(UploadPerson).filter(UploadPerson.user_id==Employee.numero_doc).filter(UploadPerson.device.direction.has(direction==direction)).all()
    

    def create(n):
        fkr = fk('es_CO')
        employee = []
        print("Creando %s empleados" % n)
        for i in range(n):
            lastName = fkr.last_name()
            firstName = fkr.first_name()
            numero_doc = '10' + fkr.ean(length=8)
            ssno = fkr.random_element(elements=('E', 'C', 'V')) + numero_doc[0:11]
            tipe_employee = fkr.random_element(elements=('Empleado', 'Contratista', 'Visitante')) + numero_doc[0:11]
            docType_id = 'CC'
            
            isAuthorized = fkr.random_element(elements=(True, False))
            company_id = 1
            region_id = 1
    
            
            new_employee = Employee(
                last_name = lastName,
                first_name = firstName,
                ssno = ssno,
                id_status = 1,
                status = 'Activo',
                numero_doc=numero_doc,
                isAuthorized=isAuthorized,
                company_id=company_id,
                region_id=region_id,
                docType_id=docType_id,
            )
            
            print("Adding employee: %s" % new_employee)
            db.session.add(new_employee)
            db.session.commit()


    def serialize(self):
        d = Serializer.serialize(self)
        return d
    

    def __repr__(self):
        return f'<Employee {self.numero_doc!r}>'


@dataclass
class UploadPerson(db.Model):
    """Tabla para almacenar los registros de reconocimiento de los dispositivos biometricos realizados 

    Attributes:
        id : int
            Llave principal auto incremental de la tabla
        msg_type : str(1)
            Tipo de mensaje reportado por MQTT
        similar : float
            Flotante indicando el nivel de similaridad del registro de reconocimiento 0 - 1
        user_id : str
            Documento de identificacion de la persona reconocida
        name : str
            Nombre de la persona reconocida
        time : datetime
            Campo de hora y tiempo del dispositivo biometrico
        mask : boolean
            Bit que relaciona si la persona reconocida lleva o no mascara
        matched : boolean
            Bit que relaciona si la persona fue reconocida o no
        device_id : str 
            Numero de serie del dispositivo
        image_url : str
            Direccion URL donde esta almacenada la imagen capturada si se habilita en los dispositivos
        isAuthorized : bool
            Bit que indica si la persona ya hizo doble validacion de identidad
        server_timestamp : datetime
            Campo de hora y tiempo del servidor
        sent_msg : str
            Mensaje enviado a LenelServices para el registro del evento y apertura de la puerta
        lenel_response : str
            Campo de texto donde se almacena la respuesta de LenelServices
        device : relationship
            Relacion OneToOne para obtener los datos del dispositivo (Relacion con Model Device)
            
    Returns:
        [type]: [description]
        
    """
    __tablename__ = 'uploadPerson'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    msg_type = Column(String(1))
    similar = Column(Float)
    user_id = Column(String(50), ForeignKey('Acceso.employee.numero_doc'))
    name = Column(String(100))
    time = Column(DateTime)
    mask = Column(Boolean)
    matched = Column(Boolean)
    device_id = Column(String(50), ForeignKey('Acceso.device.device_id'))
    image_url = Column(String(50))
    isAuthorized = Column(Boolean)
    server_timestamp = Column(DateTime)
    sent_msg = Column(String(50))
    lenel_response = Column(String(250))
    device = relationship('Device', backref='UploadPerson', 
                                primaryjoin='UploadPerson.device_id == Device.device_id')
    persona = relationship('Employee', backref='UploadPerson', viewonly=True, sync_backref=False, 
                                primaryjoin='UploadPerson.user_id == Employee.numero_doc')
    


    def __init__(self, msg_type=None, similar=None, user_id=None, name=None, time=None, mask=None, matched=None, device_id=None, image_url=None, isAuthorized=None, server_timestamp=None, site_id=None, sent_msg=None, lenel_response=None):
        self.msg_type = msg_type
        self.similar = similar
        self.user_id = user_id
        self.name = name
        self.time = time
        self.mask = mask
        self.matched = matched
        self.device_id = device_id
        self.image_url = image_url
        self.isAuthorized = isAuthorized
        self.server_timestamp = server_timestamp
        self.sent_msg = sent_msg
        self.lenel_response = lenel_response
    
    
    def create(n, direction=None, date=None):
        fkr = fk('es_CO')
        print("Creando %s eventos de reconocimiento" % n)
        
        
        # lastName = fkr.last_name()
        # firstName = fkr.first_name()
        # numero_doc = '10' + fkr.ean(length=8)
        # ssno = fkr.random_element(elements=('E', 'C', 'V')) + numero_doc[0:11]
        # docType_id = 'CC'
        
        for i in range(n):
            isRecognized = bool(random.getrandbits(1))
            msg_type = 1
            if (direction is not None):
                device_id = fkr.random_element(Device.query.with_entities(Device.device_id).filter(Device.direction==direction).all())[0]
            else:
                device_id = fkr.random_element(Device.query.with_entities(Device.device_id).all())[0]
            site_id = Device.query.get(device_id).site_id
            if date is None:
                time = fkr.date_time_between(start_date = "-1M", end_date = "now")
            else:
                time = fkr.date_time_between(start_date = date, end_date = date)
                
            server_timestamp = time
            mask = bool(random.getrandbits(1))
            isAuthorized = bool(random.getrandbits(1))
            
            if isRecognized:
                similar = random.randint(52,99)/100
                user_id = fkr.random_element(Employee.query.with_entities(Employee.numero_doc).all())[0]
                employee = Employee.query.get(user_id)
                name = employee.first_name + ' ' + employee.last_name
                matched = 1
            else:
                similar = 0
                matched = 0
                name = ''
                user_id = ''
            
            
            new_upload_person = UploadPerson(
                msg_type=msg_type,
                similar=similar,
                user_id=user_id,
                name=name,
                time=time.strftime('%Y-%m-%d %H:%M:%S'),
                mask=mask,
                matched=matched,
                device_id=device_id,
                image_url=None,
                isAuthorized=isAuthorized,
                server_timestamp=server_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                site_id=site_id
            )
            
            print("Adding uploadPerson %s : %s" % (i, new_upload_person))
            db.session.add(new_upload_person)
            db.session.commit()

    @staticmethod
    def get_by_doc(numero_doc, limit):
        """Obtiene n (limit) registros usando como filtros el documento de identificacion del contratista

        Args:
            numero_doc ([str]): [Documento de identificacion ]
            limit ([str]): [Numero de registros a obtener ]

        Returns:
            [SQLAlchemy Object]: [Objeto con n (limit) registros de reconocimientos que coincidan con un documento de identificacion]
            
        """
        return UploadPerson.query.filter_by(user_id=numero_doc).order_by(UploadPerson.id.desc()).limit(limit)

    @staticmethod
    def get_last_by_doc(numero_doc):
        """Obtiene el ultimo registro usando como filtros el documento de identificacion del contratista

        Args:
            numero_doc ([str]): [Documento de identificacion ]

        Returns:
            [SQLAlchemy Object]: [Objeto con el ultimo registro de reconocimiento que coincidan con un documento de identificacion]
            
        """
        return UploadPerson.query.filter_by(user_id=numero_doc).order_by(UploadPerson.time.desc()).first()
    
    @staticmethod
    def get_last_unauthorized(numero_doc):
        """Obtiene el ultimo registro usando como filtros el documento de identificacion del contratista y la condicion isAuthorized = 0

        Args:
            numero_doc ([str]): [Documento de identificacion ]

        Returns:
            [SQLAlchemy Object]: [Objeto con el ultimo registro de reconocimiento que coincidan con un documento de identificacion y con el bit isAuthorized en 0]
            
        """
        return UploadPerson.query.filter_by(user_id=numero_doc).filter(UploadPerson.isAuthorized == False).order_by(UploadPerson.time.desc())
    
    @staticmethod
    def get_last_authorized(numero_doc):
        """Obtiene el ultimo registro usando como filtros el documento de identificacion del contratista y la condicion isAuthorized = 1

        Args:
            numero_doc ([str]): [Documento de identificacion ]

        Returns:
            [SQLAlchemy Object]: [Objeto con el ultimo registro de reconocimiento que coincidan con un documento de identificacion y con el bit isAuthorized en 1]
            
        """
        return UploadPerson.query.filter_by(user_id=numero_doc).filter(UploadPerson.isAuthorized == True).order_by(UploadPerson.time.desc())
    
    @staticmethod
    def get_last(numero_doc, start_date = None, end_date = None, site_id = None):
        """Obtiene el ultimo registro usando como filtros el documento de identificacion del contratista 

        Args:
            numero_doc ([str]): [Documento de identificacion ]

        Returns:
            [SQLAlchemy Object]: [Objeto con el ultimo registro de reconocimiento que coincidan con un documento de identificacion]
            
        """
        last = UploadPerson.query.filter_by(user_id=numero_doc).filter(UploadPerson.server_timestamp >= start_date).filter(UploadPerson.server_timestamp <= end_date).order_by(UploadPerson.server_timestamp.desc()).limit(1)
        return last.first()

    @staticmethod
    def get_all_by_doc_and_date(numero_doc, start_date = None, end_date = None, site_id = None):
        """Obtiene el ultimo registro usando como filtros el documento de identificacion del contratista 

        Args:
            numero_doc ([str]): [Documento de identificacion ]

        Returns:
            [SQLAlchemy Object]: [Objeto con el ultimo registro de reconocimiento que coincidan con un documento de identificacion]
            
        """
        events = UploadPerson.query.with_entities(UploadPerson.server_timestamp.label('server_timestamp'), Device.site_id.label('site_id'),  Device.direction.label('direction')).filter_by(user_id=numero_doc).filter(UploadPerson.server_timestamp >= start_date).filter(UploadPerson.server_timestamp <= end_date).join(Device).filter(Device.device_id == UploadPerson.device_id).order_by(UploadPerson.server_timestamp.asc())
        return events.all()
    
    @staticmethod
    def get_first(numero_doc, start_date = None, end_date = None, site_id = None):
        """Obtiene el primer registro usando como filtros el documento de identificacion del contratista y la condicion isAuthorized = 1

        Args:
            numero_doc ([str]): [Documento de identificacion ]

        Returns:
            [SQLAlchemy Object]: [Objeto con el primer registro de reconocimiento que coincidan con un documento de identificacion y con el bit isAuthorized en 1]
        """
        first = UploadPerson.query.filter_by(user_id=numero_doc).filter(UploadPerson.server_timestamp >= start_date).filter(UploadPerson.server_timestamp <= end_date).order_by(UploadPerson.server_timestamp.asc()).limit(1)
        
        return first.first()

    @staticmethod
    def get_all_by_site(site_id, startDate, endDate):
        """Obtiene todos los registros usando como filtros el nemonico de un site y un rango de fechas

        Args:
            site_id ([str]): [Nemonico del sitio]
            startDate ([datetime]): [Fecha de inicio del rango de fechas]
            endDate ([datetime]): [Fecha de termino del rango de fechas]

        Returns:
            [SQLAlchemy Object]: [Objeto con el los registros de reconocimiento que coincidan con un nemonico en un rango de fechas. Para lograrlo hace el join con la tabla device para determinar el sitio de instalacion]
            
        """
        devices = Device.get_all_by_site_id(site_id)
        res = []
        for result in devices:
            result_res = result.device_id
            res.append(result_res)
        if(startDate is not None and endDate is not None):
            uploads = UploadPerson.query.filter(UploadPerson.device_id.in_(res)).filter(UploadPerson.server_timestamp >= startDate).filter(UploadPerson.server_timestamp <= endDate)
        if(startDate is not None and endDate is None):
            uploads = UploadPerson.query.filter(UploadPerson.device_id.in_(res)).filter(UploadPerson.server_timestamp >= startDate)
        if(startDate is None and endDate is None):
            uploads = UploadPerson.query.filter(UploadPerson.device_id.in_(res))
        return uploads
    
    @staticmethod
    def get_all_by_date(startDate, endDate):
        """Obtiene todos los registros usando como filtros el nemonico de un site y un rango de fechas

        Args:
            site_id ([str]): [Nemonico del sitio]
            startDate ([datetime]): [Fecha de inicio del rango de fechas]
            endDate ([datetime]): [Fecha de termino del rango de fechas]

        Returns:
            [SQLAlchemy Object]: [Objeto con el los registros de reconocimiento que coincidan con un nemonico en un rango de fechas. Para lograrlo hace el join con la tabla device para determinar el sitio de instalacion]
            
        """
        if(startDate is not None and endDate is not None):
            uploads = UploadPerson.query.filter(UploadPerson.server_timestamp >= startDate).filter(UploadPerson.server_timestamp <= endDate).filter(UploadPerson.matched == True).order_by(UploadPerson.server_timestamp.desc())
        if(startDate is not None and endDate is None):
            uploads = UploadPerson.query.filter(UploadPerson.server_timestamp >= startDate).filter(UploadPerson.matched == True).order_by(UploadPerson.server_timestamp.desc())
        return uploads
    
    @staticmethod
    def get_all_by_date_inputs(startDate, endDate):
        """Obtiene todos los registros usando como filtros el nemonico de un site y un rango de fechas

        Args:
            site_id ([str]): [Nemonico del sitio]
            startDate ([datetime]): [Fecha de inicio del rango de fechas]
            endDate ([datetime]): [Fecha de termino del rango de fechas]

        Returns:
            [SQLAlchemy Object]: [Objeto con el los registros de reconocimiento que coincidan con un nemonico en un rango de fechas. Para lograrlo hace el join con la tabla device para determinar el sitio de instalacion]
            
        """
        
        if(startDate is not None and endDate is not None):
            entries = UploadPerson.query.filter(UploadPerson.server_timestamp >= startDate).filter(UploadPerson.server_timestamp <= endDate)
        if(startDate is not None and endDate is None):
            uploads = UploadPerson.query.filter(UploadPerson.server_timestamp >= startDate)
        return uploads
    
    @staticmethod
    def get_all_by_site_doc(documento, site_id = None, startDate = None , endDate = None):
        """Obtiene todos los registros usando como filtros el nemonico de un site, un rango de fechas y un documento de identificacion

        Args:
            documento ([str]) : Numero de documento de un usuario
            site_id ([str]): [Nemonico del sitio]
            startDate ([datetime]): [Fecha de inicio del rango de fechas]
            endDate ([datetime]): [Fecha de termino del rango de fechas]

        Returns:
            [SQLAlchemy Object]: [Objeto con el los registros de reconocimiento que coincidan con un nemonico en un rango de fechas y para un usario especifico. Para lograrlo hace el join con la tabla device para determinar el sitio de instalacion]
            
        """
        if (site_id is not None):
            devices = Device.get_all_by_site_id(site_id)
            res = []
            for result in devices:
                result_res = result.device_id
                res.append(result_res)
            if(startDate is not None and endDate is not None):
                uploads = UploadPerson.query.filter(UploadPerson.device_id.in_(res)).filter_by(user_id=documento).filter(UploadPerson.server_timestamp >= startDate).filter(UploadPerson.server_timestamp <= endDate).all()
            if(startDate is not None and endDate is None):
                uploads = UploadPerson.query.filter(UploadPerson.device_id.in_(res)).filter_by(user_id=documento).filter(UploadPerson.server_timestamp >= startDate).all()
            if(startDate is None and endDate is None):
                uploads = UploadPerson.query.filter_by(user_id=documento).filter(UploadPerson.device_id.in_(res)).all()
            # return UploadPerson.query.filter(device_id.in_(devices)).all()
        else:
            if(startDate is not None and endDate is not None):
                uploads = UploadPerson.query.filter_by(user_id=documento).filter(UploadPerson.server_timestamp >= startDate).filter(UploadPerson.server_timestamp <= endDate).all()
            if(startDate is not None and endDate is None):
                uploads = UploadPerson.query.filter_by(user_id=documento).filter(UploadPerson.server_timestamp >= startDate).all()
            if(startDate is None and endDate is None):
                uploads = UploadPerson.query.filter_by(user_id=documento).all()
        return uploads



    def __repr__(self):
        return f'<UploadPerson {self.device_id!r}>'

@dataclass
class EmployeeSite(db.Model):
    """Tabla para relacionar la carga de imagenes en los diferentes dispositivos

        Attributes:
            id : int
                Llave principal de la tabla, auto incremental
            docType_id : str
                Llave foranea, Tipo de documento de identidad
            numero_doc : str
                Documento de identidad del Funcionario / Contratista o visitante
            site_id : str
                Nemonico del sitio de instalacion del dispositivo biometrico
            procesado : boolean
                Indica si la imagen fue procesada (enviada) al dispositivo
            device_id : str
                Numero de serie del dispositivo
            device : relationship
                Relacion OneToOne con los datos del dispositivo
            ecopass_time : datetime
                Fecha y Hora de recepcion del Ecopass con el que se envian las imagenes
            uploadfoto_time : datetime
                Fecha y Hora de recepcion de la imagen por el dispositivo
            passport_id : integer
                Campo de relacion con la tabla de Ecopasaportes recibidos    
    """
    __tablename__ = 'employeeSite'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    docType_id = Column(String(2)) 
    numero_doc = Column(String(50), ForeignKey('Acceso.employee.numero_doc'))
    # employee = relationship('Employee', foreign_keys=numero_doc)
    site_id = Column(String(10))
    procesado = Column(Boolean)
    device_id = Column(String(50), ForeignKey('Acceso.device.device_id'))
    # device = relationship('Device', foreign_keys=device_id)
    ecopass_time = Column(DateTime)
    uploadfoto_time = Column(DateTime)
    passport_id = Column(Integer, ForeignKey('Acceso.passport.id'))
    


    def __init__(self, docType_id=None, numero_doc=None, site_id=None, procesado=None, device_id=None, ecopass_time=None, uploadfoto_time=None, passport_id=None):
        self.docType_id = docType_id
        self.numero_doc = numero_doc
        self.site_id = site_id
        self.procesado = procesado
        self.device_id = device_id
        self.ecopass_time = ecopass_time
        self.uploadfoto_time = uploadfoto_time
        self.passport_id = passport_id
        

    @staticmethod
    def get_by_doc(numero_doc):
        """Obtiene todos registros usando como filtros el documento de identificacion del usuario

        Args:
            numero_doc ([str]): [Documento de identificacion ]
    
        Returns:
            [SQLAlchemy Object]: [Objeto con todos registros de envio de imagenes a dispositivos que coincidan con un documento de identificacion]
            
        """
        return EmployeeSite.query.filter_by(numero_doc=numero_doc).distinct(EmployeeSite.device_id).all()

    @staticmethod
    def get_by_doc_site(numero_doc, site_id):
        """Obtiene todos registros usando como filtros el documento de identificacion del usuario para un site_id especifico

        Args:
            numero_doc ([str]): [Documento de identificacion ]
            site_id ([str]): [Nemonico de la instalacion a consultar ]
    
        Returns:
            [SQLAlchemy Object]: [Objeto con todos registros de envio de imagenes a dispositivos que coincidan con un documento de identificacion y un site_id]
            
        """
        return EmployeeSite.query.filter_by(numero_doc=numero_doc).filter(EmployeeSite.site_id.like(site_id)).all()

    @staticmethod
    def get_by_doc_site_pass(numero_doc, site_id, pass_id):
        """Obtiene todos registros usando como filtros el documento de identificacion del usuario para un site_id especifico relacionadas con un numero de Ecopass

        Args:
            numero_doc ([str]): [Documento de identificacion ]
            site_id ([str]): [Nemonico de la instalacion a consultar ]
            pass_id ([str]): [Numero de ecopass  para la instalacion a consultar ]
    
        Returns:
            [SQLAlchemy Object]: [Objeto con todos registros de envio de imagenes a dispositivos que coincidan con un documento de identificacion y un site_id generadas por un Ecopass especifico]
            
        """
        if site_id is not None and pass_id is not None:
            return EmployeeSite.query.with_entities(EmployeeSite.id, EmployeeSite.site_id).filter_by(numero_doc=numero_doc).filter(EmployeeSite.site_id.like(site_id)).filter(EmployeeSite.passport_id.like(pass_id)).first()
        if site_id is not None and pass_id is None:
            return EmployeeSite.query.with_entities(EmployeeSite.id, EmployeeSite.site_id).filter_by(numero_doc=numero_doc).filter(EmployeeSite.site_id.like(site_id)).filter(EmployeeSite.procesado == 1).first()
        if site_id is None and pass_id is None:
            return EmployeeSite.query.with_entities(EmployeeSite.id, EmployeeSite.site_id).filter_by(numero_doc=numero_doc).first()

    def __repr__(self):
        return f'<EmployeeSite {self.numero_doc!r}>'



@dataclass
class DeviceLenel(db.Model):
    """Tabla que relaciona los dispositivos biometricos con los panel_id y reader_id creados en lenel para las mismas. Esta informacion se enviara a LenelServices para el procesamiento

    Attributes:
        device_id : str
            Numero de serie del dispositivo biometrico
        panelid_door : integer
            Numero de identificacion del panel de la puerta asociada
        readerid_door : integer 
            Numero de identificacion del reader de la puerta asociada
        panelid_destino : integer 
            Numero de identificacion del panel logico asociado con el dispositivo biometrico
        subdevice_id : integer 
            Numero de identificacion del subdevice logico asociado con el dispositivo biometrico
        tiene_puerta : boolean
            Bit que identifica si un dispositivo biometrico tiene puerta asociado con el dispositivo biometrico
            
    Returns:
        [type]: [description]
        
    """
    __tablename__ = 'device_lenel'
    __table_args__ = {"schema": "Acceso"}
    device_id = Column(String(50), ForeignKey('Acceso.device.device_id'), primary_key=True)
    panelid_door = Column(Integer)
    readerid_door = Column(Integer)
    panelid_destino = Column(Integer)
    subdevice_id = Column(Integer)
    tiene_puerta = Column(Boolean)

    def __init__(self, panelid_door=None, readerid_door=None, panelid_destino=None, subdevice_id=None, tiene_puerta=None):
        self.panelid_door = panelid_door
        self.readerid_door = readerid_door
        self.panelid_destino = panelid_destino
        self.subdevice_id = subdevice_id
        self.tiene_puerta = tiene_puerta

    @staticmethod
    def get_by_serial(device_id):
        """Obtiene la informacion de relacion lenel / biometrico para un numero serial de dispositivo biometrico especificado

        Args:
            device_id ([str]): [Numero serial del dispositivo]

        Returns:
            [SQLAlchemy Object]: [Datos de relacion dispositivo / lenel para un serial especifico]
            
        """
        return DeviceLenel.query.filter_by(device_id=device_id).first()

    def __repr__(self):
        return f'<DeviceLenel {self.device_id!r}>'


@dataclass
class LogEventosAcceso(db.Model):
    """Tabla donde se almacenan unicamente los registros de intentos de acceso (concedidos o no) reconocidos

    """
    __tablename__ = 'logEventosAcceso'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    user_id = Column(String(30))
    device_id = Column(String(50), ForeignKey('Acceso.device.device_id'), primary_key=True)
    lenel_door = Column(String(50))
    is_authorized = Column(Boolean)
    ecopass = Column(Boolean)
    tipo_usuario = Column(String(50))
    permiso_acceso = Column(Boolean)
    badge_activo = Column(Boolean)
    lenel_data = Column(Boolean)
    msg_onTime = Column(Boolean)
    tiene_tapabocas = Column(Boolean)
    created = Column(DateTime)
    uploadPerson_id = Column(Integer)
    

    def __init__(self, user_id=None, device_id=None, lenel_door=None, isAuthorized=None, ecopass=None, tipo_usuario=None, permiso_acceso=None, badge_activo=None,lenel_data=None, tiene_tapabocas=None, created=None, uploadPerson_id=None, msg_onTime=None):
        self.device_id = device_id
        self.user_id = user_id
        self.lenel_door = lenel_door
        self.isAuthorized = isAuthorized
        self.ecopass = ecopass
        self.tipo_usuario = tipo_usuario
        self.permiso_acceso = permiso_acceso
        self.badge_activo = badge_activo
        self.lenel_data = lenel_data
        self.tiene_tapabocas = tiene_tapabocas
        self.msg_onTime = msg_onTime
        self.created = created
        self.uploadPerson_id = uploadPerson_id
        

    @staticmethod
    def get_by_userId(user_id):
        """Obtiene todos registros usando como filtros el numero de registro de uploadPerson

        Args:
            numero_doc ([str]): [Documento de identificacion ]
    
        Returns:
            [SQLAlchemy Object]: [Objeto con todos registros que coincidan con un numero de registro de uploadPerson]
            
        """
        upId = int(user_id)
        eventos = LogEventosAcceso.query.filter_by(user_id=upId).all()
        
        res = []
        for evento in eventos:
            ev_res = jsonify(evento)
            res.append(ev_res)
    
        return res

    def __repr__(self):
        return f'<DeviceLenel {self.device_id!r}>'

@dataclass
class CiudadRegion(db.Model):
    """Tabla parametrica para relacionar la Ciudad y la regional

    
        id ([int]): [Llave principal auto incremental]
        regional_lectora ([str]): [Regional a la que pertenece un dispositivo biometrico]
        ciudad ([str]): [Ciudad donde esta localizado el dispositivo biometrico]
        
    """
    __tablename__ = 'ciudadRegion'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    regional_lectora = Column(String(50))
    ciudad = Column(String(150))
    
    def __init__(self, regional_lectora=None, ciudad=None):
        self.regional_lectora = regional_lectora
        self.ciudad = ciudad
    
    def get_ciudades_by_regional(regional):
        """Consultar las ciudades que pertenecen a una regional,  si hay biometrico instalado

        Args:
            regional ([str]): [Regional a consultar]

        Returns:
            [SQLalchemy object]: [ciudades que pertenecen a una regional,  si hay biometrico instalado]

        """
        regional = "%{}%".format(regional)
        return CiudadRegion.query.filter(CiudadRegion.regional_lectora.like(regional)).all()
    
    def seed():
        db.session.add(CiudadRegion('VAO-SUR','Neiva'))
        db.session.add(CiudadRegion('VAO-SUR','Neiva-Rio Ceiba'))
        db.session.add(CiudadRegion('VAO-SUR','Orito'))
        db.session.add(CiudadRegion('VRO','Apiay'))
        db.session.add(CiudadRegion('VRO','Castilla'))
        db.session.add(CiudadRegion('VRO','Villavicencio'))
        db.session.add(CiudadRegion('VPI','Cupiagua'))
        db.session.add(CiudadRegion('VPI','Floreña'))
        db.session.add(CiudadRegion('VAO-ORIENTE','Rubiales'))
        db.session.add(CiudadRegion('BOGOTA','Bogotá'))
        db.session.add(CiudadRegion('VRC','B/bermeja Galán'))
        db.session.add(CiudadRegion('VRC','B/bermeja-polic'))
        db.session.add(CiudadRegion('VRC','Barrancabermeja'))
        db.session.add(CiudadRegion('VRC','Bucaramanga'))
        db.session.add(CiudadRegion('VRC','Cantagallo'))
        db.session.add(CiudadRegion('VRC','Casabe'))
        db.session.add(CiudadRegion('VRC','Cúcuta'))
        db.session.add(CiudadRegion('VRC','Cúcuta-Caño Lim'))
        db.session.add(CiudadRegion('VRC','El Centro'))
        db.session.add(CiudadRegion('VRC','Hosp El Centro'))
        db.session.add(CiudadRegion('VRC','Lizama'))
        db.session.add(CiudadRegion('VRC','Piedecuesta'))
        db.session.add(CiudadRegion('VRC','Provincia'))
        db.session.add(CiudadRegion('VRC','Puerto Wilches'))
        db.session.add(CiudadRegion('CARIBE','Cartagena'))
        db.session.add(CiudadRegion('CENIT','Mansilla'))
        db.session.add(CiudadRegion('CENIT','Puerto Salgar'))
        db.session.add(CiudadRegion('CENIT','Villeta'))
        db.session.add(CiudadRegion('CENIT','Barranquilla'))
        db.session.add(CiudadRegion('CENIT','Coveñas C Afuer'))
        db.session.add(CiudadRegion('CENIT','Pozos Colorados'))
        db.session.add(CiudadRegion('CENIT','Chimita'))
        db.session.add(CiudadRegion('CENIT','Cocorná'))
        db.session.add(CiudadRegion('CENIT','Cúcuta-Caño Lim'))
        db.session.add(CiudadRegion('CENIT','Orú'))
        db.session.add(CiudadRegion('CENIT','Sn Martin Cesar'))
        db.session.add(CiudadRegion('CENIT','Vasconia'))
        db.session.add(CiudadRegion('CENIT','Araguaney'))
        db.session.add(CiudadRegion('CENIT','Cali'))
        db.session.add(CiudadRegion('CENIT','Cartago'))
        db.session.add(CiudadRegion('CENIT','Gualanday'))
        db.session.add(CiudadRegion('CENIT','Manizales'))
        db.session.add(CiudadRegion('CENIT','Medellín'))
        db.session.add(CiudadRegion('CENIT','Pereira'))
        db.session.add(CiudadRegion('VAO-SUR','Neiva-Dina'))
        db.session.add(CiudadRegion('VRO','Chichimene'))
        db.session.add(CiudadRegion('VRC','Tibú'))
        db.session.add(CiudadRegion('VRC','La Cira Infanta'))
        db.session.add(CiudadRegion('VRC','Sabana Torres'))
        db.session.add(CiudadRegion('VRC','Llanito'))
        db.session.add(CiudadRegion('VAO-SUR','La Hormiga'))
        db.session.add(CiudadRegion('CENIT','Dosquebradas'))
        db.session.add(CiudadRegion('CARIBE','Santa Marta'))
        db.session.add(CiudadRegion('VRC','Yondó'))
        db.session.add(CiudadRegion('VAO-SUR','Mansoya'))
        db.session.add(CiudadRegion('VAO-ORIENTE','Puerto Gaitan'))
        db.session.add(CiudadRegion('CENIT','Porvenir'))
        db.session.add(CiudadRegion('CENIT','Yumbo'))
        db.session.add(CiudadRegion('CENIT','Samoré'))
        db.session.add(CiudadRegion('CARIBE','C/gena-Mamonal'))
        db.session.add(CiudadRegion('CARIBE','Salud Cartagena'))
        db.session.add(CiudadRegion('VPI','Yopal'))
        db.session.add(CiudadRegion('CARIBE','Coveñas - DOL'))
        db.session.add(CiudadRegion('VRC','Cela Orien Tibú'))
        db.session.add(CiudadRegion('VPI','Cusiana'))
        db.session.add(CiudadRegion('CENIT','Bog Pte. Aranda'))
        db.session.add(CiudadRegion('VRO','Castilla VIT'))
        db.session.add(CiudadRegion('VAO-SUR','Neiva-Tello'))
        db.session.add(CiudadRegion('BOGOTA','Bogotá-Teusacá'))
        db.session.add(CiudadRegion('VAO-SUR','Neiva-San Fco'))
        db.session.add(CiudadRegion('VRC','El Centro Afuer'))
        db.session.add(CiudadRegion('CENIT','Sebastopol'))
        
        db.session.commit()

    def __repr__(self):
        return f'<CiudadRegion {self.regional_lectora!r}>'

@dataclass
class TipoDisponibilidad(db.Model):
    """Tabla parametrica para relacionar los tipos de disponibilidad de un espacio
        id ([int]): [Llave principal auto incremental]
        tipo_disponibilidad ([str]): [Tipo de espacio]
        
    """
    __tablename__ = 'tipo_disponibilidad'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    disponibilidad = Column(String(100))
    sigla = Column(String(5))
    
    def __init__(self, disponibilidad=None, sigla=None):
        self.disponibilidad = disponibilidad
        self.sigla = sigla


    def seed():
        db.session.add(TipoDisponibilidad('Disponible', 'DISP'))
        db.session.add(TipoDisponibilidad('Ocupado', 'OCUP'))
        db.session.add(TipoDisponibilidad('Restringido', 'REST'))
        db.session.add(TipoDisponibilidad('Reservado', 'RSVD'))
        db.session.add(TipoDisponibilidad('Reparaciones', 'REPA'))
        db.session.add(TipoDisponibilidad('VIP', 'VIP'))
        db.session.commit()
    
    def __repr__(self):
        return f'<TipoEspacio {self.sigla!r}>'

@dataclass
class TipoEspacio(db.Model):
    """Tabla parametrica para relacionar los tipos de Espacios disponibles

    
        id ([int]): [Llave principal auto incremental]
        tipo_espacio ([str]): [Tipo de espacio]
        
    """
    __tablename__ = 'tipo_espacio'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    tipo_espacio = Column(String(100))
    sigla = Column(String(5))
    
    def __init__(self, tipo_espacio=None, sigla=None):
        self.tipo_espacio = tipo_espacio
        self.sigla = sigla


    def seed():
        db.session.add(TipoEspacio('Puesto de trabajo general individual', 'PTGI'))
        db.session.add(TipoEspacio('Puesto de trabajo general multiple', 'PTGM'))
        db.session.add(TipoEspacio("Oficina individual", 'OFII'))
        db.session.add(TipoEspacio("Oficina equipo", 'OFIE'))
        db.session.add(TipoEspacio("Sala de reuniones", 'SR'))
        db.session.add(TipoEspacio("Area de reuniones", 'AR'))
        db.session.add(TipoEspacio("Auditorio", 'AUD'))
        db.session.commit()
    
    def __repr__(self):
        return f'<TipoEspacio {self.sigla!r}>'

@dataclass
class Espacio(db.Model):
    """Tabla parametrica para relacionar los Espacios disponibles

        id ([int]): [Llave principal auto incremental]
        espacio ([str]): [Nombre de espacio]
        tipo_espacio ([str]): [Tipo de espacio]
        instalacion_id ([int]): [Nemonico de la instalacion]
        piso ([str]): [Piso en que se encuentra localizado (Incluye sotanos, mesanines etc)]
        capacidad ([int]): Aforo posible

        
    """
    __tablename__ = 'espacio'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    espacio = Column(String(100))
    tipo_espacio_id = Column(Integer, ForeignKey('Acceso.tipo_espacio.id'))
    tipo_disponibilidad_id = Column(Integer, ForeignKey('Acceso.tipo_disponibilidad.id'))
    instalacion_id = Column(String(50), ForeignKey('Acceso.instalacion.nemonico'))
    piso = Column(String(5))
    capacidad = Column(Integer)
    
    # instalacion = relationship('Instalation', backref='Espacio',
    #                      primaryjoin='Instalation.nemonico == Espacio.instalacion_id', viewonly=True, sync_backref=False)
    
    
    
    def __init__(self, espacio=None, tipo_espacio_id=None, tipo_disponibilidad_id=None, instalacion_id=None, piso=None, capacidad=None):
        self.espacio = espacio
        self.tipo_espacio_id = tipo_espacio_id
        self.tipo_disponibilidad_id = tipo_disponibilidad_id
        self.instalacion_id = instalacion_id
        self.piso = piso
        self.capacidad = capacidad
        
    def create(n):
        fkr = fk('es_CO')
        espacio = []
        print("Creando %s espacios" % n)
        
        tipos = TipoEspacio.query.all()
        disponibilidades = TipoDisponibilidad.query.all()
        
        
        for i in range(n):
            espacio = ''
            capacidad = 1
            tipo_espacio_id = fkr.random_element(elements=(1,2,3,4,5,6,7))
            tipo_disponibilidad_id = fkr.random_element(elements=(1,2,3,4,5,6))
            instalacion_id = fkr.random_element(elements=('ANT-CAUC','ANT-CISN','ANT-GIRC','ANT-MEDN','ANT-PINC','ANT-REME','API-CL','API-ERA','API-GYAS','API-IV','API-OFIC','API-PZ','API-REFM','API-SURI','API-TOCO','API-TSUR','ARA-BAND','ATL-BARN','BOG-1335','BOG-AMAD','BOG-ARND','BOG-CAXD','BOG-PPAL','BOG-TAR','BOG-TEUS','BOL-RET','BOY-EMIR','BOY-MIRF','BOY-PAEZ','BOY-SUTA','BOY-VASC','CAL-MANZ','CAS-APOR','CAS-ARGY','CAS-CCM4','CAS-CDF','CAS-CDK','CAS-CDM','CAS-CL','CAS-CMA','CAS-CMD','CAS-CMT','CAS-DIS1','CAS-DIS3','CAS-DIS4','CAS-EAK','CAS-EC1','CAS-EC2','CAS-EC3','CAS-EPOR','CAS-ESAN','CAS-IV','CAS-JAGU','CAS-JARD','CAS-MONT','CAS-OFIC','CAS-PZ','CAS-SFER','CAS-VK10','CAS-VK22','CES-AYAC','CES-COPY','CHI-BMAT','CHI-CDO','CHI-CHIC','CHI-CL','CHI-CMTN','CHI-CMTO','CHI-CMTS','CHI-CMVQ','CHI-IV','CHI-PDES','CHI-PIAR','CHI-PTUB','CNG-CRIS','CNG-EAUX','CNG-ECOB','CNG-GARZ','CNG-ISI','CNG-ISIV','CNG-ISV','CNG-ISVI','CNG-ZIND','COR-GRAN','COR-TMC','CSB-CNDR','CSB-EST2','CSB-EST3','CSB-EST4','CSB-EST5','CSB-ESTS','CSB-PEÑB','CSB-PIA','CSB-ZIND','CSE-CANI','CSE-CSE8','CSE-CX14','CSE-CX5','CSE-EP1','CSE-MIT1','CSE-MIT2','CSE-PAD2','CTG-EVIP','CTG-MREF','CTG-MTNP','CTG-REF','CTG-TTNP','CTG-USO','CUC-OFIC','CUN-ALB','CUN-CCO','CUN-GUAD','CUN-MANS','CUN-PSLG','CUN-TOCA','CUN-USO','CUN-VILL','CUP-CPF','CUP-ECUP','CUP-H','CUP-K','CUP-NW','CUP-PTUB','CUP-T','CUP-VK12','CUP-VK26','CUP-VK8','CUP-XH','CUP-XL','CUP-YD','CUS-BA11','CUS-BA14','CUS-BAG','CUS-BAGC','CUS-BAPA','CUS-BAPB','CUS-BAPB2','CUS-BAWA','CUS-BAXA','CUS-C907','CUS-C910','CUS-CHIT','CUS-CMIL','CUS-CPF','CUS-ECUS','CUS-GLP','CUS-GX39','CUS-M','CUS-PTUB','CUS-T','CUS-V','EJA-GALN','EJA-POLC','EJA-REF','EYP-OFIC','FLO-A','FLO-C','FLO-CPF','FLO-I','FLO-PAB1','FLO-PAJ','FLO-PAM','FLO-T','FLO-U','HUI-BALC','HUI-BRIS','HUI-CAL','HUI-CDIN','HUI-CEBU','HUI-CEIN','HUI-CEIS','HUI-DNOR','HUI-GASD','HUI-ISLI','HUI-JAGU','HUI-LOML','HUI-MON','HUI-NVA','HUI-PIAT','HUI-SATE','HUI-SBDI','HUI-STCL','HUI-TECO','HUI-TELL','HUI-TERC','HUI-USO','HUI-YAGR','LCI-BT23','LCI-BT50','LCI-CENT','LCI-LC01','LCI-LC02','LCI-LC03','LCI-LC04','LCI-LC05','LCI-LC06','LCI-LC07','LCI-LC3A','LCI-LC6A','LCI-LCP3','LCI-LCP5','LCI-LCP6','LCI-SC22','LCI-SC38','LIZ-CENT','LIZ-DESH','LIZ-SAT','LIZ-SOL','LIZ-TES','MAG-TMPC','MET-API','MET-CORO','NAR-ALIS','NAR-PARA','NAR-TMT','NST-BVRO','NST-ORIP','NST-ORU','NST-SAMR','NST-TOLE','PRO-BONA','PRO-CBON','PRO-OFIC','PRO-SANT','PRO-SROQ','PRO-SUER','PRO-TISQ','PUT-BAT1','PUT-BAT2','PUT-BCHU','PUT-BCOL','PUT-BSUC','PUT-CARI','PUT-CORI','PUT-GUAM','PUT-HORM','PUT-LORO','PUT-MANY','PUT-OFIC','PUT-ORIT','PUT-PIA','PUT-QUIL','PUT-SATE','PUT-ZIND','REC-LIYR','REC-LIYT','REC-LIYW','REC-LIYZ','REC-VOLA','REC-VOLC','RIS-PEIR','RUB-BAT1','RUB-BAT3','RUB-BAUP','RUB-CARR','RUB-CBAN','RUB-CDM','RUB-CL','RUB-CMLL','RUB-CNAM','RUB-COE','RUB-CPF1','RUB-CPF2','RUB-EBR','RUB-EDS','RUB-HOTE','RUB-IPP','RUB-MORL','RUB-PAD2','RUB-PAD3','RUB-PAD4','RUB-PAD5','RUB-PAD6','RUB-PAD7','RUB-PAD8','RUB-PALS','STD-CAL','STD-CHIM','STD-ICP','STD-LABE','STD-SEBT','STD-STAR','STD-USO','SUC-TMC1','SUC-TMC2','TIB-AERO','TIB-EREF','TIB-I21','TIB-J10','TIB-J25','TIB-K27','TIB-K32','TIB-L29','TIB-M14','TIB-M24','TIB-M30','TIB-OFIC','TIB-PGAS','TIB-SARN','TIB-SARS','TIB-ZIND','TOL-FRES','TOL-GUAL','TOL-HERV','TOL-MARQ','VAL-BUGC','VAL-BUNV','VAL-CART','VAL-DAGU','VAL-MULC','VAL-OFIC','VAL-YUMB','VVC-OFIC'))
            piso = random.randint(1,10)
            
            if (tipo_espacio_id == 1):
                espacio = 'Sala de reuniones'
                capacidad = random.randint(2, 10)
                pass
            if (tipo_espacio_id == 2):
                espacio = 'Puesto de trabajo multiple'
                capacidad = random.randint(2, 5)
                pass
            if (tipo_espacio_id == 3):
                espacio = 'Puesto de trabajo individual'
                capacidad = 1
                pass
            if (tipo_espacio_id == 4):
                espacio = 'Oficina individual'
                capacidad = 1
                pass
            if (tipo_espacio_id == 5):
                espacio = 'Oficina para equipos'
                capacidad = random.randint(2, 10)
                pass
            if (tipo_espacio_id == 6):
                espacio = 'Auditorio'
                capacidad = random.randrange(50, 100, 10)
                pass
            if (tipo_espacio_id == 7):
                espacio = 'Area de reuniones'
                capacidad = random.randint(2, 10)
                pass
            
            
            # firstName = fkr.first_name()
            # fullname = firstName + ' ' + lastName
            # username = "%s%s" % (firstName, lastName)
            # username = unidecode(username.lower())
            # email = username + '@gmail.com'
            # token = uuid.uuid4()
            
            print("espacio %s" % espacio)
            
            new_space = Espacio(
                espacio = espacio,
                tipo_espacio_id = tipo_espacio_id,
                tipo_disponibilidad_id = tipo_disponibilidad_id,
                instalacion_id = instalacion_id,
                piso = piso,
                capacidad = capacidad
            )
            
            print("Adding space: %s" % new_space)
            db.session.add(new_space)
            db.session.commit()
        
    def get_espacios_by_instalacion(instalacion):
        """Consultar los espacios  que pertenecen a una instalacion

        Args:
            instalacion ([str]): [Instalacion a consultar]

        Returns:
            [SQLalchemy object]: [espacios que pertenecen a una instalacion]

        """
        instalacion = "%{}%".format(instalacion)
        return Espacio.query.filter(Espacio.instalacion_id.like(instalacion)).all()

    def get_espacios_by_disponibilidad(disponibilidad_id):
        """Consultar los espacios  que pertenecen a una instalacion

        Args:
            disponibilidad_id ([int]): [Tipo de disponibilidad a consultar]

        Returns:
            [SQLalchemy object]: [espacios que tienen una disponibilidad determinada]

        """
        return Espacio.query.filter(Espacio.disponibilidad_id == disponibilidad_id).all()
    
    def get_espacios_by_tipo(tipo_espacio_id):
        """Consultar los espacios  que pertenecen a un tipo de espacio

        Args:
            disponibilidad_id ([int]): [Tipo de espacio a consultar]

        Returns:
            [SQLalchemy object]: [espacios que tienen un tipo de espacio determinado]

        """
        return Espacio.query.filter(Espacio.tipo_espacio_id == tipo_espacio_id).all()
    
    def get_espacios_by_capacidad(capacidad):
        """Consultar los espacios  que pertenecen a un tipo de espacio

        Args:
            disponibilidad_id ([int]): [Tipo de espacio a consultar]

        Returns:
            [SQLalchemy object]: [espacios que tienen un tipo de espacio determinado]

        """
        return Espacio.query.filter(Espacio.capacidad == capacidad).all()

    def get_espacios_by_min_capacidad(capacidad):
        """Consultar los espacios  que pertenecen a un tipo de espacio

        Args:
            disponibilidad_id ([int]): [Tipo de espacio a consultar]

        Returns:
            [SQLalchemy object]: [espacios que tienen un tipo de espacio determinado]

        """
        return Espacio.query.filter(Espacio.capacidad <= capacidad).all()

    def __repr__(self):
        return f'<Espacio {self.espacio!r}>'
        
@dataclass
class Region(db.Model):
    """Tabla parametrica para almacenar las regionales de la organizacion

    Attributes:
        id ([int]): [Llave principal auto incremental]
        descripcion ([str]): Nombre de la regional
        sigla ([str]): Nemonico de la regional
        
        ciudades : relationship
            Obtiene las ciudades relacionadas con una regional (sin importar si hay o no biometrico instalado)
            
    """
    __tablename__ = 'region'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50))
    sigla = Column(String(15))
    ecopass = Column(Boolean)
    ecopass_email = Column(Boolean)
    validacion_email = Column(Boolean)
    verifica_tapabocas = Column(Boolean)
    # ciudades = relationship('Ubicacion', backref='Region', 
                                # primaryjoin='Region.id == Ubicacion.region_id')
    # ubicaciones = relationship('Ubicacion', backref='Region',
    #                           primaryjoin='Region.id == Ubicacion.region_id',sync_backref=False)
    
    def __init__(self, descripcion=None, sigla=None, ecopass=None, ecopass_email=None, validacion_email=None, verifica_tapabocas=None):
        self.descripcion = descripcion
        self.sigla = sigla
        self.ecopass = ecopass
        self.ecopass_email = ecopass_email
        self.validacion_email = validacion_email
        self.verifica_tapabocas = verifica_tapabocas
        pass

    def get_ciudades_by_regional_name(regional):
        """Consultar las ciudades que pertenecen a una regional,  usando como filtro el nombre de la regional

        Args:
            regional ([str]): [Nombre de la Regional a consultar]

        Returns:
            [SQLalchemy object]: [ciudades que pertenecen a una regional,  usando como filtro el nombre de la regional]

        """
        regional = '%' + regional + '%'
        return Region.query.with_entities(Region.ciudades).filter(Region.descripcion.like(regional)).all()
    
    def get_ciudades_by_regional_sigla(sigla):
        """Consultar las ciudades que pertenecen a una regional,  usando como filtro el nemonico de la regional

        Args:
            regional ([str]): [Nemonico de la Regional a consultar]

        Returns:
            [SQLalchemy object]: [ciudades que pertenecen a una regional,  usando como filtro el nemonico de la regional]
        
        """
        sigla = '%' + sigla + '%'
        return Region.query.filter(Region.sigla.like(sigla)).all()
    
    def get_ubicaciones_by_regional_sigla(sigla):
        """Consultar las ubicaciones que pertenecen a una regional,  usando como filtro el nemonico de la regional

        Args:
            regional ([str]): [Nemonico de la Regional a consultar]

        Returns:
            [SQLalchemy object]: [ubicaciones que pertenecen a una regional,  usando como filtro el nemonico de la regional]
        
        """
        sigla = '%' + sigla + '%'
        regiones = Region.query.filter(Region.sigla.like(sigla)).all()
        return regiones
    
    def get_ubicaciones_by_regional_id(region):
        """Consultar las ubicaciones que pertenecen a una regional,  usando como filtro el nemonico de la regional

        Args:
            regional ([str]): [Nemonico de la Regional a consultar]

        Returns:
            [SQLalchemy object]: [ubicaciones que pertenecen a una regional,  usando como filtro el nemonico de la regional]
        
        """

        regiones = Region.query.filter(Region.id == region).all()
        return regiones
    
    def get_regiones_settings():
        return Region.query.all()
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return  {
            'id': self.id,
            'description': self.descripcion,
            'sigla': self.sigla
        }
    
    def seed():
        db.session.add(Region('REGIONAL CARIBE','CARIBE',0,0,0,1))
        db.session.add(Region('REGIONAL CENTRAL','VRC',0,0,0,1))
        db.session.add(Region('REGIONAL ANDINA ORIENTE','VAO-ORIENTE',0,0,0,1))
        db.session.add(Region('REGIONAL ANDINA SUR','VAO-SUR',0,0,0,1))
        db.session.add(Region('REGIONAL PIEDEMONTE','VPI',0,0,0,1))
        db.session.add(Region('REGIONAL ORINOQUIA','VRO',0,0,0,1))
        db.session.add(Region('ANDINA SABANA OCCIDENTE','CENIT',0,0,0,1))
        db.session.add(Region('BOGOTA','BOGOTA',0,0,0,1))
        db.session.commit()
    
    def __repr__(self):
        return f'<Region {self.sigla!r}>'
    
    
    

@dataclass
class Ubicacion(db.Model):
    """Tabla parametrica para almacenar las ubicaciones (ciudaes / campos etc) de la organizacion

    Attributes:
        id ([int]): [Llave principal auto incremental]
        ubicacion ([str]): Nombre de la ubicacion
        sigla ([str]): Nemonico de la ubicacion
        region_id ([int]): Llave foranea para relacionar la ubicacion con la regional
        
        ciudades : relationship
            Obtiene las ciudades relacionadas con una regional (sin importar si hay o no biometrico instalado)
            
    """
    __tablename__ = 'ubicacion'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    ubicacion = Column(String(50))
    sigla = Column(String(5))
    region_id = Column(Integer, ForeignKey('Acceso.region.id'))
    instalaciones = relationship('Instalation', backref='Instalation', 
                                primaryjoin='Ubicacion.id == Instalation.ubicacion_id')

    
    def __init__(self, id=None, ubicacion=None, sigla=None, region_id=None):
        self.ubicacion = ubicacion
        self.sigla = sigla
        self.region_id = region_id
    
    def get_ciudades_by_regional(regional_id):
        region_id = Region.query.filter(Region.sigla == regional_id).first()
        return Ubicacion.query.filter(Ubicacion.region_id == region_id.id).all()
    
    def seed():
        db.session.add(Ubicacion( 1,'CARTAGENA','CTG',1))
        db.session.add(Ubicacion( 2,'BOLIVAR','BOL',1))
        db.session.add(Ubicacion( 3,'CORDOBA','COR',1))
        db.session.add(Ubicacion( 4,'SUCRE','SUC',1))
        db.session.add(Ubicacion( 5,'MAGDALENA','MAG',1))
        db.session.add(Ubicacion( 6,'ATLANTICO','ATL',1))
        db.session.add(Ubicacion( 7,'CESAR','CES',1))
        db.session.add(Ubicacion( 8,'CANTAGALLO','CNG',2))
        db.session.add(Ubicacion( 9,'CASABE','CSB',2))
        db.session.add(Ubicacion(10,'SANTANDER','STD',2))
        db.session.add(Ubicacion(11,'LA CIRA','LCI',2))
        db.session.add(Ubicacion(12,'BARRANCABERMEJA','EJA',2))
        db.session.add(Ubicacion(13,'LIZAMA','LIZ',2))
        db.session.add(Ubicacion(14,'PROVINCIA','PRO',2))
        db.session.add(Ubicacion(15,'ARAUCA','ARA',2))
        db.session.add(Ubicacion(16,'CUCUTA','CUC',2))
        db.session.add(Ubicacion(17,',NST',2))
        db.session.add(Ubicacion(18,'TIBU','TIB',2))
        db.session.add(Ubicacion(19,'BOYACA','BOY',2))
        db.session.add(Ubicacion(20,'CAMPO RUBIALES','RUB',3))
        db.session.add(Ubicacion(21,'CAÑO SUR','CSE',3))
        db.session.add(Ubicacion(22,'HUILA','HUI',4))
        db.session.add(Ubicacion(23,'PUTUMAYO','PUT',4))
        db.session.add(Ubicacion(24,'CASANARE','CAS',5))
        db.session.add(Ubicacion(25,'YOPAL','EYP',5))
        db.session.add(Ubicacion(26,'RECETOR','REC',5))
        db.session.add(Ubicacion(27,'CUPIAGUA','CUP',5))
        db.session.add(Ubicacion(28,'CUSIANA','CUS',5))
        db.session.add(Ubicacion(29,'FLOREÑA','FLO',5))
        db.session.add(Ubicacion(30,'VILLAVICENCIO','VVC',6))
        db.session.add(Ubicacion(31,'META','MET',6))
        db.session.add(Ubicacion(32,'API','API',6))
        db.session.add(Ubicacion(33,'CASTILLA','CAS',6))
        db.session.add(Ubicacion(34,'CHICHIMENE','CHI',6))
        db.session.add(Ubicacion(35,'ANTIOQUIA','ANT',7))
        db.session.add(Ubicacion(36,'BOGOTA CENIT','BOC',7))
        db.session.add(Ubicacion(37,'BOYACA','BOY',7))
        db.session.add(Ubicacion(38,'CALDAS','CAL',7))
        db.session.add(Ubicacion(39,'CUNDINAMARCA','CUN',7))
        db.session.add(Ubicacion(40,'RISARALDA','RIS',7))
        db.session.add(Ubicacion(41,'SANTANDER','STD',7))
        db.session.add(Ubicacion(42,'TOLIMA','TOL',7))
        db.session.add(Ubicacion(43,'VALLE','VAL',7))
        db.session.add(Ubicacion(44,'NARIÑO','NAR',7))
        db.session.add(Ubicacion(45,'BOGOTA','BOG',8))
        db.session.commit()

    def __repr__(self):
        return f'<Ubicacion {self.ubicacion!r}>'

@dataclass
class Instalation(db.Model):
    __tablename__ = 'instalacion'
    __table_args__ = {"schema": "Acceso"}
    instalacion = Column(String(50))
    sigla = Column(String(5))
    ubicacion_id = Column(Integer, ForeignKey('Acceso.ubicacion.id'))
    nemonico = Column(String(50), primary_key=True)
    ecopass_tiempo = Column(Boolean, default=False)
    ecopass_instalacion = Column(Boolean, default=False)
    ecopass_email = Column(Boolean, default=False)
    validacion_email = Column(Boolean, default=False)
    verifica_tapabocas = Column(Boolean, default=True)
    email = Column(String(100))
    
    ubicacion_id = Column(Integer, ForeignKey('Acceso.ubicacion.id'))
    ubicacion = relationship('Ubicacion', backref='Instalation',  
                             primaryjoin='Ubicacion.id == Instalation.ubicacion_id', viewonly=True, sync_backref=False)
    
    espacios = relationship('Espacio', backref='Instalation',
                            primaryjoin='Espacio.instalacion_id == Instalation.nemonico', viewonly=True, sync_backref=False)
    # ubicacion = relationship('Ubicacion', backref='Instalation', 
    #                             primaryjoin='Ubicacion.id == Instalation.ubicacion_id')
    
    def __init__(self, instalacion=None, sigla=None, ubicacion_id = None,  nemonico=None, ecopass_tiempo=None, ecopass_instalacion=None,ecopass_email=None, validacion_email=None, verifica_tapabocas=None, email=None):
        self.instalacion = instalacion
        self.sigla = sigla
        self.ubicacion_id = ubicacion_id
        self.nemonico = nemonico
        self.ecopass_tiempo = ecopass_tiempo
        self.ecopass_instalacion = ecopass_instalacion
        self.ecopass_email = ecopass_email
        self.validacion_email = validacion_email
        self.verifica_tapabocas = verifica_tapabocas
        self.email = email
        
    
    def get_instalaciones_by_ubicacion_sigla(sigla):
        sigla = '%' + sigla + '%'
        ubi_id = Ubicacion.query.filter(Ubicacion.sigla.like(sigla)).first()
        return Instalation.query.filter(Instalation.ubicacion_id == ubi_id.id).all()
    
    def get_instalaciones_by_ubicacion_id(ubicacion_id):
        instalaciones = Instalation.query.filter(Instalation.ubicacion_id == ubicacion_id).all()        
        return instalaciones

        
    def get_instalaciones_by_ubicacion(ubicacion):
        ubicacion = '%' + ubicacion + '%'
        ubi_id = Ubicacion.query.filter(Ubicacion.ubicacion.like(ubicacion)).first()
        if ubi_id is not None:
            return Instalation.query.filter(Instalation.ubicacion_id == ubi_id.id).all()
        else:
            return None
    
    def get_instalaciones_settings():
        return Instalation.query.all()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def seed():
        db.session.add(Instalation('ESTACIÓN CAUCASIA','CAUC',35,'ANT-CAUC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CISNEROS','CISN',35,'ANT-CISN',0,0,0,0,1,''))
        db.session.add(Instalation('CASETA DE MARCACIÓN GIRARDOTA','GIRC',35,'ANT-GIRC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN MEDELLÍN','MEDN',35,'ANT-MEDN',0,0,0,0,0,''))
        db.session.add(Instalation('CASETA DE MARCACIÓN LA PINTADA','PINC',35,'ANT-PINC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CHIQUILLO','REME',35,'ANT-REME',0,0,0,0,1,''))
        db.session.add(Instalation('CLÚSTER','CL',32,'API-CL',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ERA','ERA',32,'API-ERA',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN GAS Y ASFALTO','GYAS',32,'API-GYAS',0,0,0,0,1,''))
        db.session.add(Instalation('INTERSECCIÓN VIAL','IV',32,'API-IV',0,0,0,0,1,''))
        db.session.add(Instalation('APIAY OFICINAS ADMINISTRATIVAS','OFIC',32,'API-OFIC',0,0,0,0,1,''))
        db.session.add(Instalation('POZO','PZ',32,'API-PZ',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN REFORMA','REFM',32,'API-REFM',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SURIA','SURI',32,'API-SURI',0,0,0,0,1,''))
        db.session.add(Instalation('TERMOELÉCTRICA OCOA','TOCO',32,'API-TOCO',0,0,0,0,1,''))
        db.session.add(Instalation('TERMOELÉCTRICA SURIA','TSUR',32,'API-TSUR',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN BANADÍA','BAND',15,'ARA-BAND',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN BARANOA','BARN',6,'ATL-BARN',0,0,0,0,1,''))
        db.session.add(Instalation('EDIFICIO 13-35','1335',45,'BOG-1335',0,0,0,0,1,''))
        db.session.add(Instalation('EDIFICIO AMADEUS','AMAD',45,'BOG-AMAD',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN PUENTE ARANDA','ARND',45,'BOG-ARND',0,0,0,0,1,''))
        db.session.add(Instalation('EDIFICIO CAXDAC','CAXD',45,'BOG-CAXD',0,0,0,0,1,''))
        db.session.add(Instalation('EDIFICIO PRINCIPAL','PPAL',45,'BOG-PPAL',0,0,0,0,1,'recepprincipal@ecopetrol.com.co'))
        db.session.add(Instalation('EDIFICIO TORRE AR','TAR',45,'BOG-TAR',0,0,0,0,1,'recepciontorrearp10@ecopetrol.com.co'))
        db.session.add(Instalation('EDIFICIO TEUSACÁ','TEUS',45,'BOG-TEUS',0,0,0,0,1,'recepteusaca@ecopetrol.com.co'))
        db.session.add(Instalation('ESTACIÓN EL RETIRO','RET',2,'BOL-RET',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN MIRAFLORES','EMIR',37,'BOY-EMIR',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN MIRAFLORES','MIRF',37,'BOY-MIRF',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN PÁEZ','PAEZ',37,'BOY-PAEZ',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SUTAMARCHÁN','SUTA',37,'BOY-SUTA',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN VASCONIA','VASC',19,'BOY-VASC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN MANIZALES','MANZ',38,'CAL-MANZ',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ALTOS DE PORVENIR','APOR',24,'CAS-APOR',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ARAGUANEY','ARGY',24,'CAS-ARGY',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE CONTROL Y MANIOBRA - CCM4','CCM4',33,'CAS-CCM4',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE DISTRIBUCIÓN SAN FERNANDO - CDF','CDF',33,'CAS-CDF',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE DISTRIBUCIÓN ACACÍAS - CDK','CDK',33,'CAS-CDK',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE DISTRIBUCIÓN MÓVIL - CDM','CDM',33,'CAS-CDM',0,0,0,0,1,''))
        db.session.add(Instalation('CLÚSTER','CL',33,'CAS-CL',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE MANIOBRAS ACACÍAS - CMA','CMA',33,'CAS-CMA',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE MANIOBRA Y DISTRIBUCIÓN - CMD','CMD',33,'CAS-CMD',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE MANIOBRAS TRONCAL - CMT','CMT',33,'CAS-CMT',0,0,0,0,1,''))
        db.session.add(Instalation('DISPOSAL 1','DIS1',33,'CAS-DIS1',0,0,0,0,1,''))
        db.session.add(Instalation('DISPOSAL 3','DIS3',33,'CAS-DIS3',0,0,0,0,1,''))
        db.session.add(Instalation('DISPOSAL 4','DIS4',33,'CAS-DIS4',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ACACÍAS','EAK',33,'CAS-EAK',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CASTILLA 1','EC1',33,'CAS-EC1',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CASTILLA 2','EC2',33,'CAS-EC2',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CASTILLA 3','EC3',33,'CAS-EC3',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN PORVENIR','EPOR',24,'CAS-EPOR',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CAMPO SANTIAGO','ESAN',24,'CAS-ESAN',0,0,0,0,1,''))
        db.session.add(Instalation('INTERSECCIÓN VIAL','IV',33,'CAS-IV',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN JAGUEY','JAGU',24,'CAS-JAGU',0,0,0,0,1,''))
        db.session.add(Instalation('EL JARDÍN','JARD',33,'CAS-JARD',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN MONTERREY','MONT',24,'CAS-MONT',0,0,0,0,1,''))
        db.session.add(Instalation('CASTILLA OFICINAS ADMINISTRATIVAS','OFIC',33,'CAS-OFIC',0,0,0,0,1,''))
        db.session.add(Instalation('POZO','PZ',33,'CAS-PZ',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SAN FERNANDO','SFER',33,'CAS-SFER',0,0,0,0,1,''))
        db.session.add(Instalation('VÁLVULA VERTIMIENTO K10','VK10',33,'CAS-VK10',0,0,0,0,1,''))
        db.session.add(Instalation('VÁLVULA VERTIMIENTO K22','VK22',33,'CAS-VK22',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN AYACUCHO','AYAC',7,'CES-AYAC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN EL COPEY','COPY',7,'CES-COPY',0,0,0,0,1,''))
        db.session.add(Instalation('BODEGA DE MATERIALES (CLÚSTER 48)','BMAT',34,'CHI-BMAT',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE DISTRIBUCIÓN OROTOY - CDO','CDO',34,'CHI-CDO',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CHICHIMENE','CHIC',34,'CHI-CHIC',0,0,0,0,1,''))
        db.session.add(Instalation('CLÚSTER','CL',34,'CHI-CL',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE MANIOBRA TRONCAL NORTE - CMTN','CMTN',34,'CHI-CMTN',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE MANIOBRA TRONCAL OESTE - CMTO','CMTO',34,'CHI-CMTO',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE MANIOBRA TRONCAL SUR - CMTS','CMTS',34,'CHI-CMTS',0,0,0,0,1,''))
        db.session.add(Instalation('CENTRO DE MANIOBRA VAQUEROS - CMVQ','CMVQ',34,'CHI-CMVQ',0,0,0,0,1,''))
        db.session.add(Instalation('INTERSECCIÓN VIAL','IV',34,'CHI-IV',0,0,0,0,1,''))
        db.session.add(Instalation('PLANTA DE DESASFALTADO','PDES',34,'CHI-PDES',0,0,0,0,1,''))
        db.session.add(Instalation('GCH PIAR (CLÚSTER 46)','PIAR',34,'CHI-PIAR',0,0,0,0,1,''))
        db.session.add(Instalation('PATIO DE TUBERÍAS','PTUB',34,'CHI-PTUB',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CRISTALINAS','CRIS',8,'CNG-CRIS',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN AUXILIAR','EAUX',8,'CNG-EAUX',0,0,0,0,1,''))
        db.session.add(Instalation('ECOBODEGAS','ECOB',8,'CNG-ECOB',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN GARZAS','GARZ',8,'CNG-GARZ',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ISLA I','ISI',8,'CNG-ISI',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ISLA IV','ISIV',8,'CNG-ISIV',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ISLA V','ISV',8,'CNG-ISV',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ISLA VI','ISVI',8,'CNG-ISVI',0,0,0,0,1,''))
        db.session.add(Instalation('ZONA INDUSTRIAL CANTAGALLO','ZIND',8,'CNG-ZIND',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LA GRANJITA','GRAN',3,'COR-GRAN',0,0,0,0,1,''))
        db.session.add(Instalation('TERMINAL MARÍTIMO COVEÑAS','TMC',3,'COR-TMC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CONDOR CASABE','CNDR',9,'CSB-CNDR',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN 2','EST2',9,'CSB-EST2',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN 3','EST3',9,'CSB-EST3',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN 4','EST4',9,'CSB-EST4',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN 5','EST5',9,'CSB-EST5',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CASABE SUR','ESTS',9,'CSB-ESTS',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN PEÑAS BLANCAS','PEÑB',9,'CSB-PEÑB',0,0,0,0,1,''))
        db.session.add(Instalation('PIA CASABE','PIA',9,'CSB-PIA',0,0,0,0,1,''))
        db.session.add(Instalation('ZONA INDUSTRIAL CASABE','ZIND',9,'CSB-ZIND',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPAMENTO ANI','CANI',21,'CSE-CANI',0,0,0,0,1,''))
        db.session.add(Instalation('BODEGA CSE08','CSE8',21,'CSE-CSE8',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPAMENTO X14','CX14',21,'CSE-CX14',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPAMENTO X5','CX5',21,'CSE-CX5',0,0,0,0,1,''))
        db.session.add(Instalation('EP1','EP1',21,'CSE-EP1',0,0,0,0,1,''))
        db.session.add(Instalation('MITO 1','MIT1',21,'CSE-MIT1',0,0,0,0,1,''))
        db.session.add(Instalation('MITO 2','MIT2',21,'CSE-MIT2',0,0,0,0,1,''))
        db.session.add(Instalation('PAD 2','PAD2',21,'CSE-PAD2',0,0,0,0,1,''))
        db.session.add(Instalation('EDIFICIO HUB CARIBE','EVIP',1,'CTG-EVIP',0,0,0,0,1,''))
        db.session.add(Instalation('TERMINAL MARÍTIMO REFINERÍA DE CARTAGENA','MREF',1,'CTG-MREF',0,0,0,0,1,''))
        db.session.add(Instalation('TERMINAL MARÍTIMO NÉSTOR PINEDA','MTNP',1,'CTG-MTNP',0,0,0,0,1,''))
        db.session.add(Instalation('REFINERÍA DE CARTAGENA','REF',1,'CTG-REF',0,0,0,0,1,''))
        db.session.add(Instalation('ÁREA TANQUES NÉSTOR PINEDA','TTNP',1,'CTG-TTNP',0,0,0,0,1,''))
        db.session.add(Instalation('USO CARTAGENA','USO',1,'CTG-USO',0,0,0,0,1,''))
        db.session.add(Instalation('CÚCUTA OFICINAS ADMINISTRATIVAS','OFIC',16,'CUC-OFIC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ALBÁN','ALB',39,'CUN-ALB',0,0,0,0,1,''))
        db.session.add(Instalation('CCO MANSILLA','CCO',39,'CUN-CCO',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN GUADUERO','GUAD',39,'CUN-GUAD',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN MANSILLA','MANS',39,'CUN-MANS',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN PUERTO SALGAR','PSLG',39,'CUN-PSLG',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN TOCANCIPÁ','TOCA',39,'CUN-TOCA',0,0,0,0,1,''))
        db.session.add(Instalation('USO PUERTO SALGAR','USO',39,'CUN-USO',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN VILLETA','VILL',39,'CUN-VILL',0,0,0,0,1,''))
        db.session.add(Instalation('CPF CUPIAGUA','CPF',27,'CUP-CPF',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CUPIAGUA','ECUP',27,'CUP-ECUP',0,0,0,0,1,''))
        db.session.add(Instalation('CUPIAGUA H','H',27,'CUP-H',0,0,0,0,1,''))
        db.session.add(Instalation('CUPIAGUA K','K',27,'CUP-K',0,0,0,0,1,''))
        db.session.add(Instalation('CUPIAGUA NW','NW',27,'CUP-NW',0,0,0,0,1,''))
        db.session.add(Instalation('PATIO DE TUBERIA','PTUB',27,'CUP-PTUB',0,0,0,0,1,''))
        db.session.add(Instalation('CUPIAGUA T','T',27,'CUP-T',0,0,0,0,1,''))
        db.session.add(Instalation('VÁLVULA KM 12','VK12',27,'CUP-VK12',0,0,0,0,1,''))
        db.session.add(Instalation('VÁLVULA KM 26','VK26',27,'CUP-VK26',0,0,0,0,1,''))
        db.session.add(Instalation('VÁLVULA KM 8','VK8',27,'CUP-VK8',0,0,0,0,1,''))
        db.session.add(Instalation('CUPIAGUA XH','XH',27,'CUP-XH',0,0,0,0,1,''))
        db.session.add(Instalation('CUPIAGUA XL','XL',27,'CUP-XL',0,0,0,0,1,''))
        db.session.add(Instalation('CUPIAGUA YD','YD',27,'CUP-YD',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA X11','BA11',28,'CUS-BA11',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA X14','BA14',28,'CUS-BA14',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA G','BAG',28,'CUS-BAG',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA GC','BAGC',28,'CUS-BAGC',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA PA36','BAPA',28,'CUS-BAPA',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA PB26','BAPB',28,'CUS-BAPB',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA PB28','BAPB',28,'CUS-BAPB2',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA WA','BAWA',28,'CUS-BAWA',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA XA30','BAXA',28,'CUS-BAXA',0,0,0,0,1,''))
        db.session.add(Instalation('CERRO 907','C907',28,'CUS-C907',0,0,0,0,1,''))
        db.session.add(Instalation('CERRO 910','C910',28,'CUS-C910',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA CHITAMENA','CHIT',28,'CUS-CHIT',0,0,0,0,1,''))
        db.session.add(Instalation('CERRO 1000','CMIL',28,'CUS-CMIL',0,0,0,0,1,''))
        db.session.add(Instalation('CPF CUSIANA','CPF',28,'CUS-CPF',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CUSIANA','ECUS',28,'CUS-ECUS',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA LLENADERO GLP','GLP',28,'CUS-GLP',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA BA GX39','GX39',28,'CUS-GX39',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA M','M',28,'CUS-M',0,0,0,0,1,''))
        db.session.add(Instalation('PATIO DE TUBERIA','PTUB',28,'CUS-PTUB',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA T','T',28,'CUS-T',0,0,0,0,1,''))
        db.session.add(Instalation('CUSIANA V','V',28,'CUS-V',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN GALÁN','GALN',12,'EJA-GALN',0,0,0,0,1,''))
        db.session.add(Instalation('POLICLÍNICA','POLC',12,'EJA-POLC',0,0,0,0,1,''))
        db.session.add(Instalation('REFINERÍA DE BARRANCABERMEJA','REF',12,'EJA-REF',0,0,0,0,1,''))
        db.session.add(Instalation('YOPAL OFICINAS ADMINISTRATIVAS','OFIC',25,'EYP-OFIC',0,0,0,0,1,''))
        db.session.add(Instalation('FLOREÑA A','A',29,'FLO-A',0,0,0,0,1,''))
        db.session.add(Instalation('FLOREÑA C','C',29,'FLO-C',0,0,0,0,1,''))
        db.session.add(Instalation('CPF FLOREÑA','CPF',29,'FLO-CPF',0,0,0,0,1,''))
        db.session.add(Instalation('FLOREÑA I','I',29,'FLO-I',0,0,0,0,1,''))
        db.session.add(Instalation('PAUTO SB1','PAB1',29,'FLO-PAB1',0,0,0,0,1,''))
        db.session.add(Instalation('PAUTO J','PAJ',29,'FLO-PAJ',0,0,0,0,1,''))
        db.session.add(Instalation('PAUTO M','PAM',29,'FLO-PAM',0,0,0,0,1,''))
        db.session.add(Instalation('FLOREÑA T','T',29,'FLO-T',0,0,0,0,1,''))
        db.session.add(Instalation('FLOREÑA U','U',29,'FLO-U',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA BALCÓN','BALC',22,'HUI-BALC',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA BRISAS','BRIS',22,'HUI-BRIS',0,0,0,0,1,''))
        db.session.add(Instalation('CAL NEIVA','CAL',22,'HUI-CAL',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPO DINA','CDIN',22,'HUI-CDIN',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA CEBÚ PIA','CEBU',22,'HUI-CEBU',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA RIO CEIBAS NORTE','CEIN',22,'HUI-CEIN',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA RIO CEIBAS SUR','CEIS',22,'HUI-CEIS',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA DINA NORTE','DNOR',22,'HUI-DNOR',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA PLANTA GAS DINA','GASD',22,'HUI-GASD',0,0,0,0,1,''))
        db.session.add(Instalation('LOCACIÓN ISLA I - RIO CEIBAS','ISLI',22,'HUI-ISLI',0,0,0,0,1,''))
        db.session.add(Instalation('LA JAGUA','JAGU',22,'HUI-JAGU',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA LOMALARGA','LOML',22,'HUI-LOML',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA MONAL SAN FRANCISCO','MON',22,'HUI-MON',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN NEIVA','NVA',22,'HUI-NVA',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA PIA TERCIARIOS','PIAT',22,'HUI-PIAT',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA SATÉLITE','SATE',22,'HUI-SATE',0,0,0,0,1,''))
        db.session.add(Instalation('SUBESTACIÓN ELÉCTRICA DINA','SBDI',22,'HUI-SBDI',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA SANTA CLARA','STCL',22,'HUI-STCL',0,0,0,0,1,''))
        db.session.add(Instalation('PATIO TUBERÍA ECOBODEGAS','TECO',22,'HUI-TECO',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA TELLO','TELL',22,'HUI-TELL',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA TERCIARIOS','TERC',22,'HUI-TERC',0,0,0,0,1,''))
        db.session.add(Instalation('USO NEIVA','USO',22,'HUI-USO',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA LOS MANGOS - YAGUARÁ','YAGR',22,'HUI-YAGR',0,0,0,0,1,''))
        db.session.add(Instalation('BOCATOMA CAMPO 23 LA CIRA','BT23',11,'LCI-BT23',0,0,0,0,1,''))
        db.session.add(Instalation('BOCATOMA CAMPO 50 LA CIRA','BT50',11,'LCI-BT50',0,0,0,0,1,''))
        db.session.add(Instalation('COMPLEJO EL CENTRO','CENT',11,'LCI-CENT',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LCI-1','LC01',11,'LCI-LC01',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LCI-2','LC02',11,'LCI-LC02',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LCI-3','LC03',11,'LCI-LC03',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LCI-4','LC04',11,'LCI-LC04',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LCI-5','LC05',11,'LCI-LC05',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LCI-6','LC06',11,'LCI-LC06',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LCI-7','LC07',11,'LCI-LC07',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN 3A LA CIRA','LC3A',11,'LCI-LC3A',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LCI-6A','LC6A',11,'LCI-LC6A',0,0,0,0,1,''))
        db.session.add(Instalation('PIA 3 LA CIRA','LCP3',11,'LCI-LCP3',0,0,0,0,1,''))
        db.session.add(Instalation('PIA 5 y PIA 5A','LCP5',11,'LCI-LCP5',0,0,0,0,1,''))
        db.session.add(Instalation('PIA 6 LA CIRA','LCP6',11,'LCI-LCP6',0,0,0,0,1,''))
        db.session.add(Instalation('SUB ESTACIÓN ELÉCTRICA CAMPO 22','SC22',11,'LCI-SC22',0,0,0,0,1,''))
        db.session.add(Instalation('SUB ESTACIÓN ELÉCTRICA CAMPO 38','SC38',11,'LCI-SC38',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LIZAMA','CENT',13,'LIZ-CENT',0,0,0,0,1,''))
        db.session.add(Instalation('PLANTA DESHIDRATADORA LIZAMA','DESH',13,'LIZ-DESH',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SATÉLITE','SAT',13,'LIZ-SAT',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SOL','SOL',13,'LIZ-SOL',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN TESORO','TES',13,'LIZ-TES',0,0,0,0,1,''))
        db.session.add(Instalation('TERMINAL MARÍTIMO POZOS COLORADOS','TMPC',5,'MAG-TMPC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CENIT APIAY','API',31,'MET-API',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN COROCORA','CORO',31,'MET-CORO',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ALISALES','ALIS',44,'NAR-ALIS',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN PÁRAMO','PARA',44,'NAR-PARA',0,0,0,0,1,''))
        db.session.add(Instalation('TERMINAL MARÍTIMO TUMACO','TMT',44,'NAR-TMT',0,0,0,0,1,''))
        db.session.add(Instalation('BODEGA VILLA DEL ROSARIO','BVRO',17,'NST-BVRO',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ORIPAYA','ORIP',17,'NST-ORIP',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN ORÚ','ORU',17,'NST-ORU',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SAMORÉ','SAMR',17,'NST-SAMR',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN TOLEDO','TOLE',17,'NST-TOLE',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN BONANZA','BONA',14,'PRO-BONA',0,0,0,0,1,''))
        db.session.add(Instalation('COMPRESORES BONANZA','CBON',14,'PRO-CBON',0,0,0,0,1,''))
        db.session.add(Instalation('PROVINCIA OFICINAS ADMINISTRATIVAS','OFIC',14,'PRO-OFIC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SANTOS','SANT',14,'PRO-SANT',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SAN ROQUE','SROQ',14,'PRO-SROQ',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SUERTE','SUER',14,'PRO-SUER',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN TISQUIRAMA','TISQ',14,'PRO-TISQ',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA 1','BAT1',23,'PUT-BAT1',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA 2','BAT2',23,'PUT-BAT2',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA CHURUYACOS','BCHU',23,'PUT-BCHU',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA COLÓN','BCOL',23,'PUT-BCOL',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA SUCUMBÍOS','BSUC',23,'PUT-BSUC',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA CARIBE','CARI',23,'PUT-CARI',0,0,0,0,1,''))
        db.session.add(Instalation('CERRO ORITO','CORI',23,'PUT-CORI',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN GUAMUEZ','GUAM',23,'PUT-GUAM',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA HORMIGA','HORM',23,'PUT-HORM',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPAMENTO LORO','LORO',23,'PUT-LORO',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN MANSOYÁ','MANY',23,'PUT-MANY',0,0,0,0,1,''))
        db.session.add(Instalation('ORITO OFICINAS ADMINISTRATIVAS Y CAMPAMENTO','OFIC',23,'PUT-OFIC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CENIT ORITO','ORIT',23,'PUT-ORIT',0,0,0,0,1,''))
        db.session.add(Instalation('GPY PIA','PIA',23,'PUT-PIA',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA QUILILI','QUIL',23,'PUT-QUIL',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA SATÉLITE','SATE',23,'PUT-SATE',0,0,0,0,1,''))
        db.session.add(Instalation('ZONA INDUSTRIAL ORITO','ZIND',23,'PUT-ZIND',0,0,0,0,1,''))
        db.session.add(Instalation('RECETOR LIRIA YR','LIYR',26,'REC-LIYR',0,0,0,0,1,''))
        db.session.add(Instalation('RECETOR LIRIA YT','LIYT',26,'REC-LIYT',0,0,0,0,1,''))
        db.session.add(Instalation('RECETOR LIRIA YW','LIYW',26,'REC-LIYW',0,0,0,0,1,''))
        db.session.add(Instalation('RECETOR LIRIA YZ','LIYZ',26,'REC-LIYZ',0,0,0,0,1,''))
        db.session.add(Instalation('RECETOR VOLCANERAS A','VOLA',26,'REC-VOLA',0,0,0,0,1,''))
        db.session.add(Instalation('RECETOR VOLCANERAS C','VOLC',26,'REC-VOLC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN PEREIRA','PEIR',40,'RIS-PEIR',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA 1','BAT1',20,'RUB-BAT1',0,0,0,0,1,''))
        db.session.add(Instalation('BATERÍA 3','BAT3',20,'RUB-BAT3',0,0,0,0,1,''))
        db.session.add(Instalation('BAUPA','BAUP',20,'RUB-BAUP',0,0,0,0,1,''))
        db.session.add(Instalation('COMPLEJO ARRAYANES','CARR',20,'RUB-CARR',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPAMENTO BASE ANTIGUA','CBAN',20,'RUB-CBAN',0,0,0,0,1,''))
        db.session.add(Instalation('CDM','CDM',20,'RUB-CDM',0,0,0,0,1,''))
        db.session.add(Instalation('CLÚSTER','CL',20,'RUB-CL',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPAMENTO MI LLANURA','CMLL',20,'RUB-CMLL',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPAMENTO NUEVO AMANECER','CNAM',20,'RUB-CNAM',0,0,0,0,1,''))
        db.session.add(Instalation('COE','COE',20,'RUB-COE',0,0,0,0,1,''))
        db.session.add(Instalation('CPF1','CPF1',20,'RUB-CPF1',0,0,0,0,1,''))
        db.session.add(Instalation('CPF2','CPF2',20,'RUB-CPF2',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN DE BOMBEO RUBIALES - EBR','EBR',20,'RUB-EBR',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN DE SERVICIO','EDS',20,'RUB-EDS',0,0,0,0,1,''))
        db.session.add(Instalation('HOTEL','HOTE',20,'RUB-HOTE',0,0,0,0,1,''))
        db.session.add(Instalation('IPP','IPP',20,'RUB-IPP',0,0,0,0,1,''))
        db.session.add(Instalation('MORELIA AEROPUERTO','MORL',20,'RUB-MORL',0,0,0,0,1,''))
        db.session.add(Instalation('PAD 2','PAD2',20,'RUB-PAD2',0,0,0,0,1,''))
        db.session.add(Instalation('PAD 3','PAD3',20,'RUB-PAD3',0,0,0,0,1,''))
        db.session.add(Instalation('PAD 4','PAD4',20,'RUB-PAD4',0,0,0,0,1,''))
        db.session.add(Instalation('PAD 5','PAD5',20,'RUB-PAD5',0,0,0,0,1,''))
        db.session.add(Instalation('PAD 6','PAD6',20,'RUB-PAD6',0,0,0,0,1,''))
        db.session.add(Instalation('PAD 7','PAD7',20,'RUB-PAD7',0,0,0,0,1,''))
        db.session.add(Instalation('PAD 8','PAD8',20,'RUB-PAD8',0,0,0,0,1,''))
        db.session.add(Instalation('PATIO ALS','PALS',20,'RUB-PALS',0,0,0,0,1,''))
        db.session.add(Instalation('CAL BUCARAMANGA','CAL',10,'STD-CAL',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CHIMITÁ','CHIM',10,'STD-CHIM',0,0,0,0,1,''))
        db.session.add(Instalation('ICP','ICP',10,'STD-ICP',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN LA BELLEZA','LABE',4,'STD-LABE',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SEBASTOPOL','SEBT',10,'STD-SEBT',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SANTA ROSA','STAR',41,'STD-STAR',0,0,0,0,1,''))
        db.session.add(Instalation('USO BUCARAMANGA','USO',10,'STD-USO',0,0,0,0,1,''))
        db.session.add(Instalation('TERMINAL MARÍTIMO COVEÑAS','TMC1',4,'SUC-TMC1',0,0,0,0,1,''))
        db.session.add(Instalation('TERMINAL MARÍTIMO COVEÑAS','TMC2',4,'SUC-TMC2',0,0,0,0,1,''))
        db.session.add(Instalation('AEROPUERTO ECOPETROL TIBÚ','AERO',18,'TIB-AERO',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN REFINERIA','EREF',18,'TIB-EREF',0,0,0,0,1,''))
        db.session.add(Instalation('CAMPO TIBÚ - I21','I21',18,'TIB-I21',0,0,0,0,1,''))
        db.session.add(Instalation('J-10','J10',18,'TIB-J10',0,0,0,0,1,''))
        db.session.add(Instalation('J-25','J25',18,'TIB-J25',0,0,0,0,1,''))
        db.session.add(Instalation('K-27','K27',18,'TIB-K27',0,0,0,0,1,''))
        db.session.add(Instalation('K-32','K32',18,'TIB-K32',0,0,0,0,1,''))
        db.session.add(Instalation('L-29','L29',18,'TIB-L29',0,0,0,0,1,''))
        db.session.add(Instalation('M-14','M14',18,'TIB-M14',0,0,0,0,1,''))
        db.session.add(Instalation('M-24','M24',18,'TIB-M24',0,0,0,0,1,''))
        db.session.add(Instalation('M-30','M30',18,'TIB-M30',0,0,0,0,1,''))
        db.session.add(Instalation('TIBÚ OFICINAS ADMINISTRATIVAS','OFIC',18,'TIB-OFIC',0,0,0,0,1,''))
        db.session.add(Instalation('PLANTA DE GAS SARDINATA','PGAS',18,'TIB-PGAS',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SARDINATA NORTE','SARN',18,'TIB-SARN',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN SARDINATA SUR','SARS',18,'TIB-SARS',0,0,0,0,1,''))
        db.session.add(Instalation('ZONA INDUSTRIAL TIBÚ','ZIND',18,'TIB-ZIND',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN FRESNO','FRES',42,'TOL-FRES',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN GUALANDAY','GUAL',42,'TOL-GUAL',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN HERVEO','HERV',42,'TOL-HERV',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN MARIQUITA','MARQ',42,'TOL-MARQ',0,0,0,0,1,''))
        db.session.add(Instalation('CASETA DE MARCACIÓN BUGA','BUGC',43,'VAL-BUGC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN BUENAVENTURA','BUNV',43,'VAL-BUNV',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN CARTAGO','CART',43,'VAL-CART',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN DAGUA','DAGU',43,'VAL-DAGU',0,0,0,0,1,''))
        db.session.add(Instalation('CASETA DE MARCACIÓN MULALÓ','MULC',43,'VAL-MULC',0,0,0,0,1,''))
        db.session.add(Instalation('CALI OFICINAS ADMINISTRATIVAS','OFIC',43,'VAL-OFIC',0,0,0,0,1,''))
        db.session.add(Instalation('ESTACIÓN YUMBO','YUMB',43,'VAL-YUMB',0,0,0,0,1,''))
        db.session.add(Instalation('VILLAVICENCIO OFICINAS ADMINISTRATIVAS','OFIC',30,'VVC-OFIC',0,0,0,0,1,''))   
        db.session.commit()
    
    def __repr__(self):
        return f'<Instalation {self.nemonico!r}>'

@dataclass
class Device(db.Model):
    """Clase que contiene la información de los dispositivos biométricos

    Campos:
        id (int): Llave principal autoincremental
        device_id (str): Número serial del dispositivo biométrico
        device_name (str): Nemónico del dispositivo dentro de la estructura de Lenel - Ecopetrol
        lenel_door (str): Nemónico de la puerta lenel asociado con el dispositivo biometrico
        regional (str): Regional  a la que pertenece la instalacion del dispositivo biométrico
        instalacion (str): Edificio o ubicación donde esta instalado el dispositivo biométrico
        ip_addr (str): IP Address del dispositivo biometrico
        latitude (str): Latitud geografía del dispositivo biometrico
        longitude (str): Longitud geografía del dispositivo biometrico
        ubicacion (str): Ciudad o ubicacion dentro de la estructura de organización territorial de Ecopetrol
        last_report (datetime): Ultimo reporte Heartbeat del dispositivo biometrico
        username (str): Username de acceso al dispositivo biometrico
        device_pwd (str): Password de acceso al dispositivo biometrico
        site_id (str): Nemonico del sitio / ubicacion de la instalacion del dispositivo biometrico
        
        device_Lenel (relationship): Datos de la tabla relacionada DeviceLenel
    """
    __tablename__ = 'device'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer)
    device_id = Column(String(50), primary_key=True) 
    device_name = Column(String(100))
    lenel_door = Column(String(50))
    regional = Column(String(50))
    instalacion = Column(String(50))
    ip_addr = Column(String(50))
    latitude = Column(String(50))
    longitude = Column(String(50))
    ubicacion = Column(String(50))
    last_report = Column(DateTime)
    username = Column(String(50))
    device_pwd = Column(String(50))
    site_id = Column(String(50))
    direction = Column(Integer)
    deviceLenel = relationship('DeviceLenel', backref='Device', 
                                primaryjoin='DeviceLenel.device_id == Device.device_id')

    def __init__(self, device_id=None, device_name=None, lenel_door=None, regional=None, instalacion=None, ip_addr=None, latitude=None, longitude=None, ubicacion=None, last_report=None, username=None, device_pwd=None, site_id=None):
        self.device_id = device_id
        self.device_name = device_name
        self.lenel_door = lenel_door
        self.regional = regional
        self.instalacion = instalacion
        self.ip_addr = ip_addr
        self.latitude = latitude
        self.longitude = longitude
        self.ubicacion = ubicacion
        self.last_report = last_report
        self.username = username
        self.device_pwd = device_pwd
        self.site_id = site_id
        
    @staticmethod
    def get_by_serial(device_id):
        return Device.query.filter_by(device_id=device_id).first()

    @staticmethod
    def get_all_by_site_id(site_id):
        site_id = '%' + site_id + '%'
        devices =  Device.query.filter(Device.site_id.like(site_id)).all()
        return devices

    def __repr__(self):
        return f'<Device {self.device_id!r}>'



@dataclass
class Passport(db.Model):
    __tablename__ = 'passport'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    docType_id = Column(String(2))
    numero_doc = Column(String(50))
    ssno = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    start_time = Column(String(50))
    end_time = Column(String(50))
    status = Column(Boolean)
    notes = Column(String(250))
    created = Column(DateTime)
    is_valid = Column(Boolean)
    # sites = relationship('EmployeeSite', backref='passport', 
    #                             primaryjoin='EmployeeSite.passport_id == Passport.id')
    

    def __init__(self,docType_id=None,numero_doc=None,ssno=None,first_name=None,last_name=None,start_time=None,end_time=None, status=None, notes=None, created=None, is_valid=None):
        self.docType_id = docType_id
        self.numero_doc = numero_doc
        self.ssno = ssno
        self.first_name = first_name
        self.last_name = last_name
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.notes = notes
        self.created = created
        self.is_valid = is_valid
        
    @staticmethod
    def get_by_doc(document, limit):
        return Passport.query.filter_by(numero_doc=document).order_by(Passport.id.desc()).limit(limit)

    @staticmethod
    def get_by_doc_dates(document, start_time, end_time):
        return Passport.query.filter_by(numero_doc=document).filter(and_(Passport.start_time >= start_time, Passport.end_time <= end_time)).order_by(Passport.id.desc()).all()
    
    
    @staticmethod
    def get_by_doc_dates_site(document, start_time, end_time, site_id):
        return Passport.query.filter_by(numero_doc=document).filter(start_time >= start_time).filter(end_time<=end_time).filter(Passport.sites.site_id == site_id).one()
    
    
    def serialize(self):
        d = Serializer.serialize_list(self)
        return d

    def __repr__(self):
        return f'<Passport {self.id!r}>'



roles_parents = db.Table(
    'roles_parents',
    db.Column('role_id', db.Integer, db.ForeignKey('Acceso.role.id')),
    db.Column('parent_id', db.Integer, db.ForeignKey('Acceso.role.id'))
)


class Role(db.Model, RoleMixin):
    __table_args__ = {"schema": "Acceso"}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    parents = db.relationship(
        'Role',
        secondary=roles_parents,
        primaryjoin=(id == roles_parents.c.role_id),
        secondaryjoin=(id == roles_parents.c.parent_id),
        backref=db.backref('children', lazy='dynamic')
    )

    def __init__(self, name):
        RoleMixin.__init__(self)
        self.name = name

    def add_parent(self, parent):
        # You don't need to add this role to parent's children set,
        # relationship between roles would do this work automatically
        self.parents.append(parent)

    def add_parents(self, *parents):
        for parent in parents:
            self.add_parent(parent)

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()
    
# @dataclass
# class Role(db.Model):
#     __tablename__ = 'role'
    
#     id = Column(Integer, primary_key=True)
#     descripcion = Column(String(50), unique=True)
#     name =  Column(String(50), unique=True)
    
#     users = relationship('User',secondary=user_roles, back_populates='roles')
    
#     # users = relationship('User', secondary='user_roles', back_populates='roles')
    
#     def __init__(self, descripcion=None):
#         self.descripcion = descripcion

#     def get_roles():
#         roles = Role.query.all()
#         return roles

#     def __repr__(self):
#         return f'<Role {self.descripcion!r}>'

@dataclass
class ipBlackList(db.Model):
    __tablename__ = 'ipBlackList'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    ip = Column(String(15))
    start_date =  Column(DateTime)
    end_date =  Column(DateTime)
    username = Column(String(50))

    
    def __init__(self, ip=None, start_date=None, end_date=None, username=None):
        self.ip = ip
        self.start_date = start_date
        self.end_date = end_date
        self.username = username

    def is_blacklisted(self,ip,user, date_now):  
        print(ip,date_now)
        ipBlackListed = ipBlackList.query.filter(and_(ipBlackList.ip==ip, ipBlackList.username==user, ipBlackList.start_date<=date_now, ipBlackList.end_date>=date_now)).first()
        print(ipBlackListed)
        if ipBlackListed:
            return 1
        else:
            return 0
        
        
    def __repr__(self):
        return f'<ipBlackList {self.ip!r}>'

@dataclass
class Settings(db.Model):
    __tablename__ = 'settings'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    ecopass = Column(Integer, nullable=False)
    ecopass_email = Column(Integer, nullable=False)
    validacion_email = Column(Integer, nullable=False)
    verificacion_tapabocas = Column(Integer, nullable=False)


    
    def __init__(self, ecopass=None, ecopass_email=None, validacion_email=None, verificacion_tapabocas=None):
        self.ecopass = ecopass
        self.ecopass_email = ecopass_email
        self.validacion_email = validacion_email
        self.verificacion_tapabocas = verificacion_tapabocas
    
    def get_settings(self): 
        settings =  Settings.query.first()
        return settings

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
       
    def __repr__(self):
        return f'<Settings {self.id!r}>'
    

users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('Acceso.user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('Acceso.role.id'))
)


# @dataclass
# class UserRoles(db.Model):
#     __tablename__ = 'user_roles'
#     
#     id = Column(Integer(), primary_key=True, index=True)
#     user_id = Column(String(100), ForeignKey(User.id), primary_key = True)
#     role_id = Column(Integer(), ForeignKey('role.id'), primary_key = True)


@dataclass
class Chat(db.Model):
    __tablename__ = 'Chats'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    nombres = Column(String(13))
    numero_doc = Column(String(32), primary_key=True)
    regionalId = Column(String(50))
    ubicacionId = Column(String(50))
    instalacionNemonico = Column(String(10))
    registro_biometrico =  Column(Boolean)
    carne_activo =  Column(Boolean)
    doble_validacion =  Column(Boolean)
    tiene_foto =  Column(Boolean)
    tiene_permisos =  Column(Boolean)
    problema = Column(Text)
    termino_abandono =  Column(Boolean)
    resuelto =  Column(Boolean)
    escalado =  Column(Boolean)
    texto_adicional = Column(Text)
    email = Column(String(50))
    email_sistema = Column(String(50))
    metadatos = Column(String(254))
    fecha = Column(DateTime)
    email_sistema = Column(String(50))
    fecha_respuesta = Column(DateTime)
    text_respuesta = Column(Text)
    user_respuesta = Column(String(50))
    def __init__(
            self, 
            nombres = None,
            numero_doc = None,
            regionalId=None,
            ubicacionId=None,
            instalacionNemonico = None,
            registro_biometrico=None,
            carne_activo=None,
            doble_validacion=None,
            tiene_foto=None,
            tiene_permisos=None,
            termino_abandono=None,
            problema=None,
            resuelto=None,
            escalado=None,
            fecha=None,
            textoAdicional=None,
            email=None,
            email_sistema=None,
            fecha_respuesta=None,
            text_respuesta=None,
            user_respuesta=None
        ):
            self.nombre = nombres
            self.numero_doc = numero_doc
            self.regionalid = regionalId
            self.ubicacionid = ubicacionId
            self.instalacionNemonico = instalacionNemonico
            self.registro_biometrico = registro_biometrico
            self.carne_activo = carne_activo
            self.doble_validacion = doble_validacion
            self.tiene_foto = tiene_foto
            self.tiene_permisos = tiene_permisos
            self.termino_abandono = termino_abandono
            self.problema = problema
            self.resuelto = resuelto
            self.escalado = escalado
            self.fecha = fecha
            self.textoAdicional = textoAdicional
            self.email = email
            self.email_sistema = email_sistema
            self.fecha_respuesta = fecha_respuesta
            self.text_respuesta = text_respuesta
            self.user_respuesta = user_respuesta

    def get_chat_by_documento(documento):
        documento = "{}%".format(documento)
        return Chat.query.filter(Chat.numero_doc.like(documento)).all()

    def get_chats_by_instalacion(instalacion):
        instalacion = "{}%".format(instalacion)
        return Chat.query.filter(Chat.InstalacionNemonico.like(instalacion)).all()

    def get_chats_escalado(escalado):
        return Chat.query.filter(Chat.escalado == escalado).all()

    def get_chats_termino_abandono(termino):
        return Chat.query.filter(Chat.termino_abandono == termino).all()

    def get_chats_resuelto(resuelto):
        return Chat.query.filter(Chat.resuelto == resuelto).all()

    def get_chats_has_problema():
        return Chat.query.filter(Chat.problema != '').all()

    def get_chats_no_terminado_problema():
        return Chat.query.filter(and_(Chat.registro_biometrico == True, Chat.carne_activo == True, Chat.doble_validacion == True, Chat.tiene_foto == True, Chat.tiene_permisos == True, Chat.terminado == False)).all()

@dataclass
class DocType(db.Model):
    __tablename__ = 'docType'
    __table_args__ = {"schema": "Acceso"}
    id = Column(String(2), primary_key=True)
    descripcion = Column(String(50))
    
    
    def __init__(self, id=None, descripcion=None):
        self.id = id
        self.descripcion = descripcion
    
    def seed():
        db.session.add(DocType('CC','Cedula de Ciudadania'))
        db.session.add(DocType('CE',"Cedula de Extranjeria"))
        db.session.add(DocType('PA',"Pasaporte"))
        db.session.add(DocType('PE',"Permiso Especial de Permanencia"))
        db.session.add(DocType('TI',"Tarjeta de Identidad"))
        db.session.commit()
    

    def __repr__(self):
        return f'<DocType {self.descripcion!r}>'



@dataclass
class VisitorSite(db.Model):
    __tablename__ = 'visitorSite'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    visitor_id = Column(Integer, ForeignKey('Acceso.visitor.id'))
    site_id = Column(String(10))

@dataclass
class Visitor(db.Model):
    __tablename__ = 'visitor'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    authorization_id = Column(Integer, ForeignKey('Acceso.authorization.id'))
    last_name = Column(String(50))
    first_name = Column(String(50))
    docType_id = Column(String(2))
    numero_doc = Column(String(50), ForeignKey('Acceso.employee.numero_doc')) #//  ForeignKey('employeeSite.numero_doc'), , ForeignKey('enrolTemp.numero_doc')
    company_id = Column(Integer)
    image_url =  Column(String(250))
    region_id =  Column(Integer, ForeignKey('Acceso.region.id'))
    metadatos =  Column(String(250))
    email =  Column(String(100))
    fecha_inicial = Column(DateTime)
    fecha_final = Column(DateTime)
    created = Column(DateTime)
    updated = Column(DateTime)
    fecha2 = Column(DateTime)
    fecha3 = Column(DateTime)

    instalaciones = relationship('VisitorSite', backref='Visitor', 
                                primaryjoin='Visitor.id == VisitorSite.visitor_id', viewonly=True, sync_backref=False)

    region = relationship('Region', backref='Visitor',
                          primaryjoin='Region.id == Visitor.region_id', viewonly=True, sync_backref=False)

    # registro = relationship('EnrolTemp', backref='Visitor',
    #                       primaryjoin='and_(EnrolTemp.numero_doc == Visitor.numero_doc, EnrolTemp.stepEnrol_id == 2)', viewonly=True, lazy='joined')

    # fotos = relationship('EmployeeSite', backref='Visitor',
    #                       primaryjoin='and_(EmployeeSite.numero_doc == Visitor.numero_doc, EmployeeSite.procesado == 1)', viewonly=True, lazy='joined')

    funcionario = relationship('Authorization', backref='Visitor',
                          primaryjoin='Authorization.id == Visitor.authorization_id', viewonly=True, lazy='joined',sync_backref=False)

    # eventos = relationship('LogEventosAcceso', backref='Visitor',
    #                       primaryjoin='LogEventosuser_id == Visitor.numero_doc', viewonly=True, uselist=True, lazy='joined')

    def __init__(
            self, 
            authorization_id=None,
            last_name=None,
            first_name=None,
            docType_id=None,
            numero_doc=None,
            company_id=None,
            image_url=None,
            region_id=None,
            metadatos=None,
            email=None,
            fecha_inicial=None,
            fecha_final=None,
            created=None,
            updated=None,
            fecha2=None,
            fecha3=None
            
        ):
            self.authorization_id = authorization_id
            self.last_name = last_name
            self.first_name = first_name
            self.numero_doc = numero_doc
            self.docType_id = docType_id
            self.company_id = company_id
            self.image_url = image_url
            self.region_id = region_id
            self.metadatos = metadatos
            self.email = email
            self.fecha_inicial = fecha_inicial
            self.fecha_final = fecha_final
            self.created = created
            self.updated = updated
            self.fecha2 = fecha2
            self.fecha3 = fecha3
            
    @hybrid_property
    def fullname(self):
        return self.first_name + " " + self.last_name
    
    @staticmethod
    def create(n, site_id=None, date=None):
        fkr = fk('es_CO')
        print("Creando %s visitantes" % n)
        
        
        
        for i in range(n):
            
            emp_id = random.randint(1,Employee.query.count())
            emp = Employee.query.filter(Employee.id == emp_id).first()
            email = emp.first_name + '.' + emp.last_name + '@indracompany.es'
            fullname = emp.first_name + ' ' + emp.last_name
            
            new_auth =  Authorization (
                email = email,
                name =  fullname,
                user_id = 'UsuarioLocal' + emp.first_name[0] + emp.last_name
            )
            
            db.session.add(new_auth)
            db.session.commit()
            
            auth_id = new_auth.id
            
            lastName = fkr.last_name()
            firstName = fkr.first_name()
            fullname = firstName + ' ' + lastName
            if date is None:
                time = fkr.date_time_between(start_date = "now", end_date = "+1M")
            else:
                time = fkr.date_time_between(start_date = date, end_date = date)
            
            start_time = time
            end_time = start_time + timedelta(hours=1)

            
            new_visitor = Visitor(
                authorization_id=auth_id,
                last_name=lastName,
                first_name=firstName,
                docType_id='CC',
                numero_doc = '10' + fkr.ean(length=8),
                company_id=12632,
                image_url=None,
                metadatos=None,
                email=fkr.email(),
                fecha_inicial=start_time,
                fecha2 = fkr.date_time_between(start_date = "now", end_date = "+1M"),
                fecha3 = fkr.date_time_between(start_date = "now", end_date = "+1M"),
                created= fkr.date_time_between(start_date = "now", end_date = "now"),

            )
            
            db.session.add(new_visitor)
            db.session.commit()
            
            dev_id = random.randint(1,4)
            site_id = Device.query.filter(Device.id == dev_id).first().site_id
            
            new_visitor_site = VisitorSite(
                visitor_id=new_visitor.id,
                site_id=site_id
            )
            
            db.session.add(new_visitor_site)
            db.session.commit()
            
            print("Adding visitor ")
            
            
    def get_invitado_by_documento(documento):
        documento = "{}%".format(documento)
        return Visitor.query.filter(Visitor.numero_doc.like(documento)).all()


    def get_all_by_date(date):
        return Visitor.query.filter(or_(Visitor.fecha_inicial == date, Visitor.fecha2 == date,  Visitor.fecha2 == date)).all()

    def __repr__(self):
        fullname = self.first_name + ' ' + self.last_name
        return f'<Visitor {fullname!r}>'

@dataclass
class Authorization(db.Model):
    __tablename__ = 'authorization'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    email = Column(String(50))
    name = Column(String(100))
    user_id = Column(String(100))
    created = Column(DateTime)
    updated = Column(DateTime)

    def __init__(
            self, 
            email=None,
            name=None,
            user_id=None,
            created=None,
            updated=None
        ):

            self.email = email
            self.name = name
            self.user_id = user_id
            self.created = created
            self.updated = updated
            
            
@dataclass
class Calendar(db.Model):
    __tablename__ = 'calendar'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    calendario = Column(String(50))
    
    
    def __init__(self, calendario=None):
        self.calendario = calendario
    
    def seed():
        db.session.add(Calendar('Reservas'))
        db.session.commit()

    def __repr__(self):
        return f'<Calendar {self.calendario!r}>'
        
        
@dataclass
class RepetitionType(db.Model):
    __tablename__ = 'repetition_type'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    repetition_type = Column(String(50))
    
    
    def __init__(self, repetition_type=None):
        self.repetition_type = repetition_type
    
    def seed():
        db.session.add(RepetitionType('Diario'))
        db.session.add(RepetitionType('Semanal'))
        db.session.add(RepetitionType('Mensual'))
        db.session.add(RepetitionType('Anual'))
        db.session.add(RepetitionType('Único'))
        db.session.add(RepetitionType('Fechas especificas'))
        db.session.commit()
        
    def __repr__(self):
        return f'<RepetitionType {self.repetition_type!r}>'
    
@dataclass
class Event(db.Model):
    __tablename__ = 'event'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    event = Column(String(100))
    calendar_id = Column(Integer, ForeignKey('Acceso.calendar.id'))
    repetitiontype_id = Column(Integer, ForeignKey('Acceso.repetition_type.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    user_id = Column(Integer, ForeignKey('Acceso.user.id'))
    espacio_id = Column(Integer, ForeignKey('Acceso.espacio.id'))
    
    def __init__(self, calendar_id=None, repetition_type=None, start_time=None, end_time=None, user_id=None, espacio_id=None):
        self.calendar_id = calendar_id
        self.repetition_type = repetition_type
        self.start_time = start_time
        self.end_time = end_time
        self.user_id = user_id
        self.espacio_id = espacio_id

    def get_events(from_datetime = None, to_datetime = None, user_id = None, espacio_id = None):
        
        filters = []
        
        if (from_datetime is not None):
            filters.append({'field':'end_time', 'op':'==','value':to_datetime})
        
        if (to_datetime is not None):
            filters.append({'field':'start_time', 'op':'==','value':from_datetime})
        
        if (espacio_id is not None):
            filters.append({'field':'espacio_id', 'op':'==','value':espacio_id})
            
        if (user_id is not None):
            filters.append({'field':'user_id', 'op':'==','value':user_id})
            
        events = apply_filters(Event.query, filters)

        return events

    @staticmethod
    def create(n):
        fkr = fk('es_CO')
        event = []
        print("Creando %s eventos" % n)
        
        user_count = User.query(User.id).count()
        espacios = Espacio.query(Espacio.id).count()
        
        for i in range(n):
            calendar_id = 1
            repetition_type = fkr.random_element(elements=(1,2,3,4,5,6))
            start_time = fkr.date_time_this_year()
            hours = fkr.random_element(elements=(1,2,3,4,5,6))
            end_time = start_time + timedelta(hours = hours)
            user_id = fkr.random_number(1,user_count)
            espacio_id = fkr.random_number(1,espacios)
            

            
            new_event = Event(
                calendar_id=calendar_id,
                repetition_type=repetition_type,
                start_time=start_time,
                end_time=end_time,
                user_id=user_id,
                espacio_id=espacio_id
            )
            
            print("Adding event: %s" % new_event)
            db.session.add(new_event)
            db.session.commit()
        
        
    def __repr__(self):
        return f'<Event {self.event!r}>'


@dataclass
class AuthorizedVisitorWeb(db.Model):
    __tablename__ = 'authorizedVisitorWeb'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    numero_doc = Column(String(50), ForeignKey("Acceso.employee.numero_doc"))
    email = Column(String(50))
    nombres = Column(String(100))
    created = Column(DateTime)
    updated = Column(DateTime)

    def __init__(
            self, 
            email=None,
            numero_doc=None,
            nombres=None,
            created=None,
            updated=None
        ):

            self.email = email
            self.nombres = nombres
            self.numero_doc = numero_doc
            self.created = created
            self.updated = updated  

@dataclass
class UnathorizedVisitor(db.Model):
    __tablename__ = 'unauthorizedVisitor'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    numero_doc = Column(String(50), ForeignKey("Acceso.employee.numero_doc"))
    email = Column(String(50))
    nombres = Column(String(100))
    created = Column(DateTime)
    updated = Column(DateTime)

    def __init__(
            self, 
            email=None,
            numero_doc=None,
            nombres=None,
            created=None,
            updated=None
        ):

            self.email = email
            self.nombres = nombres
            self.numero_doc = numero_doc
            self.created = created
            self.updated = updated      

@dataclass
class UnathorizedVisitorWeb(db.Model):
    __tablename__ = 'unauthorizedVisitorWeb'
    __table_args__ = {"schema": "Acceso"}
    id = Column(Integer, primary_key=True)
    numero_doc = Column(String(50), ForeignKey("Acceso.employee.numero_doc"))
    email = Column(String(50))
    nombres = Column(String(100))
    created = Column(DateTime)
    updated = Column(DateTime)

    def __init__(
            self, 
            email=None,
            numero_doc=None,
            nombres=None,
            created=None,
            updated=None
        ):

            self.email = email
            self.nombres = nombres
            self.numero_doc = numero_doc
            self.created = created
            self.updated = updated 

                  
def serialize(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns)