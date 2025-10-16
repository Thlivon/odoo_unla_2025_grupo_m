from odoo import fields, models

#2.24) Nuevo modelo que hereda de “res.users”
class ResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        comodel_name='estate.property',
        inverse_name='salesman_id',
        string="Propiedades"
    )