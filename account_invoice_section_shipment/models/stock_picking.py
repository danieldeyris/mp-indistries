# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_invoice_section_name(self):
        self.ensure_one()
        address = "%s %s %s" % (self.partner_id.street, self.partner_id.zip, self.partner_id.city)
        return "BL : %s - %s - %s" % (self.name, self.date_done.strftime('%d/%m/%Y'), address)
