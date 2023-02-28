# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import jsonify, current_app
from flask_login import UserMixin
import sys

# from sqlalchemy import SQLAlchemyError
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import ForeignKey, Column, String, Integer, UniqueConstraint

from dataclasses import dataclass

from re import sub
from decimal import Decimal
import locale
import hashlib

from unidecode import unidecode

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

from datetime import datetime

# from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature



class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

            
        
class Users(db.Model, UserMixin):
    
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(64), unique=True)
    password      = db.Column(db.String(255))
    group_id      = db.Column(db.Integer, nullable=True)
    role_id       = db.Column(db.Integer, nullable=True)
    avatar        = db.Column(db.String(255), nullable=True)
    first_name    = db.Column(db.String(125), nullable=True)
    last_name     = db.Column(db.String(125), nullable=True)
    address       = db.Column(db.String(255), nullable=True)
    phone         = db.Column(db.String(20), nullable=True)
    rut           = db.Column(db.String(20), nullable=True)
    banco         = db.Column(db.String(100), nullable=True)
    tipo_cuenta   = db.Column(db.String(50), nullable=True)
    ncuenta       = db.Column(db.String(50), nullable=True)
    firma         = db.Column(db.String(255), nullable=True)
    

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
    
    def generate_auth_token(self, expiration = 600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({ 'id': self.id })
    
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = Users.query.get(data['id'])
        return user

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
    
    

    # username = request.form.get('username')
    # user = Users.query.filter_by(username=username).first()
    # return user if user else None

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(Users)

