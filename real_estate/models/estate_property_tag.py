from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.tag"
    _description = "Etiqueta de propiedad"

    name = fields.Char(string="Etiqueta", required=True)