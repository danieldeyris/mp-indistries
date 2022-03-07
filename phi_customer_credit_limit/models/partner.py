# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    available_credit = fields.Monetary("Crédit disponible", compute="_compute_available_credit")
    to_invoice_amount = fields.Monetary("A facturer", compute="_compute_available_credit")
    draft_invoice_lines_amount = fields.Monetary("Factures à valider", compute="_compute_available_credit")
    check_credit = fields.Boolean('Check Credit')
    credit_limit_on_hold  = fields.Boolean('Credit limit on hold')
    credit_limit = fields.Monetary('Credit Limit')

    def _compute_available_credit(self):
        for partner_id in self:
            if not partner_id.check_credit:
                partner_id.draft_invoice_lines_amount = 0
                partner_id.to_invoice_amount = 0
                partner_id.available_credit = 0
            else:
                partner_ids = [partner_id.id]
                for partner in self.child_ids:
                    partner_ids.append(partner.id)

                # calcul sur les commandes non livrées
                domain = [
                    ('order_id.partner_id', 'in', partner_ids),
                    ('order_id.state', 'in', ['sale', 'credit_limit', 'done'])]
                order_lines = self.env['sale.order.line'].search(domain)

                order = []
                to_invoice_amount = 0.0
                for line in order_lines:
                    not_invoiced = line.product_uom_qty - line.qty_invoiced
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(
                        price, line.order_id.currency_id,
                        not_invoiced,
                        product=line.product_id, partner=line.order_id.partner_id)
                    if line.order_id.id not in order:
                        if line.order_id.invoice_ids:
                            for inv in line.order_id.invoice_ids:
                                if inv.state == 'draft':
                                    order.append(line.order_id.id)
                                    break
                        else:
                            order.append(line.order_id.id)

                    to_invoice_amount += taxes['total_included']

                # Factures sur les factures en brouillon
                domain = [
                    ('move_id.partner_id', 'in', partner_ids),
                    ('move_id.state', '=', 'draft'),
                    ('sale_line_ids', '!=', False)]
                draft_invoice_lines = self.env['account.move.line'].search(domain)
                for line in draft_invoice_lines:
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_ids.compute_all(
                        price, line.move_id.currency_id,
                        line.quantity,
                        product=line.product_id, partner=line.move_id.partner_id)
                    to_invoice_amount += taxes['total_included']

                # Factures sur les factures
                # We sum from all the invoices lines that are in draft and not linked
                # to a sale order
                domain = [
                    ('move_id.partner_id', 'in', partner_ids),
                    ('move_id.state', '=', 'draft'),
                    ('sale_line_ids', '=', False)]
                draft_invoice_lines = self.env['account.move.line'].search(domain)
                draft_invoice_lines_amount = 0.0
                invoice = []
                for line in draft_invoice_lines:
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_ids.compute_all(
                        price, line.move_id.currency_id,
                        line.quantity,
                        product=line.product_id, partner=line.move_id.partner_id)
                    draft_invoice_lines_amount += taxes['total_included']
                    if line.move_id.id not in invoice:
                        invoice.append(line.move_id.id)

                partner_id.draft_invoice_lines_amount = draft_invoice_lines_amount
                partner_id.to_invoice_amount = to_invoice_amount
                partner_id.available_credit = partner_id.credit_limit - partner_id.credit - to_invoice_amount - draft_invoice_lines_amount
