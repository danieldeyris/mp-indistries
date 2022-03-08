# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_comment = fields.Text("Comment")

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.order_comment:
            invoice_vals.update({
                'move_comment': self.order_comment,
            })
        return invoice_vals

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            rec.picking_ids.write({'picking_comment': rec.order_comment})
        return res
