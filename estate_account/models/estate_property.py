from odoo import models
from odoo.exceptions import UserError

# 2.27) Heredo el modelo de estate.property y redefino el método action_property_sold

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_property_sold(self):
        # Ejecuto la acción original
        result = super().action_property_sold()

        for record in self:
            # Verifico que tenga comprador
            if not record.buyer_id:
                raise UserError("No se puede crear la factura sin un comprador asignado.")
            
            # Creo las líneas de la factura de forma simplificada
            invoice_line_vals = [
                # Primera línea: Propiedad vendida
                (0, 0, {
                    'name': record.name,
                    'quantity': 1,
                    'price_unit': record.selling_price,
                }),
                # Segunda línea: Gastos administrativos
                (0, 0, {
                    'name': 'Gastos administrativos',
                    'quantity': 1,
                    'price_unit': 100,
                }),
            ]

            # Creo la factura
            invoice_vals = {
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_line_vals,
            }

            # Creo el registro de la factura
            self.env['account.move'].create(invoice_vals)

        return result