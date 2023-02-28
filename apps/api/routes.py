# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, session, redirect, url_for, make_response, abort, g, current_app
from flask_login import login_required, current_user, login_user
from flask_charts import GoogleCharts, Chart
from jinja2 import TemplateNotFound, Environment, PackageLoader, select_autoescape
from jinja_datatables.jinja_extensions.datatableext import DatatableExt
from jinja_datatables.datatable_classes import DatatableColumn, AjaxDatatable, JSArrayDatatable, HTMLDatatable

from apps.authentication.models import Users
from apps.home.models import *

# from apps.home.forms import NewInvoice, NewClient, NewContact, NewProject, UserForm
from apps.home.numero_letras import *

from sqlalchemy.sql import func

from apps.authentication.util import verify_pass

import locale
import pdfkit
import os

from apps import db

from datetime import datetime, timedelta

from weasyprint import HTML, CSS

from babel.numbers import format_number, format_decimal, format_currency

import jwt
import uuid
import re
from  functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return 'Unauthorized Access!', 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Users.query.filter(Users.username == data['username']).first()
            if not current_user:
                return 'Unauthorized Access!', 401
        except  Exception as ex:
            print(ex)
            return 'Unauthorized Access!', 401
        return f(*args, **kwargs)

    return decorated


@blueprint.route('/api/login', methods=['POST'])
def api_login():
    response = {
        "success" : False,
        "message" : "Invalid parameters",
        "token" : ""
    }
    try:
        auth = request.form

        if not auth or not auth.get('username') or not auth.get('password'):
            response["message"] = 'Invalid data'
            return response, 422

        user = Users.query.filter(Users.username == auth['username']).first()
        
        if not user:
            response["message"] = "Unauthorized Access!"
            return response, 401

        if verify_pass(auth['password'], user.password):
        # if check_password_hash(user['password'], auth['password']):
            token = jwt.encode({
                'username': user.username,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            response["message"] = "token generated"
            response["token"] = token
            response["success"] = True
            return response, 200
        response["message"] = 'Invalid emailid or password'
        return response, 403
    except Exception as ex:
        print(str(ex))
        return response, 422


@blueprint.route('/api/token')
@login_required
def get_auth_token():
    token = current_user.generate_auth_token()
    return jsonify({ 'token': token })


@blueprint.route('/api/get_visitors')
@token_required
def getVisitors():
    today = datetime.today().strftime('%Y-%m-%d')
    today_start = today + ' 00:00:00'
    today_end = today + ' 23:59:59'
    
    visitors = Visitor.query.filter(or_(and_(Visitor.fecha_inicial >= today_start, Visitor.fecha_inicial <= today_end), and_(Visitor.fecha2 >= today_start, Visitor.fecha2 <= today_end), and_(Visitor.fecha3 >= today_start, Visitor.fecha3 <= today_end)))
    por_llegar = Visitor.query.filter(or_(and_(Visitor.fecha_inicial >= datetime.now(), Visitor.fecha_inicial <= today_end), and_(Visitor.fecha2>= datetime.now(), Visitor.fecha2 <= today_end), and_(Visitor.fecha3 >= datetime.now(), Visitor.fecha3 <= today_end)))
    cvisitor = visitors.count()
    c_por_llegar = por_llegar.count()
    
    info_visitors = []
    count_ingresos = 0
    for visitor in visitors.all():
        events = UploadPerson.get_all_by_doc_and_date(visitor.numero_doc, today_start, today_end)
        
        
        for event in events:
            if event is not None and event.direction == 1:
                count_ingresos = count_ingresos + 1
                break
            
        info_visitor = {
            'numero_doc': visitor.numero_doc,
            'fullname': visitor.first_name + ' ' + visitor.last_name,
            'company_id': visitor.company_id,
            'funcionario': visitor.funcionario.name,
            'emailFuncionario': visitor.funcionario.email,
            'instalaciones': visitor.instalaciones,
            'events': events,
            'ingreso': True if events is not None else False
        }
        info_visitors.append(info_visitor)
    
    visitor_still_inside = UploadPerson.query.with_entities(   UploadPerson.user_id.label('user_id'), UploadPerson.name.label('name'), func.max(UploadPerson.server_timestamp).label('server_timestamp'), UploadPerson.device_id.label('device_id'), Device.site_id.label('site_id'), Device.direction.label('direction')).filter(UploadPerson.user_id != '').filter(UploadPerson.server_timestamp >= today_start).join(Device).filter(Device.device_id == UploadPerson.device_id).join(Employee).filter(Employee.tipo_employee.like('Visitante')).order_by(UploadPerson.server_timestamp.desc()).group_by(UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.site_id, Device.direction, UploadPerson.server_timestamp)
    
    
    data = {
        'visitors': info_visitors,
        'still_inside': visitor_still_inside.all(),
        'cvisitor': cvisitor,
        'c_por_llegar': c_por_llegar,
        'count_ingresos': count_ingresos
    }
    
    return jsonify(data)


@blueprint.route('/api/search_visitors')
@token_required
def searchVisitors():
    today = datetime.today().strftime('%Y-%m-%d')
    params = json.loads(request.data)
    if 'start_date' in params:
        start_date = params['start_date']
    else: 
        start_date = today + ' 00:00:00'
    
    if 'end_date' in params:
        end_date = params['end_date']
    else: 
        end_date = today + ' 23:59:59'
    
    if 'name' in params:
        name = params['name']
    else: 
        name = None
            
    if 'ciudad' in params:
        ciudad = params['ciudad']
    else:
        ciudad = None

    if 'site_id' in params:
        site_id = params['site_id']
    else:
        site_id = None
    
    if 'auth_email' in params:
        auth_email = params.get['auth_email']
    else:
        auth_email = None
        
    if 'name' in params:
        visitors_dates = Visitor.query.filter(or_(Visitor.first_name.like(name), Visitor.last_name.like(name), Visitor.fullname.like(name))).filter(or_(and_(Visitor.fecha_inicial >= start_date, Visitor.fecha_inicial <= end_date), and_(Visitor.fecha2 >= start_date, Visitor.fecha2 <= end_date), and_(Visitor.fecha3 >= start_date, Visitor.fecha3 <= end_date)))
    else:
        visitors_dates = Visitor.query.filter(or_(and_(Visitor.fecha_inicial >= start_date, Visitor.fecha_inicial <= end_date), and_(Visitor.fecha2 >= start_date, Visitor.fecha2 <= end_date), and_(Visitor.fecha3 >= start_date, Visitor.fecha3 <= end_date)))
    
    if site_id is not None:
        visitors_site = visitors_dates.join(Device).filter(Visitor.device_id == Device.device_id).filter(Device.site_id == site_id)
        if auth_email is not None:
            visitors_auth = visitors_site.join(Authorization).filter(Visitor.authorization_id == Authorization.id).filter(Authorization.email == auth_email)
            visitors = visitors_auth
        else:
            visitors = visitors_dates
    else:
        if auth_email is not None:
            visitors_auth= visitors_dates.join(Authorization).filter(Visitor.authorization_id == Authorization.id).filter(Authorization.email == auth_email)
            visitors = visitors_auth
        else:
            visitors = visitors_dates
    
    cvisitor = visitors.count()
    
    
    info_visitors = []
    count_ingresos = 0
    
    for visitor in visitors.all():
        events = UploadPerson.get_all_by_doc_and_date(visitor.numero_doc, start_date, end_date)
        
        for event in events:
            if event is not None and event.direction == 1:
                count_ingresos = count_ingresos + 1
                break
            
        info_visitor = {
            'numero_doc': visitor.numero_doc,
            'fullname': visitor.first_name + ' ' + visitor.last_name,
            'company_id': visitor.company_id,
            'funcionario': visitor.funcionario.name,
            'emailFuncionario': visitor.funcionario.email,
            # 'instalaciones': visitor.instalaciones,
            # 'events': events,
            # 'ingreso': True if events is not None else False
        }
        info_visitors.append(info_visitor)
    
    print(info_visitors)
    data = {
        'visitors': info_visitors,
        'cvisitor': cvisitor,
        'count_ingresos': count_ingresos
    }
    
    return jsonify(data)

