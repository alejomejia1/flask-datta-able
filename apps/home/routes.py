# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, session, redirect, url_for, make_response
from flask_login import login_required, current_user, login_user
from flask_charts import GoogleCharts, Chart
from jinja2 import TemplateNotFound, Environment, PackageLoader, select_autoescape
from jinja_datatables.jinja_extensions.datatableext import DatatableExt
from jinja_datatables.datatable_classes import DatatableColumn, AjaxDatatable, JSArrayDatatable, HTMLDatatable

from apps.home.models import Invoice, Client, Contact, Project
from apps.authentication.models import Users
from apps.home.forms import NewInvoice, NewClient, NewContact, NewProject
from apps.home.numero_letras import *

from sqlalchemy.sql import func

import locale
import pdfkit

from apps import db

from datetime import datetime, timedelta

from weasyprint import HTML, CSS

from babel.numbers import format_number, format_decimal, format_currency


@blueprint.route('/index')
@login_required
def index():
    ds = Invoice.get_daily_total()
    ms = Invoice.get_monthly_total()
    ys = Invoice.get_yearly_total()
    lf = Invoice.get_last_n(10)
    ct = Client.get_cllients_total()
    it = Invoice.invoices_this_year()
    cty = Invoice.clients_this_year()
    incomes = Invoice.query.join(Client).with_entities(Client.reference, func.sum(Invoice.valor)).group_by(Invoice.client_id).order_by(func.sum(Invoice.valor).desc()).all()
    clientes = Client.get_clients_list()
    ingresos = []
    ingreso_labels = []
    ingreso_values = []
    for income in incomes:
        data = [income[1]]
        name = income[0]
        ingreso = {
            "name": income[0],
            "data": data
        }
        ingresos.append(ingreso)
        ingreso_labels.append(income[0])
        ingreso_values.append(income[1])
        
    my_chart = Chart("BarChart", "my-chart")   
    my_chart.options = {
        "title": "Clientes",
        "width": "100%",
        "height": "400px",
    }
    my_chart.data.add_column("string", "Client")    
    my_chart.data.add_column("number", "Ingresos")
    
    hdata = []
    for income in incomes:
        my_chart.data.add_row([income[0], income[1]])
        hdata.append(income[1])
    
    
    print(ds, ms)
    return render_template('home/index.html', segment='index', ds = ds, ms=ms, ys=ys, lf=lf, ct=ct, it=it, cty=cty, n=10, ingresos=ingresos , ingreso_labels=ingreso_labels, ingreso_values= ingreso_values, clientes=clientes, my_chart=my_chart)

@blueprint.route('/invoices')
@login_required
def invoices():
    lis = Invoice.get_last_n(100)
    return render_template('home/invoices.html', segment='index', lis=lis)


@blueprint.route('/projects')
@login_required
def projects():
    projects = Project.query.all()
    return render_template('home/projects.html', segment='index', projects=projects)


@blueprint.route('/invoices_pdf/<id>')
@login_required
def invoice_pdf(id):
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
    user = Users.query.filter(Users.id == current_user.id).first()
    invoice = Invoice.query.filter(Invoice.id == id).first()
    numeroLetras = numero_a_letras(invoice.valor) + " de Pesos"
    fechaLetras = invoice.fecha_factura.strftime('%B %d  de %Y')
    username = current_user.name
    valor = format_currency(invoice.valor,'COP',locale="es_CO")
    rendered = render_template('pdf/invoice.html', segment='index', invoice=invoice, valor=valor, valor_letras = numeroLetras.capitalize(), fecha = fechaLetras.capitalize(), username = username)
    options={
        'page-size':'Letter',
        'encoding' : 'UTF-8',
        'enable-local-file-access': ''
    }
    file_name = '{0}-CC-{1}-{2}.pdf'.format(invoice.cliente.name, invoice.nfactura, datetime.today().strftime('%Y-%m-%d'))
    pdf= pdfkit.from_string(rendered, False, options)
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    disposition  = 'attachment; filename=' + file_name
    response.headers['Content-Disposition'] = disposition
    # attachment
    return response


@blueprint.route('/new_invoice', methods=['GET', 'POST'])
@login_required
def new_invoice():
    print(current_user)
    form = NewInvoice()
    if form.validate_on_submit():
        session['form'] = form.data
        return redirect(url_for('home_blueprint.store_invoice'))
    form.prefijo.data = "CC"    
    form.nfactura.data = Invoice.get_last_invoice() + 1
    form.user_id.data = current_user.id
    form.status_id.data = 1
    form.anulada.data = False
    
    return render_template('home/form_new_invoice.html', segment='index', form=form)
    
