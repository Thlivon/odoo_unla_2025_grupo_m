from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Tipo de propiedad"
    #2.17) _sql_contraints para tipo de propiedad único
    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', 'El nombre del tipo de propiedad debe ser único')
    ]

    name = fields.Char(string="Tipo", required=True)