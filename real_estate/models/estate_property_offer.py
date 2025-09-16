from odoo import fields, models

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