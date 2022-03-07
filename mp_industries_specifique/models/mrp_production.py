# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    customer_id = fields.Many2one('res.partner', "Client", compute='_compute_sale_order_info')
    commitment_date = fields.Datetime("Date Livraison", compute='_compute_sale_order_info')
    product_text = fields.Text("article description", compute='_compute_sale_product_text')

    def _compute_sale_order_info(self):
        for order in self:
            if order.sale_order_count:
                sale_order = order.get_sale_order()
                order.customer_id = sale_order.partner_id
                order.commitment_date = sale_order.commitment_date
            else:
                order.customer_id = False
                order.commitment_date = False

    def _compute_sale_product_text(self):
        for order in self:
            order.product_text = False
            if order.sale_order_count:
                sale_order = order.get_sale_order()
                if sale_order:
                    sale_order_line = sale_order.order_line.filtered(lambda l: l.product_id == order.product_id)
                    if sale_order_line and sale_order_line.name != sale_order_line.product_id.display_name:
                        order.product_text = sale_order_line.name

    def get_sale_order(self):
        sale_order = self.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id[0]
        return sale_order


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    duration_hours = fields.Float('Duration in jour', compute='_compute_duration_hour')

    def _compute_duration_hour(self):
        for workorder in self:
            if workorder.production_id.state != 'done':
                workorder.duration_hours = round(workorder.duration_expected / 60 , 2)
            else:
                workorder.duration_hours = round(workorder.duration / 60 , 2)
