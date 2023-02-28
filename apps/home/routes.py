# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, session, redirect, url_for, make_response, abort
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

import locale
import pdfkit
import os

from apps import db

from datetime import datetime, timedelta

from weasyprint import HTML, CSS

from babel.numbers import format_number, format_decimal, format_currency


@blueprint.route('/index')
@login_required
def index():
    regiones = Region.query.count()
    instalaciones = Instalation.query.count()
    empleados = Employee.query.count()
    today = datetime.today().strftime('%Y-%m-%d')
    today_start = today + ' 00:00:00'
    today_end = today + ' 23:59:59'
    tot_evn = UploadPerson.query.filter(UploadPerson.server_timestamp >= today_start).filter(UploadPerson.server_timestamp <= today_end).count()
    tot_rec = UploadPerson.query.filter(UploadPerson.server_timestamp >= today_start).filter(UploadPerson.server_timestamp <= today_end).filter(UploadPerson.matched==1).count()
    tot_ing =  UploadPerson.query.filter(UploadPerson.server_timestamp >= today_start).filter(UploadPerson.server_timestamp <= today_end).filter(UploadPerson.matched==1).filter(UploadPerson.device.has(direction=1)).count()
    tot_sal =  UploadPerson.query.filter(UploadPerson.server_timestamp >= today_start).filter(UploadPerson.server_timestamp <= today_end).filter(UploadPerson.matched==1).filter(UploadPerson.device.has(direction=0)).count()
    tot_by_ins = UploadPerson.query.filter(UploadPerson.server_timestamp >= today_start).filter(UploadPerson.server_timestamp <= today_end).filter(UploadPerson.matched==1).join(Device).with_entities(Device.site_id, Device.direction, func.count(Device.direction), func.count(UploadPerson.id)).group_by(Device.site_id, Device.direction).order_by(Device.site_id, Device.direction.desc()).all()
    tot_by_type = UploadPerson.query.filter(UploadPerson.server_timestamp >= today_start).filter(UploadPerson.server_timestamp <= today_end).filter(UploadPerson.matched==1).distinct(UploadPerson.user_id).join(Employee).with_entities(Employee.tipo_employee, func.count(Employee.tipo_employee)).group_by(Employee.tipo_employee).all()
    events = UploadPerson.get_all_by_date(today_start, today_end).all()
    last_events = UploadPerson.query.with_entities(UploadPerson.server_timestamp, UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.direction).filter(UploadPerson.user_id != '').filter(UploadPerson.server_timestamp >= today_start).join(Device).filter(Device.device_id == UploadPerson.device_id).group_by(UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.direction, UploadPerson.server_timestamp).all()
    contractor_still_inside = UploadPerson.query.with_entities(Device.site_id, UploadPerson.user_id, UploadPerson.name, UploadPerson.server_timestamp, UploadPerson.device_id, Device.direction).filter(UploadPerson.user_id != '').filter(UploadPerson.server_timestamp >= today_start).join(Device).filter(Device.device_id == UploadPerson.device_id).filter(Device.direction == 1).join(Employee).filter(Employee.tipo_employee.like('Contratista')).group_by(Device.site_id, UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.direction, UploadPerson.server_timestamp)
    visitor_still_inside = UploadPerson.query.with_entities(   UploadPerson.user_id.label('visitor_id'), UploadPerson.name.label('name'), func.max(UploadPerson.server_timestamp).label('server_timestamp'), UploadPerson.device_id.label('device_id'), Device.site_id.label('site_id'), Device.direction.label('user_id')).filter(UploadPerson.user_id != '').filter(UploadPerson.server_timestamp >= today_start).join(Device).filter(Device.device_id == UploadPerson.device_id).join(Employee).filter(Employee.tipo_employee.like('Visitante')).order_by(UploadPerson.server_timestamp.desc()).group_by(UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.site_id, Device.direction, UploadPerson.server_timestamp).limit(1)
    employee_still_inside = UploadPerson.query.with_entities(  Device.site_id, UploadPerson.user_id, UploadPerson.name, UploadPerson.server_timestamp, UploadPerson.device_id, Device.direction).filter(UploadPerson.user_id != '').filter(UploadPerson.server_timestamp >= today_start).join(Device).filter(Device.device_id == UploadPerson.device_id).filter(Device.direction == 1).join(Employee).filter(Employee.tipo_employee.like('Empleado')).group_by(Device.site_id, UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.direction, UploadPerson.server_timestamp)

    vi = visitor_still_inside.count()
    ci = contractor_still_inside.count()
    ei = employee_still_inside.count()
    
    
    # tot_by_site_ing =  UploadPerson.query.filter(UploadPerson.server_timestamp >= '2023-02-22 00:00:00').filter(UploadPerson.server_timestamp <= today_end).filter(UploadPerson.matched==1).filter(UploadPerson.device.has(direction=1)).group_by(UploadPerson.site_id).all()
    return render_template('home/index.html', segment='index', tot_evn=tot_evn, tot_rec=tot_rec, tot_ing=tot_ing, tot_sal=tot_sal, tot_by_ins=tot_by_ins, regiones=regiones, instalaciones=instalaciones, tot_by_type=tot_by_type, events=events, last_events=last_events, visitor_still_inside=visitor_still_inside.all(), contractor_still_inside=contractor_still_inside.all(), employee_still_inside=employee_still_inside.all())


@blueprint.route('/profile/<id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    user = Users.query.get(id)
    if user is None:
        abort(403)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for('home_blueprint.index'))

    return render_template('home/profile.html', segment='index', user=user, form=form)


