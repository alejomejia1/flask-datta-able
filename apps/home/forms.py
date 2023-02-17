from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets import TextArea
from apps.home.models import Invoice, Client, Status
from datetime import datetime, timedelta

class NewInvoice(FlaskForm):
    prefijo = StringField('prefijo', validators=[DataRequired()])
    nfactura = IntegerField('nfactura', validators=[DataRequired()])
    client_id = SelectField('client_id', validators=[DataRequired()], coerce=int)
    fecha_factura = DateField('fecha_factura', format='%Y-%m-%d', default=datetime.today, validators=[DataRequired()])
    fecha_vencimiento = DateField('fecha_vencimiento', validators=[DataRequired()])
    fecha_proximo_pago = DateField('fecha_proximo_pago', validators=[DataRequired()])
    concept = StringField('concept', validators=[DataRequired()])
    observaciones = StringField('observaciones', widget=TextArea(), validators=[])
    user_id = IntegerField('user_id', validators=[DataRequired()])
    status_id = SelectField('status_id', validators=[DataRequired()])
    anulada = BooleanField('anulada', validators=[])
    valor = StringField('valor', default=0, validators=[DataRequired()])
    submit = SubmitField('Enviar')
    
    def __init__(self):
        super(NewInvoice, self).__init__()
        self.client_id.choices = [(c.id, c.name) for c in Client.query.all()]
        self.status_id.choices = [(c.id, c.status) for c in Status.query.all()]
        print(self.client_id.choices)
        self.client_id.label = "Cliente"
        self.fecha_factura.data = datetime.today()
        self.fecha_vencimiento.data = datetime.today() + timedelta(days=30)
        self.fecha_proximo_pago.data = datetime.today() + timedelta(days=30)
        self.anulada.data = False

class NewClient(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    user_id = IntegerField('user_id', validators=[DataRequired()])
    reference = StringField('reference', validators=[DataRequired()])
    nit = StringField('nit', validators=[DataRequired()])
    phone = StringField('phone', validators=[])
    email = StringField('email', validators=[])
    address = StringField('address',validators=[])
    submit = SubmitField('Enviar')
    
    def __init__(self):
        super(NewClient, self).__init__()
        self.user_id.data = current_user.id

class NewContact(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    user_id = IntegerField('user_id', validators=[DataRequired()])
    client_id = SelectField('client_id', validators=[DataRequired()], coerce=int)
    cellphone = StringField('cellphone', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    address = StringField('address',validators=[])
    submit = SubmitField('Enviar')
    
    def __init__(self):
        super(NewContact, self).__init__()
        self.user_id.data = current_user.id
        self.client_id.choices = [(c.id, c.name) for c in Client.query.all()]
        self.client_id.label = "Cliente"
    
    
    
    