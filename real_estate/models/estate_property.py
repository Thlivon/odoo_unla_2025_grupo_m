from odoo import fields, models, api
#Importo relativedelta para trabajar con fechas y horas
from dateutil.relativedelta import relativedelta
#Importo UserError para las excepciones
from odoo.exceptions import UserError

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Propiedad"
    
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
    #29) Nuevos campos Many2one property_type_id, buyer_id y salesman_id
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
    #35) Nuevo campo Many2many
    tag_ids = fields.Many2many(
        comodel_name='estate.property.tag'
        ,string="Etiquetas"
    )
    #39) Nuevo campo One2many
    offer_ids = fields.One2many(
        comodel_name = "estate.property.offer"
        ,inverse_name = "property_id"
        ,string = "Ofertas"
    )
    #2.1) Nuevo campo computado total_area
    total_area = fields.Float(
        string="Superficie total"
        ,compute="_compute_total_area"
        ,store = True
    )
    #2.5) Decorador @api.depends para autocalcular el computado en tiempo real
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    #2.7) Nuevo campo computado best_offer
    best_offer = fields.Float(
        string="Mejor oferta"
        ,compute="_compute_best_offer"
    )
    @api.depends('offer_ids')
    def _compute_best_offer(self):
        for record in self:
            offers = record.offer_ids.mapped('price')
            record.best_offer = max(offers) if offers else 0
    #2.13) Onchange al presionar el campo garden
    @api.onchange('garden')
    def _onchange_garden(self):
        for record in self:
            if (record.garden):
                record.garden_area = 10
            else:
                record.garden_area = 0
    #2.14) Onchange cuando el precio esperado > 10000                
    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        for record in self:
            if record.expected_price and record.expected_price < 10000:
                return {
                    'warning': {
                        'title': "Precio Esperado Menor a 10000",
                        'message': "El precio esperado ingresado es menor a 10000. Si no es un error, ignore esta advertencia.",
                    }
                }
    #2.15) Acciones de los botones de cancelar y vender            
    def action_property_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Una propiedad ya vendida no puede ser cancelada.")
            record.state = 'canceled'
        return True
    def action_property_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("Una propiedad cancelada no puede ser marcada como vendida.")
            record.state = 'sold'
        return True