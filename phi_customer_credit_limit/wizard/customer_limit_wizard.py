# -*- coding: utf-8 -*-


from odoo import api, fields, models


class CustomerLimitWizard(models.TransientModel):
    _name = "customer.limit.wizard"
    _description = 'Customer Credit Limit Wizard'

    credit_limit_force_reason = fields.Char("Credit limit force reason", required="1")

    def confirm_order(self):
        order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        order_id.credit_limit_force_reason = self.credit_limit_force_reason
        order_id.confirm_force_credit()
