# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            price = price * (1 - (order_line.discount2 or 0.0) / 100.0)
            order = order_line.order_id
            return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                         product=order_line.product_id, partner=order.partner_shipping_id)

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                      order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('price_unit', 'discount', 'discount2')
    def _compute_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
            line.price_reduce = line.price_reduce * (1.0 - line.discount2 / 100.0)

    @api.depends('product_uom_qty', 'discount', 'discount2', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price1 = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price2 = price1 * (1 - (line.discount2 or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price2, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    discount = fields.Float(string='Disc-I (%)', digits=dp.get_precision('Discount'), default=0.0)
    discount2 = fields.Float(string='Disc-II (%)', digits=dp.get_precision('Discount'), default=0.0)

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res['discount2'] = self.discount2
        return res
