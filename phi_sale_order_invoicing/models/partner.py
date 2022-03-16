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

    invoicing_mode = fields.Selection([
        ("standard", "One invoice per customer"),
        ("nogroup", "One invoice per Order"),
        ("reference", "One invoice per customer reference"),
        ("shipment", "One invoice per shipment")
        ],
        default="standard")