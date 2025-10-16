from odoo import fields, models, api, Command
#Importo relativedelta para trabajar con fechas y horas
from dateutil.relativedelta import relativedelta
#Importo UserError para las excepciones
from odoo.exceptions import UserError
#Importo random para generar ofertas automáticas
import random 

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
    
    #2.19) Nuevo campo computado offer_partner_ids
    offer_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string="Ofertantes",
        compute='_compute_offer_partner_ids',
        store=True
    )
    @api.depends('offer_ids.partner_id')
    def _compute_offer_partner_ids(self):
        for record in self:
            record.offer_partner_ids = record.offer_ids.mapped('partner_id')
    
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

    #2.20) Acción para generar oferta automática sobre una propiedad
    def action_generate_automatic_offer(self):
        offer_obj = self.env['estate.property.offer']
        for record in self:
            if record.state in ['sold', 'canceled']:
                raise UserError("No se pueden generar ofertas para propiedades vendidas o canceladas.")

            # Obtengo todos los partners disponibles
            all_partners = self.env['res.partner'].search([])
            if not all_partners:
                raise UserError("No hay partners disponibles para asignar la oferta automática.")

            # Obtengo los partners que hicieron ofertas
            existing_partner_ids = record.offer_partner_ids.ids
            # Filtro los partners que no hicieron ofertas
            available_partners = all_partners.filtered(lambda p: p.id not in existing_partner_ids)
            
            if not available_partners:
                raise UserError("Todos los partners ya han realizado una oferta sobre esta propiedad.")

            # Selecciono un partner aleatorio de los disponibles
            automatic_partner = random.choice(available_partners)
            
            # Genero un precio aleatorio entre -30% y +30% del precio esperado                
            automatic_offer_price = record.expected_price * (1 + random.uniform(-0.30, 0.30))

            offer_obj.create({
                'price': automatic_offer_price,
                'partner_id': automatic_partner.id,
                'property_id': record.id,
            })
        return True
    
    #2.21) Acciones de botones "Sacar etiquetas", "Cargar todas las etiquetas" y "A estrenar"
    def action_remove_all_tags(self):
        for record in self:
            # Comando para eliminar todas las etiquetas #record.tag_ids = [(6, 0, [])]
            record.write({
                'tag_ids': [Command.unlink(tag_id) for tag_id in record.tag_ids.ids]
            })
        return True

    def action_add_all_tags(self):
        for record in self:
            all_tags = self.env['estate.property.tag'].search([])
            if not all_tags:
                raise UserError("No hay etiquetas disponibles para agregar.")
            # Comando para asignar todas las etiquetas #[(6, 0, [ids])]
            record.write({
                'tag_ids': [Command.set(all_tags.ids)]
            })
        return True

    def action_set_tag_as_new(self):
        return self.func_link_or_create_tag("a estrenar")

    # Método reutilizable para vincular o crear una etiqueta
    def func_link_or_create_tag(self, tag_name):
        # Validado que el nombre de la etiqueta no esté vacío
        if not tag_name:
            raise UserError("El nombre de la etiqueta no puede estar vacío.")
        # Traigo el modelo de etiquetas    
        TagModel = self.env['estate.property.tag']
        # Busco si ya existe la etiqueta
        existing_tag = TagModel.search([('name', '=', tag_name)], limit=1)
        # Si existe la etiqueta la asigno, si no la creo
        if existing_tag:
            tag_to_link = existing_tag
        else:
            tag_to_link = TagModel.create({'name': tag_name})
        # Comando para asignar la etiqueta #[(4, id)]
        tag_command = Command.link(tag_to_link.id)
        self.write({
            'tag_ids': [tag_command]
        })
        return True

    #2.22) Método _unlink_if_new_or_cancelled con @api.ondelete() para solo permitir borrar propiedades en estado 'new' o 'canceled'
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError("Solo se pueden eliminar propiedades en estado 'Nuevo' o 'Cancelado'.")

    