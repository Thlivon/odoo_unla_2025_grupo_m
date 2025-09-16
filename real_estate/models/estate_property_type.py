from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Tipo de propiedad"

    name = fields.Char(string="Tipo", required=True)