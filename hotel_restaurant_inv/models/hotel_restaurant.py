# See LICENSE file for full copyright and licensing details.

import time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class HotelReservationOrder(models.Model):
    _inherit = "hotel.reservation.order"
    _description = "Reservation Order"

    invoice_id = fields.Many2one('account.invoice', ondelete="restrict", string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Partner')

    @api.multi
    def create_invoice(self):
        Invoice = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']
        InvoiceLine = self.env['account.invoice.line']
        prop = ir_property_obj.get('property_account_income_categ_id', 'product.category')
        account_id = prop and prop.id or False
        
        if self.is_folio :
            invoice = Invoice.create({
                'account_id': self.folio_id.partner_id.property_account_receivable_id.id,
                'partner_id': self.folio_id.partner_id.id,
                # 'patient_id': self.patient_id.id,
                'type': 'out_invoice',
                'name': '-',
                'origin': self.order_number,
                'currency_id': self.env.user.company_id.currency_id.id,
                'create_stock_moves': True,
                'pharmacy_invoice': True,
                # 'physician_id': self.physician_id and self.physician_id.id or False,
            })
            for line in self.order_list:
                account_id = False
                if line.name.id:
                    account_id = line.name.property_account_income_id.id
                if not account_id:
                    prop = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                    account_id = prop and prop.id or False

                InvoiceLine.create({
                    'name': line.name.name,
                    'price_unit': line.item_rate,
                    'account_id': account_id,
                    'quantity': line.item_qty,
                    'discount': 0.0,
                    'uom_id': line.name.uom_id.id,
                    'product_id': line.name.id,
                    'account_analytic_id': False,
                    'invoice_id': invoice.id,
                })
            self.invoice_id = invoice.id
        else :
            invoice = Invoice.create({
                'account_id': self.reservationno.cname.property_account_receivable_id.id,
                'partner_id': self.reservationno.cname.id,
                # 'patient_id': self.patient_id.id,
                'type': 'out_invoice',
                'name': '-',
                'origin': self.order_number,
                'currency_id': self.env.user.company_id.currency_id.id,
                'create_stock_moves': True,
                'pharmacy_invoice': True,
                # 'physician_id': self.physician_id and self.physician_id.id or False,
            })
            for line in self.order_list:
                account_id = False
                if line.name.id:
                    account_id = line.name.property_account_income_id.id
                if not account_id:
                    prop = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                    account_id = prop and prop.id or False

                InvoiceLine.create({
                    'name': line.name.name,
                    'price_unit': line.item_rate,
                    'account_id': account_id,
                    'quantity': line.item_qty,
                    'discount': 0.0,
                    'uom_id': line.name.uom_id.id,
                    'product_id': line.name.id,
                    'account_analytic_id': False,
                    'invoice_id': invoice.id,
                })
            self.invoice_id = invoice.id


    @api.multi
    def view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
