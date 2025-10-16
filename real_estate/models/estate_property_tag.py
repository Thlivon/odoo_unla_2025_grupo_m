from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.tag"
    _description = "Etiqueta de propiedad"
    #2.17) _sql_contraints para etiqueta única
    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)', 'El nombre de la etiqueta debe ser único')
    ]

    name = fields.Char(string="Etiqueta", required=True)