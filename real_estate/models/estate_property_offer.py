from odoo import fields, models, api
#Importo relativedelta para trabajar con fechas y horas
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class EstatePropertyType(models.Model):
    #37) Nuevo modelo estate.property.offer
    _name = "estate.property.offer"
    _description = "Oferta sobre propiedad"

    price = fields.Float(
        string="Precio"
        ,required=True
    )
    status = fields.Selection(
        string="Estado"
        ,selection=[
            ("accepted","Aceptada")
            ,("refused","Rechazada")
        ]
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner'
        ,string="Ofertante"
        ,required=True
    )
    property_id = fields.Many2one(
        comodel_name='estate.property'
        ,string="Propiedad"
        ,required=True
    )
    #2.11) Agrego el campo tipo de propiedad como campo relacionado
    property_type_id = fields.Many2one(
        comodel_name = "estate.property.type"
        ,related="property_id.property_type_id"
        ,string="Tipo de propiedad"
        ,store=True
    )
    #2.9) Se agrega campos validity y date_deadline 
    validity = fields.Integer(
        string="Validez (días)"
        ,default=7
    )
    date_deadline = fields.Date(
        string="Fecha límite"
        ,compute="_compute_date_deadline"
        ,inverse="_inverse_date_deadline"
    )
    #2.10) Autocalcular date_deadline permitiendo carga del usuario
    @api.depends("validity","date_deadline")
    def _compute_date_deadline(self):
        for record in self:
            start_datetime = record.create_date or fields.Datetime.now()
            record.date_deadline = start_datetime.date()  + relativedelta(days=record.validity)
    def _inverse_date_deadline(self):
        for record in self:
            start_datetime = record.create_date or fields.Datetime.now()
            start_date = start_datetime.date()
            record.validity = (record.date_deadline - start_date).days
    #2.16) Acción de botón de aceptar oferta
    def action_offer_accept(self):
        for offer in self:
            # Validaciones
            if not offer.property_id:
                raise UserError("La oferta no está ligada a una propiedad.")
            prop = offer.property_id
            if prop.state == 'sold':
                raise UserError("No se puede aceptar una oferta sobre una propiedad ya vendida.")
            if prop.state == 'canceled':
                raise UserError("No se puede aceptar una oferta sobre una propiedad cancelada.")

            # Actualizar la oferta actual como aceptada
            offer.status = 'accepted'

            # Actualizar la propiedad: comprador, precio de venta y estado
            prop.write({
                'buyer_id': offer.partner_id.id,
                'selling_price': offer.price,
                'state': 'offer_accepted',
            })

            # Rechazar el resto de ofertas sobre la misma propiedad
            other_offers = prop.offer_ids.filtered(lambda o: o.id != offer.id)
            if other_offers:
                other_offers.write({'status': 'refused'})

        return True            
    
    
    


    