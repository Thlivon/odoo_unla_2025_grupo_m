from odoo import fields, models
#Importo relativedelta para trabajar con fechas y horas
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Modelo para propiedades inmobiliarias"
    
    name = fields.Char(string="Título", required=True)
    description = fields.Text(string="Descripción")
    postcode = fields.Char(string="Código Postal")
    date_availability = fields.Date(
        string="Fecha disponibilidad"
        #19) copy = False
        ,copy=False 
        #20) Por defecto date_availability sera la fecha de hoy +3 meses
        ,default=lambda self: fields.Date.today() + relativedelta(months=3)
    )
    expected_price = fields.Float(string="Precio esperado")
    selling_price = fields.Float(
        string="Precio de venta"
        #19) copy = False
        ,copy=False
    )
    bedrooms = fields.Integer(string="Habitaciones", default=2)
    living_area = fields.Integer(string="Superficie cubierta")
    facades = fields.Integer(string="Fachadas")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Jardín")
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'Norte'),
            ('south', 'Sur'),
            ('east', 'Este'),
            ('west', 'Oeste'),
        ]
        ,string="Orientación del jardín"
        ,default='north'
    )
    garden_area = fields.Integer(string="Superficie jardín")
    #21) Nuevo campo de state
    state = fields.Selection(
        selection=[
            ('new', 'Nuevo'),
            ('offer_received', 'Oferta recibida'),
            ('offer_accepted', 'Oferta aceptada'),
            ('sold', 'Vendido'),
            ('canceled', 'Cancelado'),
        ]
        ,string="Estado"
        ,required=True
        ,copy=False
        ,default='new'
    )
    #29) Nuevos campos property_type_id, buyer_id y salesman_id
    property_type_id = fields.Many2one(
        comodel_name='estate.property.type'
        ,string="Tipo Propiedad"
        ,required=True
    )
    buyer_id = fields.Many2one(
        comodel_name='res.partner'
        ,string="Comprador"
    )
    salesman_id = fields.Many2one(
        comodel_name='res.users'
        ,string="Vendedor"
        ,copy=False
        ,default=lambda self: self.env.user
    )