@blueprint.route('/new_client', methods=['GET', 'POST'])
@login_required
def new_client():
    form = NewClient()
    if form.validate_on_submit():
        session['form'] = form.data
        return redirect(url_for('home_blueprint.store_client'))
    # form.user_id.data = current_user.id
    return render_template('home/form_new_client.html', segment='index', form=form)
    
@blueprint.route('/store_client')
@login_required
def store_client():
    client = session['form']
    store = Client.add_new(client)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/edit_client/<id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    print(current_user)
    client = Client.query.get(id)
    form = NewClient()
    if form.validate_on_submit():
        session['form'] = form.data
        return redirect(url_for('home_blueprint.update_invoice', id = client.id))
    if request.method == 'GET':
        form.name.data = client.prefijo
        form.user_id.data = client.nfactura
        form.reference.data = client.reference
        form.email.data = client.email
        form.phone.data = client.phone
        form.address.data = client.address
        form.nit.data = client.nit

    return render_template('home/form_edit_client.html', segment='index', form=form, id = client.id)

@blueprint.route('/update_client/<id>')
@login_required
def update_client(id):
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
    client = Client.query.get(id)
    client.name = session["form"]["name"]
    client.reference = session["form"]["reference"]
    client.email = session["form"]["email"]
    client.phone = session["form"]["phone"]
    client.address = session["form"]["address"]
    client.nit = session["form"]["nit"]
    Client.update(client)
    db.session.commit()
    return redirect(url_for('home_blueprint.clients'))

@blueprint.route('/new_contact', methods=['GET', 'POST'])
@login_required
def new_contact():
    form = NewContact()
    if form.validate_on_submit():
        session['form'] = form.data
        return redirect(url_for('home_blueprint.store_contact'))
    # form.user_id.data = current_user.id
    return render_template('home/form_new_contact.html', segment='index', form=form)
    
@blueprint.route('/store_contact')
@login_required
def store_contacct():
    contact = session['form']
    store = Contact.add_new(contact)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/new_project', methods=['GET', 'POST'])
@login_required
def new_project():
    form = NewProject()
    if form.validate_on_submit():
        session['form'] = form.data
        return redirect(url_for('home_blueprint.store_project'))
    # form.user_id.data = current_user.id
    return render_template('home/form_new_project.html', segment='index', form=form)
    
@blueprint.route('/store_project')
@login_required
def store_project():
    project = session['form']
    store = Project.add_new(project)
    return redirect(url_for('home_blueprint.index'))

  
@blueprint.route('/edit_invoice/<id>', methods=['GET', 'POST'])
@login_required
def edit_invoice(id):
    print(current_user)
    invoice = Invoice.query.filter(Invoice.id == id).first()
    form = NewInvoice()
    if form.validate_on_submit():
        session['form'] = form.data
        return redirect(url_for('home_blueprint.update_invoice', id = invoice.id))
    if request.method == 'GET':
        # form.id.data  = invoice.id
        form.prefijo.data = invoice.prefijo
        form.nfactura.data = invoice.nfactura
        form.client_id.data  = invoice.client_id
        form.user_id.data  = invoice.user_id
        form.fecha_factura.data  = invoice.fecha_factura
        form.fecha_vencimiento.data  = invoice.fecha_vencimiento
        form.fecha_proximo_pago.data  = invoice.fecha_proximo_pago
        form.concept.data  = invoice.concept
        form.observaciones.data  = invoice.observaciones
        form.status_id.data  = invoice.status_id
        form.valor.data  = invoice.valor

    return render_template('home/form_edit_invoice.html', segment='index', form=form, id = invoice.id)

@blueprint.route('/update_invoice/<id>')
@login_required
def update_invoice(id):
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
    invoice = Invoice.query.filter(Invoice.id == id).first()
    invoice.prefijo = session["form"]["prefijo"]
    invoice.client_id = session["form"]["client_id"]
    invoice.user_id = session["form"]["user_id"]
    invoice.fecha_factura = session["form"]["fecha_factura"]
    invoice.fecha_vencimiento = session["form"]["fecha_vencimiento"]
    invoice.fecha_proximo_pago = session["form"]["fecha_proximo_pago"]
    invoice.concept = session["form"]["concept"]
    invoice.observaciones = session["form"]["observaciones"]
    invoice.status_id = session["form"]["status_id"]
    invoice.valor = locale.atof(session["form"]["valor"].strip("$"))
    Invoice.update(invoice)
    db.session.commit()
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/store_invoice')
@login_required
def store_invoice():
    invoice = session['form']
    store = Invoice.add_new(invoice)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/clients')
@login_required
def clients():
    clients = Client.query.all()
    return render_template('home/clients.html', segment='index', clients=clients)

@blueprint.route('/contacts')
@login_required
def contacts():
    contacts = Contact.query.all()
    return render_template('home/contacts.html', segment='index', contacts=contacts)


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