@blueprint.route('/contratistas', methods=['GET', 'POST'])
@login_required
def contratistas():
    today = datetime.today().strftime('%Y-%m-%d')
    today_start = today + ' 00:00:00'
    contractor_still_inside = UploadPerson.query.with_entities(Device.site_id, UploadPerson.user_id, UploadPerson.name, UploadPerson.server_timestamp, UploadPerson.device_id, Device.direction).filter(UploadPerson.user_id != '').filter(UploadPerson.server_timestamp >= today_start).join(Device).filter(Device.device_id == UploadPerson.device_id).filter(Device.direction == 1).join(Employee).filter(Employee.tipo_employee.like('Contratista')).group_by(Device.site_id, UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.direction, UploadPerson.server_timestamp)
    return render_template('home/empleados.html', segment='index', contractor_still_inside=contractor_still_inside)

@blueprint.route('/empleados', methods=['GET', 'POST'])
@login_required
def empleados():
    today = datetime.today().strftime('%Y-%m-%d')
    today_start = today + ' 00:00:00'
    employee_still_inside = UploadPerson.query.with_entities(  Device.site_id, UploadPerson.user_id, UploadPerson.name, UploadPerson.server_timestamp, UploadPerson.device_id, Device.direction).filter(UploadPerson.user_id != '').filter(UploadPerson.server_timestamp >= today_start).join(Device).filter(Device.device_id == UploadPerson.device_id).filter(Device.direction == 1).join(Employee).filter(Employee.tipo_employee.like('Empleado')).group_by(Device.site_id, UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.direction, UploadPerson.server_timestamp)
    return render_template('home/empleados.html', segment='index', employee_still_inside=employee_still_inside)

@blueprint.route('/visitantes', methods=['GET', 'POST'])
@login_required
def visitantes():
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
            'instalaciones': visitor.instalaciones,
            'events': events,
            'company_id': visitor.company_id,
            'funcionario': visitor.funcionario.name,
            'emailFuncionario': visitor.funcionario.email,
            'ingreso': True if visitor.instalaciones is not None else False
        }
        info_visitors.append(info_visitor)
    
    visitor_still_inside = UploadPerson.query.with_entities(   UploadPerson.user_id.label('user_id'), UploadPerson.name.label('name'), func.max(UploadPerson.server_timestamp).label('server_timestamp'), UploadPerson.device_id.label('device_id'), Device.site_id.label('site_id'), Device.direction.label('direction')).filter(UploadPerson.user_id != '').filter(UploadPerson.server_timestamp >= today_start).join(Device).filter(Device.device_id == UploadPerson.device_id).join(Employee).filter(Employee.tipo_employee.like('Visitante')).order_by(UploadPerson.server_timestamp.desc()).group_by(UploadPerson.user_id, UploadPerson.name, UploadPerson.device_id, Device.site_id, Device.direction, UploadPerson.server_timestamp)
    return render_template('home/visitantes.html', segment='index', visitors_data=visitors, visitor_still_inside=visitor_still_inside, info_visitors=info_visitors, cvisitor=cvisitor, count_ingresos=count_ingresos, c_por_llegar=c_por_llegar)


@blueprint.route('/info/<cedula>')
@login_required
def info(cedula):
    """Acceso a la vista de informacion de un usuario identificado con un numero de documento enviado como parametro"""
    print(f'Se obtiene la cédula')
    cedula = cedula.split('.')[0]
    print(f'Documento: {cedula}')
    if cedula != 0 or cedula is not None:
        print('Se obtiene usuario de enrolTemp...')
        user = Employee.get_by_doc(cedula)
        print('Consultando planta Personal ... ')
        # empleado = PlantaPersonal.get_by_doc(cedula)
        print('Consultando planta Contratistas ... ')
        # contratista = PlantaContratistas.get_by_doc(cedula)
        print('Leyendo Pasaportes ... ')
        pasaportes = Passport.get_by_doc(cedula, 10)
        print('Consultando  Empleados ... ')
        employee = Employee.get_by_doc(cedula)
        # print('Consultando  dispositivos con imagen ... ')
        # sitesEmp=EmployeeSite.get_by_doc(cedula)
        
        # if app.config('CONSULTAR_LENEL'):
        #     print('Consultando  datos lenel ... ')
        #     datosLenel=lenel_data(cedula)
        # else: 
        #     datosLenel={}

        # print('Consultando  datos lenel ... ')
        # datosLenel=lenel_data(cedula)
        # print('Consultando  Diagnostico ... ')  
        # diag = diagnostico(cedula, None)
        # print('Cargando regionales')
        # regionales = get_regionales();
        print('Renderizando informe.... ')
    

        #print(pasaportes.end_date)
        # data = EnrolTemp.query.filter_by(numero_doc=cedula).first()
        imagen= cedula + ".jpg"
        apikey= os.getenv("APIKEY")
        return render_template(
            "home/info.html",
            imagen=imagen,
            enrolTemp=user,
            # registros=registros,
            # terminados=terminados,
            # ultimo=ultimo,
            empleado=empleado,
            # contratista=contratista,
            # transacciones=transacciones,
            cedula=cedula,
            pasaportes=pasaportes,
            employee=employee,
            # sites=sitesEmp,
            apikey=apikey,
            # datosLenel=json.loads(datosLenel),
            # diagnostico=diag,
            # regionales = regionales.json
            # terminos=terminos
        )
    else:
        return render_template(
            "home/info.html",
            imagen=None,
            enrolTemp=None,
            registros=None,
            terminados=None,
            ultimo=None,
            empleado=None,
            contratista=None,
            # transacciones=None,
            cedula=None,
            pasaportes=None,
            employee=None,
            # sites=None,
            apikey=None
        )
        
        
@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
